#!/usr/bin/env python3
"""Run blind cross-provider quality review for completed Pi benchmark outputs."""

import argparse
import hashlib
import json
import re
import statistics
import subprocess
import time
from collections import Counter
from pathlib import Path

import run_pi_bench


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PRE_RELEASE_ARCHIVE = ROOT / "archive" / "pre-release" / "evals"
DEFAULT_CONFIG_PATH = PRE_RELEASE_ARCHIVE / "config" / "initial-quality-judge.json"
DEFAULT_MATRIX_PATH = PRE_RELEASE_ARCHIVE / "config" / "initial-skill-matrix.json"
DEFAULT_BENCHMARK_RESULTS_DIR = run_pi_bench.DEFAULT_RESULTS_DIR
DEFAULT_JUDGE_RESULTS_DIR = HERE / "results" / "current-judge"
JUDGE_RUNNER_VERSION = "2"
REQUIRED_DIMENSIONS = (
    "factual_semantic_fidelity",
    "task_completion",
    "uncertainty_obligation",
    "technical_terminology",
    "safety_actionability",
    "readability_concision",
)


def collect_judge_provenance(
    config_path,
    matrix_path,
    source_results,
    source_raw_directory,
    run_command=None,
):
    kwargs = {} if run_command is None else {"run_command": run_command}
    current = run_pi_bench.collect_provenance(matrix_path, **kwargs)
    source = source_results["provenance"]
    return {
        "judge_runner_version": JUDGE_RUNNER_VERSION,
        "judge_config_sha256": hashlib.sha256(
            Path(config_path).read_bytes()
        ).hexdigest(),
        "source_matrix_sha256": source["matrix_sha256"],
        "source_raw_sha256": run_pi_bench.tree_sha256(source_raw_directory),
        "source_package_commit": source["package_commit"],
        "source_skill_sha256": source["skill_sha256"],
        "package_commit": current["package_commit"],
        "package_dirty": current["package_dirty"],
        "skill_sha256": current["skill_sha256"],
        "pi_version": current["pi_version"],
    }


def source_compatibility_error(source_provenance, judge_provenance):
    if source_provenance.get("package_dirty") is not False:
        return "benchmark evidence must come from a clean git working tree"
    if judge_provenance.get("package_dirty") is not False:
        return "judge generation requires a clean git working tree"
    if judge_provenance.get("skill_sha256") != source_provenance.get(
        "skill_sha256"
    ):
        return "judge generation requires the benchmark skill snapshot"
    return None


def validate_judge_config(config):
    if not isinstance(config, dict) or config.get("schema_version") != 1:
        raise ValueError("judge config schema_version must be 1")
    if not isinstance(config.get("version"), int) or config["version"] < 1:
        raise ValueError("judge config version must be a positive integer")
    amendments = config.get("amendments")
    if (
        not isinstance(amendments, list)
        or [item.get("version") for item in amendments if isinstance(item, dict)]
        != list(range(1, config["version"] + 1))
        or any(
            not isinstance(item.get("reason"), str) or not item["reason"].strip()
            for item in amendments
        )
    ):
        raise ValueError("judge amendment history is invalid")

    dimensions = config.get("dimensions")
    if (
        not isinstance(dimensions, list)
        or tuple(item.get("id") for item in dimensions if isinstance(item, dict))
        != REQUIRED_DIMENSIONS
        or any(
            not isinstance(item.get("label"), str)
            or not item["label"].strip()
            or not isinstance(item.get("instruction"), str)
            or not item["instruction"].strip()
            for item in dimensions
        )
    ):
        raise ValueError("judge rubric dimensions are incomplete or invalid")

    comparisons = config.get("comparisons")
    if not isinstance(comparisons, list) or not comparisons:
        raise ValueError("judge comparisons must be nonempty")
    comparison_ids = []
    for comparison in comparisons:
        if not isinstance(comparison, dict) or not all(
            isinstance(comparison.get(key), str) and comparison[key]
            for key in ("id", "left_condition", "right_condition", "role")
        ):
            raise ValueError("judge comparison fields are invalid")
        if comparison["left_condition"] == comparison["right_condition"]:
            raise ValueError("judge comparison conditions must differ")
        comparison_ids.append(comparison["id"])
    if len(comparison_ids) != len(set(comparison_ids)):
        raise ValueError("judge comparison IDs must be unique")

    judges = config.get("judges_by_source_provider")
    if not isinstance(judges, dict) or not judges:
        raise ValueError("judge provider mapping must be nonempty")
    for source_provider, judge in judges.items():
        if (
            not isinstance(source_provider, str)
            or not source_provider
            or not isinstance(judge, dict)
            or not all(
                isinstance(judge.get(key), str) and judge[key]
                for key in ("provider", "model", "thinking")
            )
        ):
            raise ValueError("judge provider mapping is invalid")
        if judge["provider"] == source_provider:
            raise ValueError("judge mapping must use a cross-provider model")
        if judge["thinking"] not in run_pi_bench.THINKING_LEVELS:
            raise ValueError("judge thinking level is unsupported")

    if (
        not isinstance(config.get("source_repetitions_minimum"), int)
        or config["source_repetitions_minimum"] < 3
    ):
        raise ValueError("judge source repetition minimum must be at least 3")
    if not isinstance(config.get("retry_limit"), int) or config["retry_limit"] < 1:
        raise ValueError("judge retry_limit must be at least 1")
    if (
        not isinstance(config.get("timeout_seconds"), (int, float))
        or isinstance(config["timeout_seconds"], bool)
        or config["timeout_seconds"] <= 0
    ):
        raise ValueError("judge timeout_seconds must be positive")
    if (
        not isinstance(config.get("inter_call_delay_seconds"), (int, float))
        or isinstance(config["inter_call_delay_seconds"], bool)
        or config["inter_call_delay_seconds"] < 0
    ):
        raise ValueError("judge inter_call_delay_seconds must be nonnegative")
    if not isinstance(config.get("system_prompt"), str) or not config[
        "system_prompt"
    ].strip():
        raise ValueError("judge system_prompt must be nonempty")

    score_range = config.get("score_range")
    if (
        not isinstance(score_range, dict)
        or set(score_range) != {"minimum", "maximum"}
        or not all(isinstance(score_range[key], int) for key in score_range)
        or score_range["minimum"] >= score_range["maximum"]
    ):
        raise ValueError("judge score range is invalid")
    categories = config.get("blocking_issue_categories")
    if (
        not isinstance(categories, list)
        or not categories
        or not all(isinstance(item, str) and item for item in categories)
        or len(categories) != len(set(categories))
    ):
        raise ValueError("judge blocking issue categories are invalid")
    limitations = config.get("limitations")
    if (
        not isinstance(limitations, list)
        or not limitations
        or not all(isinstance(item, str) and item.strip() for item in limitations)
    ):
        raise ValueError("judge limitations must be explicit")


def load_judge_config(path=DEFAULT_CONFIG_PATH):
    config = run_pi_bench.strict_json_loads(Path(path).read_text(encoding="utf-8"))
    validate_judge_config(config)
    return config


def validate_judge_matrix(config, matrix):
    validate_judge_config(config)
    run_pi_bench.validate_matrix(matrix)
    if matrix.get("matrix_id") != config.get("source_matrix_id"):
        raise ValueError("judge source matrix ID does not match")
    if matrix["repetitions"] < config["source_repetitions_minimum"]:
        raise ValueError("source matrix has insufficient repetitions for judging")
    conditions = set(matrix["conditions"])
    if any(
        comparison["left_condition"] not in conditions
        or comparison["right_condition"] not in conditions
        for comparison in config["comparisons"]
    ):
        raise ValueError("judge comparison references an unknown source condition")
    source_providers = {model["provider"] for model in matrix["models"]}
    missing = source_providers - set(config["judges_by_source_provider"])
    if missing:
        raise ValueError(
            "judge mapping is missing source provider: " + ", ".join(sorted(missing))
        )
    for source_provider in source_providers:
        if (
            config["judges_by_source_provider"][source_provider]["provider"]
            == source_provider
        ):
            raise ValueError("judge mapping must use a cross-provider model")


def validate_source_results(results, matrix, matrix_path=run_pi_bench.DEFAULT_MATRIX_PATH):
    if not isinstance(results, dict) or results.get("schema_version") != 1:
        raise ValueError("source benchmark results schema is invalid")
    source_matrix = results.get("matrix")
    if (
        not isinstance(source_matrix, dict)
        or source_matrix.get("id") != matrix["matrix_id"]
        or source_matrix.get("version") != matrix["version"]
    ):
        raise ValueError("source benchmark matrix identity does not match")
    completeness = results.get("completeness")
    if not isinstance(completeness, dict) or completeness.get("complete") is not True:
        raise ValueError("source benchmark must be complete before judging")
    integrity = results.get("condition_integrity")
    if not isinstance(integrity, dict) or integrity.get("accepted") is not True:
        raise ValueError("source benchmark condition integrity is not accepted")
    semantic = results.get("semantic_acceptance")
    if not isinstance(semantic, dict) or not isinstance(semantic.get("accepted"), bool):
        raise ValueError("source benchmark semantic acceptance is invalid")
    provenance = results.get("provenance")
    expected_matrix_hash = hashlib.sha256(Path(matrix_path).read_bytes()).hexdigest()
    if (
        not isinstance(provenance, dict)
        or provenance.get("matrix_sha256") != expected_matrix_hash
    ):
        raise ValueError("source benchmark matrix provenance does not match")


def validate_source_evidence(
    source_results,
    matrix,
    scenarios,
    raw_directory,
    skill_text,
    aggregate_function=run_pi_bench.aggregate_results,
):
    recomputed = aggregate_function(
        matrix,
        scenarios,
        source_results["provenance"],
        Path(raw_directory),
        skill_text=skill_text,
    )
    authority_fields = (
        ("completeness", "completeness"),
        ("condition_integrity", "condition integrity"),
        ("semantic_acceptance", "semantic acceptance"),
    )
    for key, label in authority_fields:
        if recomputed.get(key) != source_results.get(key):
            raise ValueError(
                f"source benchmark {label} does not match raw evidence"
            )
    return recomputed


def source_cell(judge_cell, condition):
    source = judge_cell["source_model"]
    return {
        "provider": source["provider"],
        "model": source["model"],
        "thinking": source["thinking"],
        "condition": condition,
        "scenario_id": judge_cell["scenario_id"],
        "repetition": judge_cell["source_repetition"],
    }


def load_source_pair(
    raw_directory,
    judge_cell,
    matrix,
    scenario,
    skill_text,
    provenance,
):
    candidates = {}
    evaluations = {}
    for condition in (
        judge_cell["left_condition"],
        judge_cell["right_condition"],
    ):
        cell = source_cell(judge_cell, condition)
        path = Path(raw_directory) / run_pi_bench.raw_result_name(cell)
        if not path.exists():
            raise RuntimeError(f"missing source benchmark result: {path}")
        try:
            document = run_pi_bench.strict_json_loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError) as error:
            raise RuntimeError(f"invalid source benchmark result: {path}: {error}") from error
        if error := run_pi_bench.raw_document_error(document):
            raise RuntimeError(f"invalid source benchmark result: {path}: {error}")
        if document.get("cell") != cell or document.get("provenance") != provenance:
            raise RuntimeError(f"stale source benchmark result: {path}")
        if error := run_pi_bench.raw_evidence_error(
            document,
            cell,
            matrix,
            scenario,
            skill_text,
        ):
            raise RuntimeError(f"invalid source benchmark result: {path}: {error}")
        if document["status"] != "success":
            raise RuntimeError(f"source benchmark result is not successful: {path}")
        if document["condition_integrity"]["passed"] is not True:
            raise RuntimeError(f"source benchmark condition integrity failed: {path}")
        candidates[condition] = document["response"]["text"]
        evaluations[condition] = document["evaluation"]
    return candidates, evaluations


def iter_judge_cells(matrix, config):
    validate_judge_matrix(config, matrix)
    for source_model in matrix["models"]:
        judge = config["judges_by_source_provider"][source_model["provider"]]
        for comparison in config["comparisons"]:
            for scenario_id in matrix["scenario_ids"]:
                for repetition in range(1, matrix["repetitions"] + 1):
                    yield {
                        "source_model": dict(source_model),
                        "comparison_id": comparison["id"],
                        "comparison_role": comparison["role"],
                        "left_condition": comparison["left_condition"],
                        "right_condition": comparison["right_condition"],
                        "scenario_id": scenario_id,
                        "source_repetition": repetition,
                        "judge": dict(judge),
                    }


def judge_cell_id(cell):
    source = cell["source_model"]
    judge = cell["judge"]
    values = (
        source["provider"],
        source["model"],
        source["thinking"],
        cell["comparison_id"],
        cell["scenario_id"],
        str(cell["source_repetition"]),
        judge["provider"],
        judge["model"],
        judge["thinking"],
    )
    return "__".join(values)


def blind_assignment(cell):
    left = cell["left_condition"]
    right = cell["right_condition"]
    repetition = cell["source_repetition"]
    if repetition == 1:
        left_is_a = True
    elif repetition == 2:
        left_is_a = False
    else:
        digest = hashlib.sha256(judge_cell_id(cell).encode("utf-8")).digest()
        left_is_a = digest[0] % 2 == 0
    if left_is_a:
        return {"A": left, "B": right}
    return {"A": right, "B": left}


def build_judge_prompt(config, scenario, candidates, assignment):
    if set(assignment) != {"A", "B"} or set(assignment.values()) != set(
        candidates
    ):
        raise ValueError("blind assignment does not match candidates")
    rubric = "\n".join(
        f"- {item['id']} ({item['label']}): {item['instruction']}"
        for item in config["dimensions"]
    )
    dimension_ids = ", ".join(item["id"] for item in config["dimensions"])
    issue_categories = ", ".join(config["blocking_issue_categories"])
    minimum = config["score_range"]["minimum"]
    maximum = config["score_range"]["maximum"]
    return (
        "Evaluate two blinded candidates against one task and source.\n\n"
        f"Task\n\n{scenario['task']}\n\n"
        f"Source\n\n{scenario['source']}\n\n"
        f"Candidate A\n\n{candidates[assignment['A']]}\n\n"
        f"Candidate B\n\n{candidates[assignment['B']]}\n\n"
        "Rubric\n\n"
        f"{rubric}\n\n"
        "Score each applicable dimension from "
        f"{minimum} (unacceptable) to {maximum} (excellent). For an inapplicable "
        "dimension, set applicable to false and score to null. Evidence must cite a "
        "specific source/candidate difference. Readability cannot excuse a factual, "
        "contract, terminology, modality, or safety defect.\n\n"
        "Return one JSON object with exactly this structure:\n"
        "{\n"
        '  "schema_version": 1,\n'
        '  "candidates": {\n'
        '    "A": {"scores": {<all dimension IDs>: '
        '{"applicable": <boolean>, "score": <integer or null>, '
        '"evidence": "<concise evidence>"}}, "blocking_issues": '
        '[{"category": "<category>", "evidence": "<concise evidence>"}]},\n'
        '    "B": {"scores": {<same dimensions and fields>}, '
        '"blocking_issues": [<same issue structure>]}\n'
        "  },\n"
        '  "preference": "A | B | tie",\n'
        '  "confidence": "low | medium | high",\n'
        '  "preference_reason": "<concise comparison>"\n'
        "}\n"
        f"Dimension IDs: {dimension_ids}.\n"
        f"Blocking categories: {issue_categories}. Use blocking issues only for "
        "semantic, task, modality, terminology, or safety defects; never for style alone."
    )


def judge_output_error(verdict, config):
    root_fields = {
        "schema_version",
        "candidates",
        "preference",
        "confidence",
        "preference_reason",
    }
    if not isinstance(verdict, dict) or set(verdict) != root_fields:
        return "judge verdict fields are invalid"
    if verdict["schema_version"] != 1:
        return "judge verdict schema_version must be 1"
    if verdict["preference"] not in {"A", "B", "tie"}:
        return "judge preference is invalid"
    if verdict["confidence"] not in {"low", "medium", "high"}:
        return "judge confidence is invalid"
    if (
        not isinstance(verdict["preference_reason"], str)
        or not verdict["preference_reason"].strip()
    ):
        return "judge preference reason is invalid"
    candidates = verdict["candidates"]
    if not isinstance(candidates, dict) or set(candidates) != {"A", "B"}:
        return "judge candidate fields are invalid"

    dimension_ids = {item["id"] for item in config["dimensions"]}
    minimum = config["score_range"]["minimum"]
    maximum = config["score_range"]["maximum"]
    categories = set(config["blocking_issue_categories"])
    for label, candidate in candidates.items():
        if not isinstance(candidate, dict) or set(candidate) != {
            "scores",
            "blocking_issues",
        }:
            return f"candidate {label} fields are invalid"
        scores = candidate["scores"]
        if not isinstance(scores, dict) or set(scores) != dimension_ids:
            return f"candidate {label} dimension set is invalid"
        for dimension_id, report in scores.items():
            if not isinstance(report, dict) or set(report) != {
                "applicable",
                "score",
                "evidence",
            }:
                return f"candidate {label} {dimension_id} score fields are invalid"
            applicable = report["applicable"]
            score = report["score"]
            if not isinstance(applicable, bool):
                return f"candidate {label} {dimension_id} applicability is invalid"
            if applicable:
                if (
                    not isinstance(score, int)
                    or isinstance(score, bool)
                    or not minimum <= score <= maximum
                ):
                    return f"candidate {label} {dimension_id} score is invalid"
            elif score is not None:
                return f"candidate {label} {dimension_id} score must be null"
            if not isinstance(report["evidence"], str) or not report[
                "evidence"
            ].strip():
                return f"candidate {label} {dimension_id} evidence is invalid"
        issues = candidate["blocking_issues"]
        if not isinstance(issues, list):
            return f"candidate {label} blocking issues must be an array"
        for issue in issues:
            if not isinstance(issue, dict) or set(issue) != {"category", "evidence"}:
                return f"candidate {label} blocking issue fields are invalid"
            if issue["category"] not in categories:
                return f"candidate {label} blocking issue category is invalid"
            if not isinstance(issue["evidence"], str) or not issue[
                "evidence"
            ].strip():
                return f"candidate {label} blocking issue evidence is invalid"
    return None


def parse_judge_output(text, config):
    stripped = text.strip()
    fence = re.fullmatch(r"```(?:json)?\s*\n(.*)\n```", stripped, re.DOTALL | re.IGNORECASE)
    if fence is not None:
        stripped = fence.group(1)
    verdict = run_pi_bench.strict_json_loads(stripped)
    if error := judge_output_error(verdict, config):
        raise ValueError(error)
    return verdict


def authoritative_outcome(
    left_condition,
    right_condition,
    left_evaluation,
    right_evaluation,
    verdict,
    assignment,
):
    condition_for_label = dict(assignment)
    preference = verdict["preference"]
    judge_preference = (
        "tie" if preference == "tie" else condition_for_label[preference]
    )
    blocking_conditions = sorted(
        condition_for_label[label]
        for label in ("A", "B")
        if verdict["candidates"][label]["blocking_issues"]
    )
    left_passed = left_evaluation["semantic_gate_passed"]
    right_passed = right_evaluation["semantic_gate_passed"]

    if left_passed != right_passed:
        winner = left_condition if left_passed else right_condition
        return {
            "winner": winner,
            "basis": "deterministic-semantic-gate",
            "judge_preference": judge_preference,
            "blocking_conditions": blocking_conditions,
            "review_required": winner in blocking_conditions,
        }
    if not left_passed:
        return {
            "winner": None,
            "basis": "deterministic-both-failed",
            "judge_preference": judge_preference,
            "blocking_conditions": blocking_conditions,
            "review_required": True,
        }
    if blocking_conditions:
        return {
            "winner": None,
            "basis": "judge-blocking-issue",
            "judge_preference": judge_preference,
            "blocking_conditions": blocking_conditions,
            "review_required": True,
        }
    return {
        "winner": judge_preference,
        "basis": "judge-preference",
        "judge_preference": judge_preference,
        "blocking_conditions": [],
        "review_required": False,
    }


def build_judge_command(cell, config, prompt):
    judge = cell["judge"]
    return [
        "pi",
        "--print",
        "--mode",
        "json",
        "--provider",
        judge["provider"],
        "--model",
        judge["model"],
        "--thinking",
        judge["thinking"],
        "--system-prompt",
        config["system_prompt"],
        "--no-extensions",
        "--no-skills",
        "--no-prompt-templates",
        "--no-themes",
        "--no-context-files",
        "--no-tools",
        "--no-session",
        "--no-approve",
        "--offline",
        prompt,
    ]


def candidate_hashes(candidates):
    return {
        condition: hashlib.sha256(text.encode("utf-8")).hexdigest()
        for condition, text in sorted(candidates.items())
    }


def judge_evidence_error(
    document,
    cell,
    config,
    scenario,
    candidates,
    evaluations,
):
    assignment = blind_assignment(cell)
    if document.get("blind_assignment") != assignment:
        return "blind assignment does not match judge cell"
    if document.get("candidate_sha256") != candidate_hashes(candidates):
        return "candidate hashes do not match source benchmark outputs"
    prompt = build_judge_prompt(config, scenario, candidates, assignment)
    expected_prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    if document.get("prompt_sha256") != expected_prompt_hash:
        return "prompt hash does not match judge input"
    verdict = document.get("verdict")
    if error := judge_output_error(verdict, config):
        return error
    response = document.get("response")
    response_text = response.get("text") if isinstance(response, dict) else None
    if not isinstance(response_text, str):
        return "response verdict text is missing"
    try:
        parsed_verdict = parse_judge_output(response_text, config)
    except (ValueError, json.JSONDecodeError) as error:
        return f"response verdict is invalid: {error}"
    if parsed_verdict != verdict:
        return "stored verdict does not match response verdict"
    expected_outcome = authoritative_outcome(
        cell["left_condition"],
        cell["right_condition"],
        evaluations[cell["left_condition"]],
        evaluations[cell["right_condition"]],
        verdict,
        assignment,
    )
    if document.get("outcome") != expected_outcome:
        return "authoritative outcome does not match source semantic evidence"
    return None


def judge_response_error(response, cell, require_stop=True):
    if error := run_pi_bench.response_error(
        response, "judge response", require_stop=require_stop
    ):
        return error
    judge = cell["judge"]
    if (
        response["provider"] != judge["provider"]
        or response["model"] != judge["model"]
        or response.get("response_model") not in {None, judge["model"]}
    ):
        return "judge response identity does not match requested judge"
    routing = response["routing"]
    if routing["tool_calls"] != 0 or routing["skill_loaded"]:
        return "judge response used disallowed tools or skills"
    return None


def judge_document_error(document, config):
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        return "judge document schema is invalid"
    if document.get("status") not in {"success", "failure"}:
        return "judge document status is invalid"
    common = {
        "schema_version",
        "status",
        "cell",
        "provenance",
        "blind_assignment",
        "candidate_sha256",
        "prompt_sha256",
        "attempts",
        "updated_at",
    }
    status_fields = (
        {"last_error"}
        if document["status"] == "failure"
        else {"duration_ms", "response", "verdict", "outcome"}
    )
    if set(document) != common | status_fields:
        return "judge document fields are invalid"
    if not isinstance(document["cell"], dict) or not isinstance(
        document["provenance"], dict
    ):
        return "judge document identity is invalid"
    assignment = document["blind_assignment"]
    if (
        not isinstance(assignment, dict)
        or set(assignment) != {"A", "B"}
        or len(set(assignment.values())) != 2
    ):
        return "judge blind assignment is invalid"
    hashes = document["candidate_sha256"]
    if (
        not isinstance(hashes, dict)
        or set(hashes) != set(assignment.values())
        or not all(
            isinstance(value, str) and len(value) == 64 for value in hashes.values()
        )
        or not isinstance(document["prompt_sha256"], str)
        or len(document["prompt_sha256"]) != 64
    ):
        return "judge input hashes are invalid"
    if not isinstance(document["updated_at"], str) or not document[
        "updated_at"
    ]:
        return "judge updated_at is invalid"
    attempts = document["attempts"]
    if not isinstance(attempts, list) or not attempts:
        return "judge attempts must be nonempty"
    for index, attempt in enumerate(attempts, 1):
        if (
            not isinstance(attempt, dict)
            or attempt.get("number") != index
            or attempt.get("status") not in {"success", "failure"}
            or not isinstance(attempt.get("started_at"), str)
            or not attempt["started_at"]
            or not isinstance(attempt.get("duration_ms"), (int, float))
            or isinstance(attempt.get("duration_ms"), bool)
            or attempt["duration_ms"] < 0
        ):
            return f"judge attempt {index} is invalid"
        expected = {"number", "started_at", "status", "duration_ms"}
        if attempt["status"] == "failure":
            expected.add("error")
            if "partial_response" in attempt:
                expected.add("partial_response")
            error = attempt.get("error")
            if (
                not isinstance(error, dict)
                or set(error) != {"kind", "message"}
                or not all(isinstance(error.get(key), str) and error[key] for key in error)
            ):
                return f"judge attempt {index} error is invalid"
        if set(attempt) != expected:
            return f"judge attempt {index} fields are invalid"
        if "partial_response" in attempt:
            if error := judge_response_error(
                attempt["partial_response"], document["cell"], require_stop=False
            ):
                return f"judge attempt {index} partial response is invalid: {error}"
        if index < len(attempts) and attempt["status"] != "failure":
            return "only final judge attempt may succeed"
    if document["status"] == "failure":
        if attempts[-1]["status"] != "failure" or document["last_error"] != attempts[-1].get("error"):
            return "failed judge document does not match final attempt"
        return None
    if attempts[-1]["status"] != "success":
        return "successful judge document needs final successful attempt"
    if document["duration_ms"] != attempts[-1]["duration_ms"]:
        return "judge duration does not match final attempt"
    if error := judge_response_error(document["response"], document["cell"]):
        return error
    if error := judge_output_error(document["verdict"], config):
        return error
    outcome = document["outcome"]
    if not isinstance(outcome, dict) or set(outcome) != {
        "winner",
        "basis",
        "judge_preference",
        "blocking_conditions",
        "review_required",
    }:
        return "judge outcome is invalid"
    return None


def summarize_judgments(documents, config):
    groups = {}
    blocking_issue_counts = Counter()
    review_required = 0
    cross_provider = 0
    for document in documents:
        cell = document["cell"]
        source = cell["source_model"]
        judge = cell["judge"]
        key = (
            source["provider"],
            source["model"],
            source["thinking"],
            cell["comparison_id"],
            cell["comparison_role"],
            judge["provider"],
            judge["model"],
            judge["thinking"],
        )
        group = groups.setdefault(
            key,
            {
                "source_model": dict(source),
                "judge": dict(judge),
                "comparison_id": cell["comparison_id"],
                "comparison_role": cell["comparison_role"],
                "judgments": 0,
                "authoritative_outcomes": Counter(),
                "judge_preferences": Counter(),
                "position_preferences": Counter(),
                "review_required": 0,
                "blocking_issue_counts": Counter(),
                "dimension_values": {},
            },
        )
        group["judgments"] += 1
        if source["provider"] != judge["provider"]:
            cross_provider += 1
        outcome = document["outcome"]
        winner = outcome["winner"] if outcome["winner"] is not None else "no-winner"
        group["authoritative_outcomes"][winner] += 1
        group["judge_preferences"][outcome["judge_preference"]] += 1
        group["position_preferences"][document["verdict"]["preference"]] += 1
        if outcome["review_required"]:
            review_required += 1
            group["review_required"] += 1

        assignment = document["blind_assignment"]
        verdict = document["verdict"]
        for label, candidate in verdict["candidates"].items():
            condition = assignment[label]
            for issue in candidate["blocking_issues"]:
                category = issue["category"]
                blocking_issue_counts[category] += 1
                group["blocking_issue_counts"][category] += 1
            condition_values = group["dimension_values"].setdefault(condition, {})
            for dimension_id, report in candidate["scores"].items():
                values = condition_values.setdefault(
                    dimension_id, {"scores": [], "not_applicable": 0}
                )
                if report["applicable"]:
                    values["scores"].append(report["score"])
                else:
                    values["not_applicable"] += 1

    comparison_rows = []
    for key in sorted(groups):
        group = groups[key]
        dimensions = {}
        for condition, reports in sorted(group.pop("dimension_values").items()):
            dimensions[condition] = {}
            for dimension_id in (item["id"] for item in config["dimensions"]):
                values = reports[dimension_id]
                scores = values["scores"]
                dimensions[condition][dimension_id] = {
                    "applicable_samples": len(scores),
                    "not_applicable_samples": values["not_applicable"],
                    "mean": round(statistics.mean(scores), 6) if scores else None,
                }
        group["authoritative_outcomes"] = dict(
            sorted(group["authoritative_outcomes"].items())
        )
        group["judge_preferences"] = dict(sorted(group["judge_preferences"].items()))
        group["position_preferences"] = dict(
            sorted(group["position_preferences"].items())
        )
        group["blocking_issue_counts"] = dict(
            sorted(group["blocking_issue_counts"].items())
        )
        group["dimensions"] = dimensions
        comparison_rows.append(group)
    return {
        "judgments": len(documents),
        "cross_provider_judgments": cross_provider,
        "review_required": review_required,
        "blocking_issue_counts": dict(sorted(blocking_issue_counts.items())),
        "comparisons": comparison_rows,
    }


def judge_raw_result_name(cell):
    source = cell["source_model"]
    judge = cell["judge"]
    values = (
        source["provider"],
        source["model"],
        source["thinking"],
        cell["comparison_id"],
        cell["scenario_id"],
        f"r{cell['source_repetition']}",
        judge["provider"],
        judge["model"],
        judge["thinking"],
    )
    return "__".join(run_pi_bench.file_slug(value) for value in values) + ".json"


def aggregate_judge_results(
    matrix,
    config,
    provenance,
    raw_directory,
    source_results,
    generated_at=None,
    source_raw_directory=None,
    scenarios=None,
    skill_text=None,
):
    documents = []
    unresolved = []
    counts = Counter()
    cells = list(iter_judge_cells(matrix, config))
    for cell in cells:
        path = Path(raw_directory) / judge_raw_result_name(cell)
        if not path.exists():
            counts["missing"] += 1
            unresolved.append({"kind": "missing", "cell": cell})
            continue
        try:
            document = run_pi_bench.strict_json_loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError) as error:
            counts["invalid"] += 1
            unresolved.append(
                {"kind": "invalid", "cell": cell, "error": str(error)}
            )
            continue
        try:
            error = judge_document_error(document, config)
        except (KeyError, TypeError, ValueError) as validation_error:
            error = f"judge document validation failed: {validation_error}"
        if error:
            counts["invalid"] += 1
            unresolved.append({"kind": "invalid", "cell": cell, "error": error})
            continue
        if document["cell"] != cell or document["provenance"] != provenance:
            counts["stale"] += 1
            unresolved.append({"kind": "stale", "cell": cell})
            continue
        if document["status"] != "success":
            counts["failed"] += 1
            unresolved.append(
                {
                    "kind": "failed",
                    "cell": cell,
                    "error": document["last_error"],
                    "attempts": len(document["attempts"]),
                }
            )
            continue
        if source_raw_directory is None or scenarios is None or skill_text is None:
            counts["invalid"] += 1
            unresolved.append(
                {
                    "kind": "invalid",
                    "cell": cell,
                    "error": "source evidence is unavailable for judge validation",
                }
            )
            continue
        try:
            candidates, evaluations = load_source_pair(
                source_raw_directory,
                cell,
                matrix,
                scenarios[cell["scenario_id"]],
                skill_text,
                source_results["provenance"],
            )
        except (KeyError, RuntimeError, ValueError) as source_error:
            counts["invalid"] += 1
            unresolved.append(
                {"kind": "invalid", "cell": cell, "error": str(source_error)}
            )
            continue
        if error := judge_evidence_error(
            document,
            cell,
            config,
            scenarios[cell["scenario_id"]],
            candidates,
            evaluations,
        ):
            counts["invalid"] += 1
            unresolved.append({"kind": "invalid", "cell": cell, "error": error})
            continue
        counts["successful"] += 1
        documents.append(document)

    expected = len(cells)
    summary = summarize_judgments(documents, config)
    completeness = {
        "expected": expected,
        "successful": counts["successful"],
        "failed": counts["failed"],
        "missing": counts["missing"],
        "stale": counts["stale"],
        "invalid": counts["invalid"],
        "complete": counts["successful"] == expected,
    }
    source_semantic_accepted = source_results["semantic_acceptance"]["accepted"]
    source_integrity_accepted = source_results["condition_integrity"]["accepted"]
    quality_acceptance = {
        "expected_judgments": expected,
        "successful_judgments": counts["successful"],
        "cross_provider_judgments": summary["cross_provider_judgments"],
        "review_required": summary["review_required"],
        "accepted": (
            completeness["complete"]
            and source_semantic_accepted
            and source_integrity_accepted
            and summary["cross_provider_judgments"] == expected
            and summary["review_required"] == 0
        ),
    }
    return {
        "schema_version": 1,
        "generated_at": generated_at or run_pi_bench.utc_now(),
        "provenance": provenance,
        "judge": {
            "id": config["judge_id"],
            "version": config["version"],
            "source_matrix_id": config["source_matrix_id"],
        },
        "completeness": completeness,
        "semantic_authority": {
            "source_accepted": source_semantic_accepted,
            "condition_integrity_accepted": source_integrity_accepted,
            "rule": "Deterministic semantic and output-contract failures override judge preference.",
        },
        "quality_acceptance": quality_acceptance,
        "summary": summary,
        "limitations": list(config["limitations"]),
        "unresolved": unresolved,
    }


def write_judge_reports(results, results_directory):
    results_directory = Path(results_directory)
    results_directory.mkdir(parents=True, exist_ok=True)
    run_pi_bench.write_json_atomic(results_directory / "results.json", results)
    failures_path = results_directory / "failures.json"
    if results["unresolved"]:
        run_pi_bench.write_json_atomic(failures_path, results["unresolved"])
    elif failures_path.exists():
        failures_path.unlink()

    completeness = results["completeness"]
    accepted = results["quality_acceptance"]["accepted"]
    lines = [
        "# Independent quality-judge results",
        "",
        (
            f"**{'ACCEPTED' if accepted else 'NOT ACCEPTED'}: "
            f"{completeness['successful']}/{completeness['expected']} judgments successful.**"
        ),
        "",
        "## Semantic authority",
        "",
        (
            "- Source deterministic semantic acceptance: "
            + ("accepted" if results["semantic_authority"]["source_accepted"] else "not accepted")
            + "."
        ),
        (
            "- Source condition integrity: "
            + (
                "accepted"
                if results["semantic_authority"]["condition_integrity_accepted"]
                else "not accepted"
            )
            + "."
        ),
        "- Deterministic semantic failures override judge preference.",
        (
            "- Judge blocking findings requiring review: "
            f"{results['quality_acceptance']['review_required']}."
        ),
        "",
        "## Quality scores and preferences",
        "",
        "Preference counts remain separate from authoritative semantic outcomes.",
    ]
    for row in results["summary"]["comparisons"]:
        source = row["source_model"]
        judge = row["judge"]
        lines.extend(
            [
                "",
                (
                    f"### `{source['provider']}/{source['model']}:{source['thinking']}` "
                    f"— {row['comparison_id']}"
                ),
                "",
                f"Judge: `{judge['provider']}/{judge['model']}:{judge['thinking']}`.",
                f"Judgments: {row['judgments']}.",
                f"Review required: {row['review_required']}.",
                "",
                "| Result type | Counts |",
                "|---|---|",
                "| Authoritative outcomes | "
                + ", ".join(
                    f"{name}: {count}"
                    for name, count in row["authoritative_outcomes"].items()
                )
                + " |",
                "| Judge preferences | "
                + ", ".join(
                    f"{name}: {count}"
                    for name, count in row["judge_preferences"].items()
                )
                + " |",
                "",
                "| Condition | Dimension | Applicable | N/A | Mean |",
                "|---|---|---:|---:|---:|",
            ]
        )
        for condition, dimensions in row["dimensions"].items():
            for dimension, metric in dimensions.items():
                mean = "n/a" if metric["mean"] is None else f"{metric['mean']:.2f}"
                lines.append(
                    f"| {condition} | `{dimension}` | "
                    f"{metric['applicable_samples']} | "
                    f"{metric['not_applicable_samples']} | {mean} |"
                )

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {limitation}" for limitation in results["limitations"])
    if results["unresolved"]:
        lines.extend(
            [
                "",
                "## Unresolved judgments",
                "",
                f"See `failures.json` for {len(results['unresolved'])} unresolved cells.",
            ]
        )
    (results_directory / "RESULTS.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def run_judge_cell(
    cell,
    config,
    scenario,
    candidates,
    evaluations,
    provenance,
    raw_path,
    invoke=None,
    pause=None,
    now=None,
):
    if set(candidates) != {cell["left_condition"], cell["right_condition"]}:
        raise ValueError("candidate conditions do not match judge cell")
    if set(evaluations) != set(candidates):
        raise ValueError("candidate evaluations do not match judge cell")
    assignment = blind_assignment(cell)
    prompt = build_judge_prompt(config, scenario, candidates, assignment)
    prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    hashes = candidate_hashes(candidates)
    attempts = []
    raw_path = Path(raw_path)
    if raw_path.exists():
        existing = run_pi_bench.strict_json_loads(raw_path.read_text(encoding="utf-8"))
        if error := judge_document_error(existing, config):
            raise RuntimeError(f"invalid judge result cannot be reused: {raw_path}: {error}")
        if (
            existing["cell"] != cell
            or existing["provenance"] != provenance
            or existing["blind_assignment"] != assignment
            or existing["candidate_sha256"] != hashes
            or existing["prompt_sha256"] != prompt_sha256
        ):
            raise RuntimeError(f"stale judge result cannot be reused: {raw_path}")
        if existing["status"] == "success":
            if error := judge_evidence_error(
                existing,
                cell,
                config,
                scenario,
                candidates,
                evaluations,
            ):
                raise RuntimeError(
                    f"invalid judge result cannot be reused: {raw_path}: {error}"
                )
            return {"action": "skipped", "path": str(raw_path)}
        attempts = list(existing["attempts"])

    if invoke is None:
        invoke = run_pi_bench.invoke_pi
    if pause is None:
        pause = time.sleep
    if now is None:
        now = run_pi_bench.utc_now
    command = build_judge_command(cell, config, prompt)
    document = {
        "schema_version": 1,
        "status": "failure",
        "cell": cell,
        "provenance": provenance,
        "blind_assignment": assignment,
        "candidate_sha256": hashes,
        "prompt_sha256": prompt_sha256,
        "attempts": attempts,
        "updated_at": now(),
        "last_error": {"kind": "pending", "message": "Judge call not started."},
    }
    for attempt_in_run in range(config["retry_limit"]):
        started_at = now()
        call = invoke(command, config["timeout_seconds"])
        attempt = {
            "number": len(document["attempts"]) + 1,
            "started_at": started_at,
            "status": call["status"],
            "duration_ms": call["duration_ms"],
        }
        if call["status"] == "failure":
            attempt["error"] = call["error"]
            if "partial_response" in call:
                attempt["partial_response"] = call["partial_response"]
        else:
            response = call["response"]
            error = judge_response_error(response, cell)
            verdict = None
            if error is None:
                try:
                    verdict = parse_judge_output(response["text"], config)
                except (ValueError, json.JSONDecodeError) as parse_error:
                    error = str(parse_error)
            if error is not None:
                attempt["status"] = "failure"
                attempt["error"] = {"kind": "verdict", "message": error}
                attempt["partial_response"] = response
            else:
                attempt["status"] = "success"
                document["attempts"].append(attempt)
                outcome = authoritative_outcome(
                    cell["left_condition"],
                    cell["right_condition"],
                    evaluations[cell["left_condition"]],
                    evaluations[cell["right_condition"]],
                    verdict,
                    assignment,
                )
                document.update(
                    status="success",
                    updated_at=now(),
                    duration_ms=call["duration_ms"],
                    response=response,
                    verdict=verdict,
                    outcome=outcome,
                )
                document.pop("last_error", None)
                run_pi_bench.write_json_atomic(raw_path, document)
                return {"action": "completed", "path": str(raw_path)}
        document["attempts"].append(attempt)
        document["last_error"] = attempt["error"]
        document["updated_at"] = now()
        run_pi_bench.write_json_atomic(raw_path, document)
        if attempt_in_run + 1 < config["retry_limit"]:
            pause(config["inter_call_delay_seconds"])
    return {"action": "failed", "path": str(raw_path)}


def execute_judging(
    config_path,
    matrix_path,
    benchmark_results_directory,
    judge_results_directory,
    report_only=False,
    invoke=None,
    pause=None,
    emit=print,
    provenance=None,
):
    config_path = Path(config_path)
    matrix_path = Path(matrix_path)
    if pause is None:
        pause = time.sleep
    benchmark_results_directory = Path(benchmark_results_directory)
    judge_results_directory = Path(judge_results_directory)
    config = load_judge_config(config_path)
    matrix = run_pi_bench.load_matrix(matrix_path)
    validate_judge_matrix(config, matrix)
    fixtures, scenarios = run_pi_bench.load_matrix_scenarios(matrix)
    source_results_path = benchmark_results_directory / "results.json"
    source_results = run_pi_bench.strict_json_loads(
        source_results_path.read_text(encoding="utf-8")
    )
    validate_source_results(source_results, matrix, matrix_path=matrix_path)
    source_raw_directory = benchmark_results_directory / "raw"
    source_provenance = source_results["provenance"]
    if not report_only and source_provenance["package_dirty"]:
        raise RuntimeError(
            "judge generation requires benchmark evidence from a clean git working tree"
        )
    source_skill_text = run_pi_bench.SKILL_PATH.read_text(encoding="utf-8")
    validate_source_evidence(
        source_results,
        matrix,
        scenarios,
        source_raw_directory,
        source_skill_text,
    )
    if provenance is None:
        provenance = collect_judge_provenance(
            config_path,
            matrix_path,
            source_results,
            source_raw_directory,
        )
    raw_directory = judge_results_directory / "raw"
    raw_directory.mkdir(parents=True, exist_ok=True)

    if not report_only:
        if "skill_sha256" in provenance:
            if error := source_compatibility_error(source_provenance, provenance):
                raise RuntimeError(error)
        skill_text = source_skill_text
        if run_pi_bench.tree_sha256(run_pi_bench.SKILL_DIR) != source_provenance[
            "skill_sha256"
        ]:
            raise RuntimeError(
                "judge generation requires the benchmark skill snapshot"
            )
        cells = list(iter_judge_cells(matrix, config))
        for index, cell in enumerate(cells, 1):
            candidates, evaluations = load_source_pair(
                source_raw_directory,
                cell,
                matrix,
                scenarios[cell["scenario_id"]],
                skill_text,
                source_provenance,
            )
            raw_path = raw_directory / judge_raw_result_name(cell)
            source = cell["source_model"]
            judge = cell["judge"]
            emit(
                f"[{index}/{len(cells)}] {source['provider']}/{source['model']} "
                f"{cell['comparison_id']} {cell['scenario_id']} "
                f"r{cell['source_repetition']} -> {judge['provider']}/{judge['model']}"
            )
            try:
                outcome = run_judge_cell(
                    cell,
                    config,
                    scenarios[cell["scenario_id"]],
                    candidates,
                    evaluations,
                    provenance,
                    raw_path,
                    invoke=invoke,
                    pause=pause,
                )
            except RuntimeError as error:
                emit(f"  STALE {error}")
                continue
            emit(f"  {outcome['action'].upper()}")
            if outcome["action"] != "skipped" and index < len(cells):
                pause(config["inter_call_delay_seconds"])

    results = aggregate_judge_results(
        matrix,
        config,
        provenance,
        raw_directory,
        source_results,
        source_raw_directory=source_raw_directory,
        scenarios=scenarios,
        skill_text=source_skill_text,
    )
    write_judge_reports(results, judge_results_directory)
    return results


def judge_accepted(results):
    return (
        results["completeness"]["complete"]
        and results["semantic_authority"]["source_accepted"]
        and results["semantic_authority"]["condition_integrity_accepted"]
        and results["quality_acceptance"]["accepted"]
    )


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=f"judge config (default: {DEFAULT_CONFIG_PATH})",
    )
    parser.add_argument(
        "--matrix",
        type=Path,
        default=DEFAULT_MATRIX_PATH,
        help=f"source benchmark matrix (default: {DEFAULT_MATRIX_PATH})",
    )
    parser.add_argument(
        "--benchmark-results-dir",
        type=Path,
        default=DEFAULT_BENCHMARK_RESULTS_DIR,
        help=(
            "completed benchmark result directory "
            f"(default: {DEFAULT_BENCHMARK_RESULTS_DIR})"
        ),
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_JUDGE_RESULTS_DIR,
        help=f"judge result directory (default: {DEFAULT_JUDGE_RESULTS_DIR})",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="aggregate existing judge cells without model calls",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        results = execute_judging(
            args.config,
            args.matrix,
            args.benchmark_results_dir,
            args.results_dir,
            report_only=args.report_only,
        )
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError,
        RuntimeError,
        subprocess.CalledProcessError,
    ) as error:
        parser.error(str(error))
    print((args.results_dir / "RESULTS.md").read_text(encoding="utf-8"), end="")
    return 0 if judge_accepted(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
