import contextlib
import copy
import io
import hashlib
import json
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals"
ARCHIVE_CONFIG = ROOT / "archive" / "pre-release" / "evals" / "config"
CONFIG_PATH = ARCHIVE_CONFIG / "initial-quality-judge.json"
MATRIX_PATH = ARCHIVE_CONFIG / "initial-skill-matrix.json"
INDEPENDENT_CONFIG_PATH = ARCHIVE_CONFIG / "independent-review-quality-judge.json"
INDEPENDENT_MATRIX_PATH = ARCHIVE_CONFIG / "independent-review-matrix.json"
RELEASE_CANDIDATE_CONFIG_PATH = EVALS / "release-candidate-quality-judge.json"
RELEASE_CANDIDATE_MATRIX_PATH = EVALS / "release-candidate-matrix.json"
sys.path.insert(0, str(EVALS))

import run_quality_judge


def schema_v2_design():
    matrix = json.loads(MATRIX_PATH.read_text())
    matrix.update(
        schema_version=2,
        run_kind="release-candidate",
        judge_config_path="release-candidate-quality-judge.json",
        matrix_id="release-candidate",
        conditions=["baseline", "native-skill", "guarded"],
        conditions_by_scenario={
            scenario_id: (
                ["baseline", "native-skill"]
                if scenario_id == "schema-constrained-incident-status"
                else ["baseline", "native-skill", "guarded"]
            )
            for scenario_id in matrix["scenario_ids"]
        },
        semantic_gate_conditions=["native-skill", "guarded"],
        max_parallel_calls=3,
        max_parallel_calls_by_provider={
            "openai-codex": 1,
            "github-copilot": 2,
        },
        acceptance_thresholds={
            "applicable_cell_completeness": 1.0,
            "model_identity": 1.0,
            "routing_safety": 1.0,
            "semantic": 1.0,
            "procedure": 1.0,
            "output_contract": 1.0,
            "guard_integrity": 1.0,
            "positive_activation_minimum_fraction": {
                "numerator": 2,
                "denominator": 3,
            },
            "negative_activation_maximum_loaded": 0,
            "activation_applicable": True,
        },
    )
    matrix["isolation"]["tools_by_condition"] = {
        "baseline": [],
        "native-skill": ["read"],
        "guarded": [],
    }
    config = json.loads(CONFIG_PATH.read_text())
    config.update(
        schema_version=2,
        judge_id="release-candidate-quality",
        source_matrix_id=matrix["matrix_id"],
        comparisons=[
            {
                "id": "baseline-vs-native",
                "left_condition": "baseline",
                "right_condition": "native-skill",
                "role": "routing-control-cohort",
            },
            {
                "id": "native-vs-guarded",
                "left_condition": "native-skill",
                "right_condition": "guarded",
                "role": "end-to-end-package-path",
            },
        ],
        max_parallel_calls=3,
        max_parallel_calls_by_provider={
            "openai-codex": 1,
            "github-copilot": 2,
        },
        preference_claim="descriptive-only",
        acceptance_thresholds={
            "judge_completeness": 1.0,
            "cross_provider_mapping": 1.0,
            "maximum_review_required": 0,
        },
    )
    return matrix, config


def schema_v3_design():
    matrix, config = schema_v2_design()
    matrix["schema_version"] = 3
    matrix["acceptance_model"] = "hybrid-semantic-v1"
    matrix["objective_gate_conditions"] = matrix.pop("semantic_gate_conditions")
    matrix["acceptance_thresholds"]["objective_contract"] = matrix[
        "acceptance_thresholds"
    ].pop("semantic")
    matrix["acceptance_thresholds"]["objective_procedure"] = matrix[
        "acceptance_thresholds"
    ].pop("procedure")
    matrix["semantic_review"] = {
        "config_path": matrix["judge_config_path"],
        "applicability_field": "semantic_review_applicable",
        "gated_conditions": ["native-skill", "guarded"],
        "required_unique_candidate_coverage": 1.0,
        "accepted_label": "equivalent",
        "adverse_labels": ["not_equivalent", "uncertain"],
        "conflict_policy": "fail",
        "manual_override": False,
    }
    config["schema_version"] = 3
    config["verdict_schema_version"] = 2
    config["semantic_gate"] = {
        "enabled": True,
        "gated_conditions": ["native-skill", "guarded"],
        "applicability_field": "semantic_review_applicable",
        "accepted_label": "equivalent",
        "adverse_labels": ["not_equivalent", "uncertain"],
        "require_all_observations_accepted": True,
        "manual_override": False,
    }
    config["acceptance_thresholds"] = {
        "judge_completeness": 1.0,
        "cross_provider_mapping": 1.0,
        "semantic_candidate_coverage": 1.0,
        "maximum_not_equivalent": 0,
        "maximum_uncertain": 0,
        "maximum_conflicts": 0,
        "maximum_review_required": 0,
    }
    return matrix, config


class JudgeConfigTest(unittest.TestCase):
    def test_default_judge_reads_default_benchmark_output(self):
        self.assertEqual(
            run_quality_judge.DEFAULT_BENCHMARK_RESULTS_DIR,
            run_quality_judge.run_pi_bench.DEFAULT_RESULTS_DIR,
        )

    def test_initial_config_declares_complete_rubric_and_cross_provider_judges(self):
        config = run_quality_judge.load_judge_config(CONFIG_PATH)
        matrix = json.loads(MATRIX_PATH.read_text())

        self.assertEqual(
            [dimension["id"] for dimension in config["dimensions"]],
            [
                "factual_semantic_fidelity",
                "task_completion",
                "uncertainty_obligation",
                "technical_terminology",
                "safety_actionability",
                "readability_concision",
            ],
        )
        self.assertEqual(config["version"], 2)
        self.assertEqual(run_quality_judge.JUDGE_RUNNER_VERSION, "4")
        self.assertEqual(config["source_repetitions_minimum"], 3)
        self.assertEqual(
            [comparison["id"] for comparison in config["comparisons"]],
            ["baseline-vs-native", "baseline-vs-direct-prompt"],
        )
        for model in matrix["models"]:
            judge = config["judges_by_source_provider"][model["provider"]]
            self.assertNotEqual(judge["provider"], model["provider"])
        self.assertEqual(
            config["judges_by_source_provider"]["openai-codex"],
            {
                "provider": "github-copilot",
                "model": "gemini-3.6-flash",
                "thinking": "low",
            },
        )

    def test_independent_review_config_preserves_blind_cross_provider_design(self):
        config = run_quality_judge.load_judge_config(INDEPENDENT_CONFIG_PATH)
        matrix = run_quality_judge.run_pi_bench.load_matrix(
            INDEPENDENT_MATRIX_PATH
        )

        run_quality_judge.validate_judge_matrix(config, matrix)
        self.assertEqual(config["source_matrix_id"], "v1-independent-review")
        self.assertEqual(len(list(run_quality_judge.iter_judge_cells(matrix, config))), 108)

    def test_schema_v2_preregisters_parallelism_and_descriptive_preference(self):
        matrix, config = schema_v2_design()

        run_quality_judge.validate_judge_matrix(config, matrix)

        self.assertEqual(config["max_parallel_calls"], 3)
        self.assertEqual(config["preference_claim"], "descriptive-only")

    def test_release_candidate_judge_uses_matched_cross_provider_pairs(self):
        config = run_quality_judge.load_judge_config(
            RELEASE_CANDIDATE_CONFIG_PATH
        )
        matrix = run_quality_judge.run_pi_bench.load_matrix(
            RELEASE_CANDIDATE_MATRIX_PATH
        )
        cells = list(run_quality_judge.iter_judge_cells(matrix, config))

        self.assertEqual(len(cells), 99)
        self.assertEqual(
            [comparison["id"] for comparison in config["comparisons"]],
            ["baseline-vs-native", "native-vs-guarded"],
        )
        self.assertEqual(config["preference_claim"], "descriptive-only")
        self.assertFalse(
            any(
                cell["comparison_id"] == "native-vs-guarded"
                and cell["scenario_id"] == "hushvale-spore-transfer-csv"
                for cell in cells
            )
        )
        for cell in cells:
            self.assertNotEqual(
                cell["source_model"]["provider"], cell["judge"]["provider"]
            )
        with tempfile.TemporaryDirectory() as directory:
            results = run_quality_judge.aggregate_judge_results(
                matrix,
                config,
                {"judge_config_sha256": "a" * 64},
                Path(directory),
                {
                    "semantic_acceptance": {"accepted": True},
                    "condition_integrity": {"accepted": True},
                    "guard_integrity": {"accepted": True},
                },
            )
        self.assertEqual(len(results["applicability"]["groups"]), 33)
        self.assertEqual(
            sum(
                group["expected_judgments"]
                for group in results["applicability"]["groups"]
            ),
            99,
        )
        source_provenance = {
            "preregistered_judge_config_path": matrix["judge_config_path"],
            "preregistered_judge_config_sha256": hashlib.sha256(
                RELEASE_CANDIDATE_CONFIG_PATH.read_bytes()
            ).hexdigest(),
        }
        with tempfile.TemporaryDirectory() as directory:
            alternate = Path(directory) / "alternate-judge.json"
            alternate.write_bytes(RELEASE_CANDIDATE_CONFIG_PATH.read_bytes())
            with self.assertRaisesRegex(ValueError, "path is not preregistered"):
                run_quality_judge.validate_preregistered_judge_config(
                    alternate,
                    matrix,
                    source_provenance,
                )

    def test_validation_rejects_missing_dimension_and_same_provider_mapping(self):
        config = run_quality_judge.load_judge_config(CONFIG_PATH)

        missing = copy.deepcopy(config)
        missing["dimensions"].pop()
        with self.assertRaisesRegex(ValueError, "rubric dimensions"):
            run_quality_judge.validate_judge_config(missing)

        same_provider = copy.deepcopy(config)
        same_provider["judges_by_source_provider"]["openai-codex"]["provider"] = (
            "openai-codex"
        )
        with self.assertRaisesRegex(ValueError, "cross-provider"):
            run_quality_judge.validate_judge_config(same_provider)


def fake_judge_response(cell, text):
    measured = {"value": None, "available": False}
    return {
        "text": text,
        "provider": cell["judge"]["provider"],
        "model": cell["judge"]["model"],
        "response_model": cell["judge"]["model"],
        "stop_reason": "stop",
        "usage": {
            "input_tokens": dict(measured),
            "output_tokens": {
                "value": None,
                "available": False,
                "includes_reasoning": True,
            },
            "reasoning_tokens": dict(measured),
            "visible_output_tokens": {
                "value": None,
                "available": False,
                "derived": True,
            },
            "cache_read_tokens": dict(measured),
            "cache_write_tokens": dict(measured),
            "total_tokens": dict(measured),
        },
        "cost_usd": dict(measured),
        "routing": {
            "tool_calls": 0,
            "non_read_tool_calls": 0,
            "read_calls": 0,
            "successful_read_calls": 0,
            "failed_read_calls": 0,
            "skill_entrypoint_read_calls": 0,
            "skill_tree_read_calls": 0,
            "outside_skill_read_calls": 0,
            "skill_loaded": False,
        },
    }


def fake_source_response(source_cell, text):
    response = fake_judge_response(
        {"judge": source_cell},
        text,
    )
    if source_cell["condition"] == "native-skill":
        response["routing"].update(
            tool_calls=1,
            read_calls=1,
            successful_read_calls=1,
            skill_entrypoint_read_calls=1,
            skill_tree_read_calls=1,
            skill_loaded=True,
        )
    return response


def valid_verdict(config):
    scores = {
        dimension["id"]: {
            "applicable": True,
            "score": 4,
            "evidence": f"Evidence for {dimension['id']}.",
        }
        for dimension in config["dimensions"]
    }
    candidate = {"scores": copy.deepcopy(scores), "blocking_issues": []}
    if config["schema_version"] == 3:
        candidate["semantic_fidelity"] = {"label": "equivalent", "issues": []}
    return {
        "schema_version": 2 if config["schema_version"] == 3 else 1,
        "candidates": {
            "A": copy.deepcopy(candidate),
            "B": copy.deepcopy(candidate),
        },
        "preference": "A",
        "confidence": "medium",
        "preference_reason": "Candidate A is clearer with equal fidelity.",
    }


class JudgeCellTest(unittest.TestCase):
    def test_matrix_expands_to_unique_cross_provider_blind_cells(self):
        config = run_quality_judge.load_judge_config(CONFIG_PATH)
        matrix = run_quality_judge.run_pi_bench.load_matrix(MATRIX_PATH)
        cells = list(run_quality_judge.iter_judge_cells(matrix, config))

        self.assertEqual(len(cells), 108)
        identities = [run_quality_judge.judge_cell_id(cell) for cell in cells]
        self.assertEqual(len(identities), len(set(identities)))
        for cell in cells:
            self.assertNotEqual(
                cell["source_model"]["provider"], cell["judge"]["provider"]
            )

        grouped = {}
        for cell in cells:
            key = (
                cell["source_model"]["provider"],
                cell["source_model"]["model"],
                cell["comparison_id"],
                cell["scenario_id"],
            )
            grouped.setdefault(key, []).append(cell)
        for group in grouped.values():
            group.sort(key=lambda cell: cell["source_repetition"])
            first = run_quality_judge.blind_assignment(group[0])
            second = run_quality_judge.blind_assignment(group[1])
            self.assertNotEqual(first["A"], second["A"])
            self.assertEqual(set(first.values()), set(second.values()))

    def test_schema_v2_judges_only_matched_applicable_pairs(self):
        matrix, config = schema_v2_design()

        cells = list(run_quality_judge.iter_judge_cells(matrix, config))

        expected = len(matrix["models"]) * matrix["repetitions"] * (
            len(matrix["scenario_ids"])
            + len(matrix["scenario_ids"]) - 1
        )
        self.assertEqual(len(cells), expected)
        self.assertFalse(
            any(
                cell["comparison_id"] == "native-vs-guarded"
                and cell["scenario_id"] == "schema-constrained-incident-status"
                for cell in cells
            )
        )

    def test_schema_v2_rejects_comparison_without_matched_scenario(self):
        matrix, config = schema_v2_design()
        for scenario_id in matrix["scenario_ids"]:
            matrix["conditions_by_scenario"][scenario_id] = [
                "baseline",
                "native-skill",
            ]

        with self.assertRaisesRegex(ValueError, "no matched scenarios"):
            run_quality_judge.validate_judge_matrix(config, matrix)

    def test_schema_v2_execution_order_fills_preregistered_provider_lanes(self):
        matrix, config = schema_v2_design()
        cells = list(run_quality_judge.iter_judge_cells(matrix, config))

        ordered = run_quality_judge.provider_bounded_order(
            cells,
            config["max_parallel_calls_by_provider"],
            lambda cell: cell["judge"]["provider"],
        )

        self.assertEqual(
            [cell["judge"]["provider"] for cell in ordered[:3]],
            ["openai-codex", "github-copilot", "github-copilot"],
        )
        self.assertEqual(
            sorted(run_quality_judge.judge_cell_id(cell) for cell in ordered),
            sorted(run_quality_judge.judge_cell_id(cell) for cell in cells),
        )

    def test_raw_names_stay_unique_when_model_differs_only_by_thinking(self):
        config = run_quality_judge.load_judge_config(CONFIG_PATH)
        matrix = run_quality_judge.run_pi_bench.load_matrix(MATRIX_PATH)
        additional = copy.deepcopy(matrix["models"][0])
        additional["thinking"] = "low"
        matrix["models"].append(additional)

        cells = list(run_quality_judge.iter_judge_cells(matrix, config))
        names = [run_quality_judge.judge_raw_result_name(cell) for cell in cells]

        self.assertEqual(len(names), len(set(names)))

    def test_matrix_validation_rejects_insufficient_samples_or_missing_judge(self):
        config = run_quality_judge.load_judge_config(CONFIG_PATH)
        matrix = run_quality_judge.run_pi_bench.load_matrix(MATRIX_PATH)

        insufficient = copy.deepcopy(matrix)
        insufficient["repetitions"] = 2
        with self.assertRaisesRegex(ValueError, "repetitions"):
            run_quality_judge.validate_judge_matrix(config, insufficient)

        missing = copy.deepcopy(config)
        missing["judges_by_source_provider"].pop("github-copilot")
        with self.assertRaisesRegex(ValueError, "source provider"):
            run_quality_judge.validate_judge_matrix(missing, matrix)


class JudgePromptAndVerdictTest(unittest.TestCase):
    def test_prompt_is_blind_and_contains_source_task_rubric_and_candidates(self):
        config = run_quality_judge.load_judge_config(CONFIG_PATH)
        scenario = {
            "task": "Rewrite for operators.",
            "source": "Operators may restart `api` after 09:00 UTC.",
        }
        candidates = {
            "baseline": "After 09:00 UTC, operators may restart `api`.",
            "native-skill": "Operators may restart `api` after 09:00 UTC.",
        }
        assignment = {"A": "native-skill", "B": "baseline"}

        prompt = run_quality_judge.build_judge_prompt(
            config, scenario, candidates, assignment
        )

        self.assertIn(scenario["task"], prompt)
        self.assertIn(scenario["source"], prompt)
        self.assertIn("Candidate A\n\nOperators may restart", prompt)
        self.assertIn("Candidate B\n\nAfter 09:00 UTC", prompt)
        for dimension in config["dimensions"]:
            self.assertIn(dimension["id"], prompt)
            self.assertIn(dimension["instruction"], prompt)
        self.assertNotIn("native-skill", prompt)
        self.assertNotIn("baseline", prompt)
        self.assertNotIn("provider", prompt.lower())
        self.assertNotIn("model", prompt.lower())

    def test_verdict_parser_accepts_exact_schema_and_rejects_invalid_evidence(self):
        config = run_quality_judge.load_judge_config(CONFIG_PATH)
        verdict = valid_verdict(config)
        parsed = run_quality_judge.parse_judge_output(json.dumps(verdict), config)
        self.assertEqual(parsed, verdict)
        fenced = run_quality_judge.parse_judge_output(
            f"```json\n{json.dumps(verdict)}\n```", config
        )
        self.assertEqual(fenced, verdict)
        with self.assertRaises((ValueError, json.JSONDecodeError)):
            run_quality_judge.parse_judge_output(
                f"Result:\n```json\n{json.dumps(verdict)}\n```", config
            )

        invalid_score = copy.deepcopy(verdict)
        invalid_score["candidates"]["A"]["scores"][
            "readability_concision"
        ]["score"] = 6
        with self.assertRaisesRegex(ValueError, "score"):
            run_quality_judge.parse_judge_output(json.dumps(invalid_score), config)

        missing_dimension = copy.deepcopy(verdict)
        missing_dimension["candidates"]["A"]["scores"].pop(
            "technical_terminology"
        )
        with self.assertRaisesRegex(ValueError, "dimension"):
            run_quality_judge.parse_judge_output(
                json.dumps(missing_dimension), config
            )

        invalid_issue = copy.deepcopy(verdict)
        invalid_issue["candidates"]["B"]["blocking_issues"] = [
            {"category": "style", "evidence": "Style alone is not blocking."}
        ]
        with self.assertRaisesRegex(ValueError, "category"):
            run_quality_judge.parse_judge_output(json.dumps(invalid_issue), config)

    def test_verdict_parser_rejects_duplicate_json_keys(self):
        config = run_quality_judge.load_judge_config(CONFIG_PATH)
        with self.assertRaisesRegex(ValueError, "duplicate object key"):
            run_quality_judge.parse_judge_output(
                '{"schema_version":1,"schema_version":1}', config
            )


class SourceBenchmarkTest(unittest.TestCase):
    def test_source_results_require_complete_integrity_but_allow_semantic_failures(self):
        matrix = run_quality_judge.run_pi_bench.load_matrix(MATRIX_PATH)
        results = {
            "schema_version": 1,
            "matrix": {"id": "v1", "version": matrix["version"]},
            "completeness": {"complete": True},
            "condition_integrity": {"accepted": True},
            "semantic_acceptance": {"accepted": False},
            "provenance": {
                "matrix_sha256": run_quality_judge.hashlib.sha256(
                    MATRIX_PATH.read_bytes()
                ).hexdigest()
            },
        }
        run_quality_judge.validate_source_results(results, matrix)

        incomplete = copy.deepcopy(results)
        incomplete["completeness"]["complete"] = False
        with self.assertRaisesRegex(ValueError, "complete"):
            run_quality_judge.validate_source_results(incomplete, matrix)

        invalid_integrity = copy.deepcopy(results)
        invalid_integrity["condition_integrity"]["accepted"] = False
        with self.assertRaisesRegex(ValueError, "integrity"):
            run_quality_judge.validate_source_results(invalid_integrity, matrix)

    def test_source_evidence_recomputes_authoritative_aggregate_fields(self):
        matrix = run_quality_judge.run_pi_bench.load_matrix(MATRIX_PATH)
        stored = {
            "completeness": {"complete": True},
            "condition_integrity": {"accepted": True},
            "semantic_acceptance": {"accepted": True},
            "provenance": {"matrix_sha256": "a" * 64},
        }

        run_quality_judge.validate_source_evidence(
            stored,
            matrix,
            {},
            Path("raw"),
            "skill",
            aggregate_function=lambda *_args, **_kwargs: copy.deepcopy(stored),
        )
        recomputed = copy.deepcopy(stored)
        recomputed["semantic_acceptance"]["accepted"] = False
        with self.assertRaisesRegex(ValueError, "semantic acceptance"):
            run_quality_judge.validate_source_evidence(
                stored,
                matrix,
                {},
                Path("raw"),
                "skill",
                aggregate_function=lambda *_args, **_kwargs: recomputed,
            )

    def test_source_pair_is_loaded_from_validated_benchmark_raw_cells(self):
        config = run_quality_judge.load_judge_config(CONFIG_PATH)
        matrix = run_quality_judge.run_pi_bench.load_matrix(MATRIX_PATH)
        fixtures = run_quality_judge.run_pi_bench.load_fixtures()
        scenarios = run_quality_judge.run_pi_bench.load_scenarios(fixtures)
        cell = next(run_quality_judge.iter_judge_cells(matrix, config))
        scenario = scenarios[cell["scenario_id"]]
        provenance = {
            "runner_version": "1",
            "matrix_sha256": "a" * 64,
            "package_commit": "b" * 40,
            "package_dirty": False,
            "skill_sha256": "c" * 64,
            "pi_version": "0.84.1",
        }
        skill_text = run_quality_judge.run_pi_bench.SKILL_PATH.read_text()

        with tempfile.TemporaryDirectory() as directory:
            raw = Path(directory)
            expected = {}
            for condition in (cell["left_condition"], cell["right_condition"]):
                source_cell = run_quality_judge.source_cell(cell, condition)
                text = f"Candidate output for {condition}."
                expected[condition] = text
                path = raw / run_quality_judge.run_pi_bench.raw_result_name(source_cell)
                run_quality_judge.run_pi_bench.run_cell(
                    source_cell,
                    matrix,
                    scenario,
                    skill_text,
                    provenance,
                    path,
                    invoke=lambda _command, _timeout, source_cell=source_cell, text=text: {
                        "status": "success",
                        "duration_ms": 5,
                        "response": fake_source_response(source_cell, text),
                    },
                    pause=lambda _: None,
                    now=lambda: "2026-08-09T12:00:00+00:00",
                )

            candidates, evaluations = run_quality_judge.load_source_pair(
                raw,
                cell,
                matrix,
                scenario,
                skill_text,
                provenance,
            )

        self.assertEqual(candidates, expected)
        self.assertEqual(set(evaluations), set(expected))
        self.assertTrue(
            all(
                isinstance(value["semantic_gate_passed"], bool)
                for value in evaluations.values()
            )
        )


class JudgeEvidenceTest(unittest.TestCase):
    def test_evidence_recomputes_prompt_candidates_and_authoritative_outcome(self):
        config = run_quality_judge.load_judge_config(CONFIG_PATH)
        matrix = run_quality_judge.run_pi_bench.load_matrix(MATRIX_PATH)
        cell = next(run_quality_judge.iter_judge_cells(matrix, config))
        scenario = {"task": "Rewrite.", "source": "Service may stop."}
        candidates = {
            cell["left_condition"]: "Service may stop.",
            cell["right_condition"]: "The service may stop.",
        }
        evaluations = {
            cell["left_condition"]: {"semantic_gate_passed": False},
            cell["right_condition"]: {"semantic_gate_passed": True},
        }
        assignment = run_quality_judge.blind_assignment(cell)
        verdict = valid_verdict(config)
        prompt = run_quality_judge.build_judge_prompt(
            config, scenario, candidates, assignment
        )
        document = {
            "blind_assignment": assignment,
            "candidate_sha256": run_quality_judge.candidate_hashes(candidates),
            "prompt_sha256": run_quality_judge.hashlib.sha256(
                prompt.encode()
            ).hexdigest(),
            "response": fake_judge_response(cell, json.dumps(verdict)),
            "verdict": verdict,
            "outcome": run_quality_judge.authoritative_outcome(
                cell["left_condition"],
                cell["right_condition"],
                evaluations[cell["left_condition"]],
                evaluations[cell["right_condition"]],
                verdict,
                assignment,
            ),
        }

        self.assertIsNone(
            run_quality_judge.judge_evidence_error(
                document, cell, config, scenario, candidates, evaluations
            )
        )
        document["response"]["text"] = "not json"
        self.assertIn(
            "response verdict",
            run_quality_judge.judge_evidence_error(
                document, cell, config, scenario, candidates, evaluations
            ),
        )
        document["response"]["text"] = json.dumps(verdict)
        document["outcome"]["winner"] = cell["left_condition"]
        self.assertIn(
            "outcome",
            run_quality_judge.judge_evidence_error(
                document, cell, config, scenario, candidates, evaluations
            ),
        )


class JudgeCellPersistenceTest(unittest.TestCase):
    def setUp(self):
        self.config = run_quality_judge.load_judge_config(CONFIG_PATH)
        matrix = run_quality_judge.run_pi_bench.load_matrix(MATRIX_PATH)
        self.cell = next(run_quality_judge.iter_judge_cells(matrix, self.config))
        self.scenario = {
            "task": "Rewrite for operators.",
            "source": "Operators may restart `api` after 09:00 UTC.",
        }
        self.candidates = {
            self.cell["left_condition"]: "Operators may restart `api` after 09:00 UTC.",
            self.cell["right_condition"]: "After 09:00 UTC, operators may restart `api`.",
        }
        self.evaluations = {
            self.cell["left_condition"]: {"semantic_gate_passed": True},
            self.cell["right_condition"]: {"semantic_gate_passed": True},
        }
        self.provenance = {"judge_config_sha256": "a" * 64}

    def test_success_persists_blind_evidence_and_resumes_without_call(self):
        verdict = valid_verdict(self.config)
        calls = []

        def invoke(command, timeout_seconds):
            calls.append((command, timeout_seconds))
            return {
                "status": "success",
                "duration_ms": 25,
                "response": fake_judge_response(
                    self.cell, json.dumps(verdict)
                ),
            }

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cell.json"
            result = run_quality_judge.run_judge_cell(
                self.cell,
                self.config,
                self.scenario,
                self.candidates,
                self.evaluations,
                self.provenance,
                path,
                invoke=invoke,
                pause=lambda _: None,
                now=lambda: "2026-08-09T12:00:00+00:00",
            )
            document = json.loads(path.read_text())

            self.assertEqual(result["action"], "completed")
            self.assertEqual(document["status"], "success")
            self.assertEqual(document["verdict"], verdict)
            self.assertEqual(
                set(document["blind_assignment"].values()),
                {self.cell["left_condition"], self.cell["right_condition"]},
            )
            self.assertEqual(len(document["candidate_sha256"]), 2)
            self.assertEqual(document["outcome"]["basis"], "judge-preference")
            self.assertNotIn(self.cell["left_condition"], calls[0][0][-1])
            self.assertNotIn(self.cell["right_condition"], calls[0][0][-1])

            resumed = run_quality_judge.run_judge_cell(
                self.cell,
                self.config,
                self.scenario,
                self.candidates,
                self.evaluations,
                self.provenance,
                path,
                invoke=lambda *_: self.fail("resumed cell invoked judge"),
            )
            self.assertEqual(resumed["action"], "skipped")

    def test_invalid_verdict_is_saved_then_retried(self):
        verdict = valid_verdict(self.config)
        responses = iter(
            [
                fake_judge_response(self.cell, "not json"),
                fake_judge_response(self.cell, json.dumps(verdict)),
            ]
        )

        def invoke(_command, _timeout_seconds):
            return {
                "status": "success",
                "duration_ms": 10,
                "response": next(responses),
            }

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cell.json"
            run_quality_judge.run_judge_cell(
                self.cell,
                self.config,
                self.scenario,
                self.candidates,
                self.evaluations,
                self.provenance,
                path,
                invoke=invoke,
                pause=lambda _: None,
                now=lambda: "2026-08-09T12:00:00+00:00",
            )
            document = json.loads(path.read_text())

        self.assertEqual(
            [attempt["status"] for attempt in document["attempts"]],
            ["failure", "success"],
        )
        self.assertEqual(document["attempts"][0]["error"]["kind"], "verdict")
        self.assertIn("partial_response", document["attempts"][0])
        self.assertIsNone(
            run_quality_judge.judge_document_error(document, self.config)
        )
        document["attempts"][0]["partial_response"]["routing"].update(
            tool_calls=1,
            non_read_tool_calls=1,
        )
        self.assertIn(
            "partial",
            run_quality_judge.judge_document_error(document, self.config),
        )


class JudgeAggregationTest(unittest.TestCase):
    def test_summary_unblinds_scores_and_keeps_authoritative_outcomes_separate(self):
        config = run_quality_judge.load_judge_config(CONFIG_PATH)
        matrix = run_quality_judge.run_pi_bench.load_matrix(MATRIX_PATH)
        cells = [
            cell
            for cell in run_quality_judge.iter_judge_cells(matrix, config)
            if cell["comparison_id"] == "baseline-vs-native"
        ][:2]
        documents = []
        for index, cell in enumerate(cells):
            assignment = run_quality_judge.blind_assignment(cell)
            verdict = valid_verdict(config)
            verdict["preference"] = "A"
            native_label = next(
                label
                for label, condition in assignment.items()
                if condition == "native-skill"
            )
            verdict["candidates"][native_label]["scores"][
                "readability_concision"
            ]["score"] = 5
            evaluations = {
                "baseline": {"semantic_gate_passed": index != 0},
                "native-skill": {"semantic_gate_passed": True},
            }
            documents.append(
                {
                    "cell": cell,
                    "blind_assignment": assignment,
                    "verdict": verdict,
                    "outcome": run_quality_judge.authoritative_outcome(
                        "baseline",
                        "native-skill",
                        evaluations["baseline"],
                        evaluations["native-skill"],
                        verdict,
                        assignment,
                    ),
                }
            )

        summary = run_quality_judge.summarize_judgments(documents, config)
        row = summary["comparisons"][0]

        self.assertEqual(row["authoritative_outcomes"]["native-skill"], 2)
        self.assertEqual(row["judge_preferences"], {"baseline": 1, "native-skill": 1})
        self.assertEqual(row["position_preferences"], {"A": 2})
        self.assertEqual(
            row["dimensions"]["native-skill"]["readability_concision"]["mean"],
            5,
        )
        self.assertEqual(row["review_required"], 0)
        self.assertEqual(summary["cross_provider_judgments"], 2)

    def test_summary_marks_blocking_findings_for_review(self):
        config = run_quality_judge.load_judge_config(CONFIG_PATH)
        matrix = run_quality_judge.run_pi_bench.load_matrix(MATRIX_PATH)
        cell = next(run_quality_judge.iter_judge_cells(matrix, config))
        assignment = run_quality_judge.blind_assignment(cell)
        verdict = valid_verdict(config)
        verdict["candidates"]["A"]["blocking_issues"] = [
            {"category": "safety", "evidence": "Warning follows command."}
        ]
        evaluations = {
            cell["left_condition"]: {"semantic_gate_passed": True},
            cell["right_condition"]: {"semantic_gate_passed": True},
        }
        outcome = run_quality_judge.authoritative_outcome(
            cell["left_condition"],
            cell["right_condition"],
            evaluations[cell["left_condition"]],
            evaluations[cell["right_condition"]],
            verdict,
            assignment,
        )

        summary = run_quality_judge.summarize_judgments(
            [
                {
                    "cell": cell,
                    "blind_assignment": assignment,
                    "verdict": verdict,
                    "outcome": outcome,
                }
            ],
            config,
        )

        self.assertEqual(summary["review_required"], 1)
        self.assertEqual(summary["blocking_issue_counts"]["safety"], 1)


class JudgeReportingTest(unittest.TestCase):
    def test_empty_raw_directory_reports_every_cell_missing_and_not_accepted(self):
        config = run_quality_judge.load_judge_config(CONFIG_PATH)
        matrix = run_quality_judge.run_pi_bench.load_matrix(MATRIX_PATH)
        provenance = {"judge_config_sha256": "a" * 64}
        source_results = {
            "semantic_acceptance": {"accepted": True},
            "condition_integrity": {"accepted": True},
        }

        with tempfile.TemporaryDirectory() as directory:
            results = run_quality_judge.aggregate_judge_results(
                matrix,
                config,
                provenance,
                Path(directory),
                source_results,
                generated_at="2026-08-09T12:00:00+00:00",
            )

        self.assertEqual(results["completeness"]["expected"], 108)
        self.assertEqual(results["completeness"]["missing"], 108)
        self.assertFalse(results["completeness"]["complete"])
        self.assertFalse(results["quality_acceptance"]["accepted"])
        self.assertTrue(results["semantic_authority"]["source_accepted"])
        self.assertEqual(len(results["unresolved"]), 108)

    def test_reports_put_semantic_authority_before_quality_and_show_limits(self):
        config = run_quality_judge.load_judge_config(CONFIG_PATH)
        matrix = run_quality_judge.run_pi_bench.load_matrix(MATRIX_PATH)
        provenance = {"judge_config_sha256": "a" * 64}
        source_results = {
            "semantic_acceptance": {"accepted": False},
            "condition_integrity": {"accepted": True},
        }
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            results = run_quality_judge.aggregate_judge_results(
                matrix,
                config,
                provenance,
                directory / "raw",
                source_results,
                generated_at="2026-08-09T12:00:00+00:00",
            )
            run_quality_judge.write_judge_reports(results, directory)
            report = (directory / "RESULTS.md").read_text()
            stored = json.loads((directory / "results.json").read_text())
            failures = json.loads((directory / "failures.json").read_text())

        self.assertEqual(stored, results)
        self.assertEqual(failures, results["unresolved"])
        self.assertLess(
            report.index("## Semantic authority"),
            report.index("## Quality scores and preferences"),
        )
        self.assertIn("Deterministic semantic, applicable-procedure", report)
        self.assertIn("## Limitations", report)
        for limitation in config["limitations"]:
            self.assertIn(limitation, report)


class JudgeOrchestrationTest(unittest.TestCase):
    def test_evaluator_commit_can_change_when_source_skill_snapshot_is_unchanged(self):
        source = {
            "package_commit": "a" * 40,
            "package_dirty": False,
            "skill_sha256": "c" * 64,
        }
        current = {
            "package_commit": "b" * 40,
            "package_dirty": False,
            "skill_sha256": "c" * 64,
        }

        self.assertIsNone(
            run_quality_judge.source_compatibility_error(source, current)
        )
        self.assertIn(
            "benchmark package commit",
            run_quality_judge.source_compatibility_error(
                source, current, require_same_commit=True
            ),
        )
        current["skill_sha256"] = "d" * 64
        self.assertIn(
            "skill snapshot",
            run_quality_judge.source_compatibility_error(source, current),
        )

    def source_results(self, package_dirty=False):
        return {
            "schema_version": 1,
            "matrix": {
                "id": "v1",
                "version": json.loads(MATRIX_PATH.read_text())["version"],
            },
            "completeness": {"complete": True},
            "condition_integrity": {"accepted": True},
            "semantic_acceptance": {"accepted": True},
            "provenance": {
                "runner_version": "1",
                "matrix_sha256": run_quality_judge.hashlib.sha256(
                    MATRIX_PATH.read_bytes()
                ).hexdigest(),
                "package_commit": "b" * 40,
                "package_dirty": package_dirty,
                "skill_sha256": "c" * 64,
                "pi_version": "0.84.1",
            },
        }

    def test_report_only_never_invokes_judge_and_writes_incomplete_report(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            source = directory / "source"
            source.mkdir()
            (source / "results.json").write_text(json.dumps(self.source_results()))
            destination = directory / "judge"

            with mock.patch.object(
                run_quality_judge, "validate_source_evidence"
            ) as validate:
                results = run_quality_judge.execute_judging(
                    CONFIG_PATH,
                    MATRIX_PATH,
                    source,
                    destination,
                    report_only=True,
                    invoke=lambda *_: self.fail("report-only invoked judge"),
                    provenance={"judge_config_sha256": "a" * 64},
                )
            validate.assert_called_once()

            self.assertFalse(results["completeness"]["complete"])
            self.assertTrue((destination / "results.json").exists())
            self.assertTrue((destination / "RESULTS.md").exists())

    def test_generation_uses_configured_delay_between_cells(self):
        config = run_quality_judge.load_judge_config(CONFIG_PATH)
        matrix = run_quality_judge.run_pi_bench.load_matrix(MATRIX_PATH)
        cells = list(run_quality_judge.iter_judge_cells(matrix, config))[:2]
        source_results = self.source_results()
        source_results["provenance"]["skill_sha256"] = (
            run_quality_judge.run_pi_bench.tree_sha256(
                run_quality_judge.run_pi_bench.SKILL_DIR
            )
        )
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            source = directory / "source"
            source.mkdir()
            (source / "results.json").write_text(json.dumps(source_results))
            with (
                mock.patch.object(run_quality_judge, "validate_source_evidence"),
                mock.patch.object(
                    run_quality_judge,
                    "iter_judge_cells",
                    return_value=iter(cells),
                ),
                mock.patch.object(
                    run_quality_judge,
                    "load_source_pair",
                    return_value=(
                        {
                            cells[0]["left_condition"]: "left",
                            cells[0]["right_condition"]: "right",
                        },
                        {
                            cells[0]["left_condition"]: {
                                "semantic_gate_passed": True
                            },
                            cells[0]["right_condition"]: {
                                "semantic_gate_passed": True
                            },
                        },
                    ),
                ),
                mock.patch.object(
                    run_quality_judge,
                    "run_judge_cell",
                    return_value={"action": "completed", "path": "raw"},
                ) as run_cell,
                mock.patch.object(run_quality_judge.time, "sleep") as sleep,
            ):
                run_quality_judge.execute_judging(
                    CONFIG_PATH,
                    MATRIX_PATH,
                    source,
                    directory / "judge",
                    provenance={"judge_config_sha256": "a" * 64},
                    emit=lambda _message: None,
                )

        self.assertEqual(run_cell.call_count, 2)
        self.assertTrue(
            all(call.kwargs["pause"] is sleep for call in run_cell.call_args_list)
        )
        sleep.assert_called_once_with(config["inter_call_delay_seconds"])

    def test_schema_v2_generation_runs_judgments_in_parallel(self):
        matrix, config = schema_v2_design()
        cells = list(run_quality_judge.iter_judge_cells(matrix, config))[:3]
        scenarios = {
            scenario_id: {"task": "task", "source": "source"}
            for scenario_id in matrix["scenario_ids"]
        }
        active = 0
        max_active = 0
        lock = threading.Lock()

        def fake_run_cell(*_args, **_kwargs):
            nonlocal active, max_active
            with lock:
                active += 1
                max_active = max(max_active, active)
            time.sleep(0.03)
            with lock:
                active -= 1
            return {"action": "completed", "path": "raw"}

        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            matrix_path = directory / "matrix.json"
            config_path = directory / "judge.json"
            matrix_path.write_text(json.dumps(matrix))
            config_path.write_text(json.dumps(config))
            source = directory / "source"
            source.mkdir()
            source_results = {
                "schema_version": 1,
                "matrix": {"id": matrix["matrix_id"], "version": matrix["version"]},
                "completeness": {"complete": True},
                "condition_integrity": {"accepted": True},
                "semantic_acceptance": {"accepted": True},
                "procedure_acceptance": {"accepted": True},
                "output_contract_acceptance": {"accepted": True},
                "guard_integrity": {"accepted": True},
                "provenance": {
                    "runner_version": "5",
                    "matrix_sha256": hashlib.sha256(matrix_path.read_bytes()).hexdigest(),
                    "package_commit": "b" * 40,
                    "package_dirty": False,
                    "skill_sha256": run_quality_judge.run_pi_bench.tree_sha256(
                        run_quality_judge.run_pi_bench.SKILL_DIR
                    ),
                    "extension_sha256": run_quality_judge.run_pi_bench.tree_sha256(
                        run_quality_judge.run_pi_bench.ROOT / "extensions"
                    ),
                    "preregistered_judge_config_path": matrix["judge_config_path"],
                    "preregistered_judge_config_sha256": hashlib.sha256(
                        RELEASE_CANDIDATE_CONFIG_PATH.read_bytes()
                    ).hexdigest(),
                    "pi_version": "0.84.1",
                },
            }
            (source / "results.json").write_text(json.dumps(source_results))
            with (
                mock.patch.object(
                    run_quality_judge.run_pi_bench,
                    "load_matrix_scenarios",
                    return_value=({}, scenarios),
                ),
                mock.patch.object(run_quality_judge, "validate_source_evidence"),
                mock.patch.object(
                    run_quality_judge,
                    "validate_preregistered_judge_config",
                ),
                mock.patch.object(
                    run_quality_judge,
                    "iter_judge_cells",
                    side_effect=[iter(cells), iter(())],
                ),
                mock.patch.object(
                    run_quality_judge,
                    "load_source_pair",
                    return_value=(
                        {"baseline": "left", "native-skill": "right"},
                        {
                            "baseline": {"semantic_gate_passed": True},
                            "native-skill": {"semantic_gate_passed": True},
                        },
                    ),
                ),
                mock.patch.object(
                    run_quality_judge,
                    "run_judge_cell",
                    side_effect=fake_run_cell,
                ),
            ):
                run_quality_judge.execute_judging(
                    config_path,
                    matrix_path,
                    source,
                    directory / "judge-results",
                    provenance={
                        "judge_config_sha256": "a" * 64,
                        "package_commit": "b" * 40,
                        "package_dirty": False,
                        "skill_sha256": source_results["provenance"]["skill_sha256"],
                        "extension_sha256": source_results["provenance"]["extension_sha256"],
                    },
                    pause=lambda _seconds: None,
                    emit=lambda _message: None,
                )

        self.assertGreater(max_active, 1)
        self.assertLessEqual(
            max_active,
            config["max_parallel_calls_by_provider"]["github-copilot"],
        )

    def test_cli_converts_provenance_command_failure_to_exit_two(self):
        with mock.patch.object(
            run_quality_judge,
            "execute_judging",
            side_effect=subprocess.CalledProcessError(1, ["git"]),
        ):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    run_quality_judge.main([])

        self.assertEqual(raised.exception.code, 2)

    def test_generation_rejects_dirty_source_provenance_before_calls(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            source = directory / "source"
            source.mkdir()
            (source / "results.json").write_text(
                json.dumps(self.source_results(package_dirty=True))
            )

            with self.assertRaisesRegex(RuntimeError, "clean"):
                run_quality_judge.execute_judging(
                    CONFIG_PATH,
                    MATRIX_PATH,
                    source,
                    directory / "judge",
                    invoke=lambda *_: self.fail("dirty run invoked judge"),
                    provenance={"judge_config_sha256": "a" * 64},
                )


class AuthorityAndInvocationTest(unittest.TestCase):
    def setUp(self):
        self.config = run_quality_judge.load_judge_config(CONFIG_PATH)
        matrix = run_quality_judge.run_pi_bench.load_matrix(MATRIX_PATH)
        self.cell = next(run_quality_judge.iter_judge_cells(matrix, self.config))

    def test_deterministic_failure_overrides_opposite_judge_preference(self):
        assignment = {"A": "baseline", "B": "native-skill"}
        verdict = valid_verdict(self.config)
        verdict["preference"] = "A"

        outcome = run_quality_judge.authoritative_outcome(
            "baseline",
            "native-skill",
            {"semantic_gate_passed": False},
            {"semantic_gate_passed": True},
            verdict,
            assignment,
        )

        self.assertEqual(outcome["winner"], "native-skill")
        self.assertEqual(outcome["basis"], "deterministic-semantic-gate")
        self.assertFalse(outcome["review_required"])
        self.assertEqual(outcome["judge_preference"], "baseline")

    def test_schema_v2_procedure_failure_overrides_judge_preference(self):
        assignment = {"A": "baseline", "B": "native-skill"}
        verdict = valid_verdict(self.config)
        verdict["preference"] = "A"

        outcome = run_quality_judge.authoritative_outcome(
            "baseline",
            "native-skill",
            {
                "semantic_gate_passed": True,
                "deterministic_gate_passed": False,
            },
            {
                "semantic_gate_passed": True,
                "deterministic_gate_passed": True,
            },
            verdict,
            assignment,
        )

        self.assertEqual(outcome["winner"], "native-skill")
        self.assertEqual(outcome["basis"], "deterministic-source-gates")

    def test_blocking_issue_suppresses_preference_when_both_gates_pass(self):
        assignment = {"A": "native-skill", "B": "baseline"}
        verdict = valid_verdict(self.config)
        verdict["preference"] = "A"
        verdict["candidates"]["A"]["blocking_issues"] = [
            {"category": "semantic", "evidence": "Adds guaranteed success."}
        ]

        outcome = run_quality_judge.authoritative_outcome(
            "baseline",
            "native-skill",
            {"semantic_gate_passed": True},
            {"semantic_gate_passed": True},
            verdict,
            assignment,
        )

        self.assertIsNone(outcome["winner"])
        self.assertEqual(outcome["basis"], "judge-blocking-issue")
        self.assertTrue(outcome["review_required"])
        self.assertEqual(outcome["judge_preference"], "native-skill")

    def test_command_uses_cross_provider_judge_with_full_isolation(self):
        prompt = "blind prompt"
        command = run_quality_judge.build_judge_command(
            self.cell, self.config, prompt
        )

        self.assertEqual(
            command[command.index("--provider") + 1],
            self.cell["judge"]["provider"],
        )
        self.assertEqual(
            command[command.index("--model") + 1], self.cell["judge"]["model"]
        )
        self.assertIn("--no-tools", command)
        self.assertIn("--no-skills", command)
        self.assertIn("--no-extensions", command)
        self.assertIn("--no-prompt-templates", command)
        self.assertIn("--no-themes", command)
        self.assertIn("--no-context-files", command)
        self.assertIn("--no-session", command)
        self.assertIn("--no-approve", command)
        self.assertIn("--offline", command)
        self.assertEqual(command[-1], prompt)


class HybridSemanticJudgeTest(unittest.TestCase):
    def test_schema_v3_judges_only_semantic_applicable_scenarios(self):
        matrix, config = schema_v3_design()
        selected = matrix["scenario_ids"][0]
        scenarios = {
            scenario_id: {
                "fixture": {
                    "semantic_review_applicable": scenario_id == selected,
                }
            }
            for scenario_id in matrix["scenario_ids"]
        }
        cells = list(
            run_quality_judge.iter_judge_cells(matrix, config, scenarios)
        )
        self.assertTrue(cells)
        self.assertEqual({cell["scenario_id"] for cell in cells}, {selected})

    def test_schema_v3_config_and_verdict_contract(self):
        matrix, config = schema_v3_design()
        run_quality_judge.validate_judge_matrix(config, matrix)
        verdict = valid_verdict(config)
        self.assertIsNone(run_quality_judge.judge_output_error(verdict, config))

        equivalent_with_issue = copy.deepcopy(verdict)
        equivalent_with_issue["candidates"]["A"]["semantic_fidelity"]["issues"] = [
            {
                "category": "modality",
                "claim_id": "claim-1",
                "source_evidence": "must",
                "candidate_evidence": "should",
                "explanation": "Obligation weakened.",
            }
        ]
        self.assertIn(
            "equivalent semantic fidelity must have no issues",
            run_quality_judge.judge_output_error(equivalent_with_issue, config),
        )

        adverse_without_issue = copy.deepcopy(verdict)
        adverse_without_issue["candidates"]["B"]["semantic_fidelity"]["label"] = "uncertain"
        self.assertIn(
            "adverse semantic fidelity needs issues",
            run_quality_judge.judge_output_error(adverse_without_issue, config),
        )

    def test_adverse_semantic_label_overrides_preference(self):
        _matrix, config = schema_v3_design()
        verdict = valid_verdict(config)
        verdict["preference"] = "A"
        verdict["candidates"]["A"]["semantic_fidelity"] = {
            "label": "not_equivalent",
            "issues": [
                {
                    "category": "actor",
                    "claim_id": "actor-1",
                    "source_evidence": "Operators must approve.",
                    "candidate_evidence": "Approval is required.",
                    "explanation": "Assigned actor omitted.",
                }
            ],
        }
        outcome = run_quality_judge.authoritative_outcome(
            "native-skill",
            "guarded",
            {"objective_gate_passed": True},
            {"objective_gate_passed": True},
            verdict,
            {"A": "native-skill", "B": "guarded"},
        )
        self.assertIsNone(outcome["winner"])
        self.assertEqual(outcome["basis"], "semantic-fidelity-adverse")
        self.assertTrue(outcome["review_required"])

    def test_ungated_baseline_adverse_label_does_not_block_native_preference(self):
        _matrix, config = schema_v3_design()
        verdict = valid_verdict(config)
        verdict["preference"] = "B"
        verdict["candidates"]["A"]["semantic_fidelity"] = {
            "label": "not_equivalent",
            "issues": [{
                "category": "omission",
                "claim_id": "claim-1",
                "source_evidence": "required fact",
                "candidate_evidence": "different text",
                "explanation": "Baseline omitted the fact.",
            }],
        }
        verdict["candidates"]["A"]["blocking_issues"] = [{
            "category": "semantic",
            "evidence": "Baseline omitted the required fact.",
        }]
        outcome = run_quality_judge.authoritative_outcome(
            "baseline",
            "native-skill",
            {"objective_gate_passed": True},
            {"objective_gate_passed": True},
            verdict,
            {"A": "baseline", "B": "native-skill"},
            semantic_gated_conditions={"native-skill", "guarded"},
        )
        self.assertEqual(outcome["winner"], "native-skill")
        self.assertFalse(outcome["review_required"])

    def test_semantic_issue_evidence_must_match_claim_source_and_candidate(self):
        _matrix, config = schema_v3_design()
        scenario = {
            "source": "Operators must approve the change.",
            "fixture": {
                "semantic_review_applicable": True,
                "semantic_claims": [{
                    "id": "approval",
                    "risk": "actor",
                    "proposition": "Operators approve the change.",
                }],
            },
        }
        candidates = {
            "native-skill": "Approval is required.",
            "guarded": "Operators must approve the change.",
        }
        assignment = {"A": "native-skill", "B": "guarded"}
        verdict = valid_verdict(config)
        verdict["candidates"]["A"]["semantic_fidelity"] = {
            "label": "not_equivalent",
            "issues": [{
                "category": "actor",
                "claim_id": "unknown",
                "source_evidence": "Operators must approve the change.",
                "candidate_evidence": "Approval is required.",
                "explanation": "Actor omitted.",
            }],
        }
        self.assertIn(
            "claim_id",
            run_quality_judge.semantic_attestation_evidence_error(
                verdict, config, scenario, candidates, assignment
            ),
        )
        verdict["candidates"]["A"]["semantic_fidelity"]["issues"][0][
            "claim_id"
        ] = "approval"
        verdict["candidates"]["A"]["semantic_fidelity"]["issues"][0][
            "candidate_evidence"
        ] = "invented excerpt"
        self.assertIn(
            "candidate evidence",
            run_quality_judge.semantic_attestation_evidence_error(
                verdict, config, scenario, candidates, assignment
            ),
        )

    def test_all_inapplicable_semantic_set_cannot_pass_vacuously(self):
        matrix, config = schema_v3_design()
        scenarios = {
            scenario_id: {"semantic_review_applicable": False}
            for scenario_id in matrix["scenario_ids"]
        }
        semantic = run_quality_judge.summarize_semantic_attestations(
            [], matrix, config, scenarios
        )
        self.assertEqual(semantic["expected_unique_candidates"], 0)
        self.assertFalse(semantic["accepted"])

    def test_unique_candidate_conflict_and_adverse_observation_fail(self):
        matrix, config = schema_v3_design()
        source_model = matrix["models"][0]
        judge = config["judges_by_source_provider"][source_model["provider"]]
        scenario_id = matrix["scenario_ids"][0]
        documents = []
        for comparison_id, label in (
            ("baseline-vs-native", "equivalent"),
            ("native-vs-guarded", "uncertain"),
        ):
            verdict = valid_verdict(config)
            issue = []
            if label == "uncertain":
                issue = [{
                    "category": "scope",
                    "claim_id": "scope-1",
                    "source_evidence": "all nodes",
                    "candidate_evidence": "nodes",
                    "explanation": "Scope is ambiguous.",
                }]
            verdict["candidates"]["A"]["semantic_fidelity"] = {
                "label": label,
                "issues": issue,
            }
            documents.append({
                "cell": {
                    "source_model": source_model,
                    "judge": judge,
                    "comparison_id": comparison_id,
                    "scenario_id": scenario_id,
                    "source_repetition": 1,
                },
                "blind_assignment": {
                    "A": "native-skill",
                    "B": "baseline" if comparison_id == "baseline-vs-native" else "guarded",
                },
                "verdict": verdict,
            })
        scenarios = {
            scenario_id: {"semantic_review_applicable": True}
        }
        semantic = run_quality_judge.summarize_semantic_attestations(
            documents, matrix, config, scenarios
        )
        self.assertEqual(semantic["expected_unique_candidates"], 2 * len(matrix["models"]) * matrix["repetitions"])
        self.assertEqual(semantic["covered_unique_candidates"], 2)
        self.assertEqual(semantic["uncertain_observations"], 1)
        self.assertEqual(semantic["conflicts"], 1)
        self.assertFalse(semantic["accepted"])


if __name__ == "__main__":
    unittest.main()
