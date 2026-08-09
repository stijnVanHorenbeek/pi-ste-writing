#!/usr/bin/env python3
"""Run reproducible Pi benchmarks for semantic-safe technical writing.

Adapted from AminBlg/SimpleEnglish at commit
59bf6702197a5aadc96d197ea17f290d8d50dcd3.
Copyright (c) 2026 AminBlg.
Licensed under the MIT License; see the repository root LICENSE file.
"""

import argparse
import datetime
import hashlib
import json
import math
import os
import re
import shutil
import statistics
import subprocess
import tempfile
import time
from collections import Counter
from pathlib import Path

import score_fixtures


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_MATRIX_PATH = HERE / "v1-matrix.json"
DEFAULT_CORPUS_PATH = HERE / "fixtures" / "semantic-preservation.json"
DEFAULT_BENCHMARK_SCENARIOS_PATH = HERE / "benchmark-scenarios.json"
DEFAULT_RESULTS_DIR = HERE / "results" / "v1"
RUNNER_VERSION = "4"
CONDITIONS = ("baseline", "native-skill", "direct-prompt")
THINKING_LEVELS = {"off", "minimal", "low", "medium", "high", "xhigh", "max"}
SKILL_DIR = ROOT / "skills" / "clear-technical-writing"
SKILL_PATH = SKILL_DIR / "SKILL.md"


def tree_sha256(directory):
    digest = hashlib.sha256()
    for path in sorted(Path(directory).rglob("*")):
        if (
            not path.is_file()
            or "__pycache__" in path.parts
            or path.suffix in {".pyc", ".pyo"}
        ):
            continue
        relative = path.relative_to(directory).as_posix().encode("utf-8")
        content = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def collect_provenance(matrix_path, run_command=subprocess.run):
    def output(command):
        process = run_command(
            command,
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        return process.stdout.strip()

    return {
        "runner_version": RUNNER_VERSION,
        "matrix_sha256": hashlib.sha256(Path(matrix_path).read_bytes()).hexdigest(),
        "package_commit": output(["git", "rev-parse", "HEAD"]),
        "package_dirty": bool(output(["git", "status", "--porcelain"])),
        "skill_sha256": tree_sha256(SKILL_DIR),
        "pi_version": output(["pi", "--version"]),
    }


def validate_output_contract(contract, context="benchmark"):
    prefix = f"{context} output contract"
    if not isinstance(contract, dict) or contract.get("type") not in {
        "text",
        "json_object",
    }:
        raise ValueError(f"{prefix} type is unsupported")
    if contract["type"] == "text":
        try:
            for pattern in contract.get("forbidden_patterns", []):
                re.compile(pattern)
        except (TypeError, re.error) as error:
            raise ValueError(f"{prefix} regex is invalid: {error}") from error
        return

    required = contract.get("required_keys", [])
    property_types = contract.get("property_types", {})
    property_values = contract.get("property_values", {})
    supported_types = {
        "string",
        "integer",
        "number",
        "boolean",
        "array",
        "object",
        "null",
    }
    if (
        not isinstance(required, list)
        or not all(isinstance(key, str) and key for key in required)
        or len(required) != len(set(required))
        or not isinstance(property_types, dict)
        or not all(isinstance(key, str) and key for key in property_types)
        or not all(
            isinstance(value, str) and value in supported_types
            for value in property_types.values()
        )
        or not isinstance(property_values, dict)
        or not all(isinstance(key, str) and key for key in property_values)
        or not set(property_values).issubset(set(required) | set(property_types))
        or not isinstance(contract.get("additional_properties"), bool)
    ):
        raise ValueError(f"{prefix} JSON schema is invalid")


def validate_matrix(matrix):
    if not isinstance(matrix, dict) or matrix.get("schema_version") != 1:
        raise ValueError("matrix schema_version must be 1")
    if not isinstance(matrix.get("version"), int) or matrix["version"] < 1:
        raise ValueError("matrix version must be a positive integer")
    amendments = matrix.get("amendments")
    if (
        not isinstance(amendments, list)
        or not all(isinstance(item, dict) for item in amendments)
        or [item.get("version") for item in amendments]
        != list(range(1, matrix["version"] + 1))
        or any(
            not isinstance(item.get("reason"), str)
            or not item["reason"].strip()
            for item in amendments
        )
    ):
        raise ValueError(
            "matrix amendment history must be contiguous and state reasons"
        )

    conditions = matrix.get("conditions")
    if conditions != list(CONDITIONS):
        raise ValueError(
            "matrix conditions must be baseline, native-skill, and direct-prompt"
        )
    scenarios = matrix.get("scenario_ids")
    if (
        not isinstance(scenarios, list)
        or not scenarios
        or not all(isinstance(item, str) and item for item in scenarios)
        or len(scenarios) != len(set(scenarios))
    ):
        raise ValueError("matrix scenario IDs must be unique nonempty strings")

    models = matrix.get("models")
    if not isinstance(models, list) or not models:
        raise ValueError("matrix models must be nonempty")
    model_keys = []
    for model in models:
        if not isinstance(model, dict) or not all(
            isinstance(model.get(key), str) and model[key]
            for key in ("provider", "model", "thinking")
        ):
            raise ValueError("each matrix model needs provider, model, and thinking")
        if model["thinking"] not in THINKING_LEVELS:
            raise ValueError(f"unsupported matrix thinking level: {model['thinking']}")
        model_keys.append(
            (model["provider"], model["model"], model["thinking"])
        )
    if len(model_keys) != len(set(model_keys)):
        raise ValueError("matrix model specifications must be unique")

    if not isinstance(matrix.get("repetitions"), int) or matrix["repetitions"] < 3:
        raise ValueError("benchmark matrix requires at least 3 repetitions")
    if not isinstance(matrix.get("retry_limit"), int) or matrix["retry_limit"] < 1:
        raise ValueError("matrix retry_limit must be at least 1")
    if not isinstance(matrix.get("timeout_seconds"), (int, float)) or matrix["timeout_seconds"] <= 0:
        raise ValueError("matrix timeout_seconds must be positive")
    delay = matrix.get("inter_call_delay_seconds")
    if not isinstance(delay, (int, float)) or delay < 0:
        raise ValueError("matrix inter_call_delay_seconds must be nonnegative")
    if not isinstance(matrix.get("system_prompt"), str) or not matrix["system_prompt"].strip():
        raise ValueError("matrix system_prompt must be nonempty")

    gate_conditions = matrix.get("semantic_gate_conditions")
    if (
        not isinstance(gate_conditions, list)
        or not gate_conditions
        or not all(isinstance(item, str) for item in gate_conditions)
        or len(gate_conditions) != len(set(gate_conditions))
        or not set(gate_conditions).issubset(conditions)
    ):
        raise ValueError("matrix semantic gate conditions must be unique conditions")

    isolation = matrix.get("isolation")
    if not isinstance(isolation, dict) or isolation.get("skills") != "explicit-only":
        raise ValueError("matrix isolation skills must be explicit-only")
    boolean_isolation = (
        "extensions",
        "prompt_templates",
        "themes",
        "context_files",
        "session_persistence",
        "project_trust",
        "startup_network",
    )
    if any(not isinstance(isolation.get(key), bool) for key in boolean_isolation):
        raise ValueError("matrix isolation resource values must be boolean")
    tools = isolation.get("tools_by_condition")
    if not isinstance(tools, dict) or set(tools) != set(conditions):
        raise ValueError("matrix tools_by_condition must cover every condition")
    if any(
        not isinstance(value, list)
        or not all(isinstance(tool, str) and tool for tool in value)
        or len(value) != len(set(value))
        for value in tools.values()
    ):
        raise ValueError("matrix tools_by_condition values must be unique tool lists")

    validate_output_contract(matrix.get("output_contract"), context="matrix")
    for key in ("corpus_path", "benchmark_scenarios_path"):
        value = matrix.get(key)
        if value is not None and (
            not isinstance(value, str)
            or not value.strip()
            or Path(value).is_absolute()
        ):
            raise ValueError(f"matrix {key} must be a nonempty relative path")


def load_matrix(path=DEFAULT_MATRIX_PATH):
    matrix = strict_json_loads(Path(path).read_text(encoding="utf-8"))
    validate_matrix(matrix)
    return matrix


def load_fixtures(path=DEFAULT_CORPUS_PATH):
    corpus = strict_json_loads(Path(path).read_text(encoding="utf-8"))
    return {fixture["id"]: fixture for fixture in corpus["fixtures"]}


def matrix_data_path(matrix, key, default):
    value = matrix.get(key)
    if value is None:
        return Path(default)
    path = (HERE / value).resolve()
    if not path.is_relative_to(HERE):
        raise ValueError(f"matrix {key} must stay within evals")
    return path


def load_matrix_scenarios(matrix):
    fixtures = load_fixtures(
        matrix_data_path(matrix, "corpus_path", DEFAULT_CORPUS_PATH)
    )
    scenarios = load_scenarios(
        fixtures,
        matrix_data_path(
            matrix,
            "benchmark_scenarios_path",
            DEFAULT_BENCHMARK_SCENARIOS_PATH,
        ),
    )
    return fixtures, scenarios


def load_scenarios(
    fixtures,
    path=DEFAULT_BENCHMARK_SCENARIOS_PATH,
):
    scenarios = {
        fixture_id: {
            "id": fixture_id,
            "mode": fixture["mode"],
            "task": fixture["task"],
            "source": fixture["source"],
            "fixture": fixture,
            "expect_skill_loaded": True,
        }
        for fixture_id, fixture in fixtures.items()
    }
    data = strict_json_loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(
        data.get("scenarios"), list
    ):
        raise ValueError("benchmark scenario schema is invalid")
    for scenario in data["scenarios"]:
        if not isinstance(scenario, dict) or not all(
            isinstance(scenario.get(key), str) and scenario[key]
            for key in ("id", "task", "source", "mode")
        ):
            raise ValueError("benchmark scenario fields are invalid")
        if scenario["id"] in scenarios:
            raise ValueError(f"duplicate benchmark scenario: {scenario['id']}")
        if not isinstance(scenario.get("expect_skill_loaded"), bool):
            raise ValueError("benchmark scenario skill expectation is invalid")
        validate_output_contract(
            scenario.get("output_contract"),
            context=f"scenario {scenario['id']}",
        )
        scenarios[scenario["id"]] = scenario
    return scenarios


def iter_cells(matrix, fixtures):
    for scenario_id in matrix["scenario_ids"]:
        if scenario_id not in fixtures:
            raise ValueError(f"unknown matrix scenario: {scenario_id}")
    for model in matrix["models"]:
        for condition in matrix["conditions"]:
            for scenario_id in matrix["scenario_ids"]:
                for repetition in range(1, matrix["repetitions"] + 1):
                    yield {
                        "provider": model["provider"],
                        "model": model["model"],
                        "thinking": model["thinking"],
                        "condition": condition,
                        "scenario_id": scenario_id,
                        "repetition": repetition,
                    }


def measured(value, **metadata):
    return {"value": value, "available": value is not None, **metadata}


def sum_usage(messages, key):
    values = []
    for message in messages:
        usage = message.get("usage")
        value = usage.get(key) if isinstance(usage, dict) else None
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            or value < 0
        ):
            return None
        values.append(value)
    return sum(values) if values else None


def parse_pi_json_events(stdout, skill_path=SKILL_PATH):
    assistant_messages = []
    pending_reads = {}
    tool_calls = 0
    non_read_tool_calls = 0
    read_calls = 0
    successful_read_calls = 0
    failed_read_calls = 0
    skill_entrypoint_read_calls = 0
    skill_tree_read_calls = 0
    outside_skill_read_calls = 0
    resolved_skill_path = Path(skill_path).resolve()
    resolved_skill_root = resolved_skill_path.parent
    for line_number, line in enumerate(stdout.splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = strict_json_loads(line)
        except (json.JSONDecodeError, ValueError) as error:
            raise RuntimeError(
                f"Pi returned invalid JSON on output line {line_number}: {error}"
            ) from error
        if not isinstance(event, dict):
            raise RuntimeError(
                f"Pi returned a non-object JSON event on output line {line_number}"
            )
        message = event.get("message")
        if event.get("type") == "message_end":
            if not isinstance(message, dict):
                raise RuntimeError(
                    f"Pi returned invalid message on output line {line_number}"
                )
            if message.get("role") == "assistant":
                assistant_messages.append(message)
        if event.get("type") == "tool_execution_start":
            tool_calls += 1
            if event.get("toolName") == "read":
                args = event.get("args")
                path = args.get("path") if isinstance(args, dict) else None
                pending_reads[event.get("toolCallId")] = path
            else:
                non_read_tool_calls += 1
        if event.get("type") == "tool_execution_end" and event.get("toolName") == "read":
            read_calls += 1
            path = pending_reads.pop(event.get("toolCallId"), None)
            if event.get("isError") is not False:
                failed_read_calls += 1
                continue
            successful_read_calls += 1
            try:
                resolved_path = Path(path).resolve() if path else None
            except (OSError, RuntimeError, TypeError):
                resolved_path = None
            if resolved_path is None or not resolved_path.is_relative_to(
                resolved_skill_root
            ):
                outside_skill_read_calls += 1
                continue
            skill_tree_read_calls += 1
            if resolved_path == resolved_skill_path:
                skill_entrypoint_read_calls += 1

    final_message = assistant_messages[-1] if assistant_messages else None
    final_content = final_message.get("content") if final_message else None
    if final_message is None or not isinstance(final_content, list) or not any(
        isinstance(part, dict)
        and part.get("type") == "text"
        and isinstance(part.get("text"), str)
        and part["text"].strip()
        for part in final_content
    ):
        raise RuntimeError("Pi benchmark call returned no final assistant text")

    text = "".join(
        part.get("text", "")
        for part in final_content
        if isinstance(part, dict) and part.get("type") == "text"
    )
    input_tokens = sum_usage(assistant_messages, "input")
    output_tokens = sum_usage(assistant_messages, "output")
    reasoning_tokens = sum_usage(assistant_messages, "reasoning")
    visible_output_tokens = None
    if output_tokens is not None and reasoning_tokens is not None:
        visible_output_tokens = output_tokens - reasoning_tokens
    cost_values = []
    for message in assistant_messages:
        usage = message.get("usage")
        cost = usage.get("cost") if isinstance(usage, dict) else None
        value = cost.get("total") if isinstance(cost, dict) else None
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            or value < 0
        ):
            cost_values = []
            break
        cost_values.append(value)
    cost_usd = round(sum(cost_values), 12) if cost_values else None

    return {
        "text": text,
        "provider": final_message.get("provider"),
        "model": final_message.get("model"),
        "response_model": final_message.get("responseModel"),
        "stop_reason": final_message.get("stopReason"),
        "usage": {
            "input_tokens": measured(input_tokens),
            "output_tokens": measured(
                output_tokens,
                includes_reasoning=True,
            ),
            "reasoning_tokens": measured(reasoning_tokens),
            "visible_output_tokens": measured(
                visible_output_tokens,
                derived=True,
            ),
            "cache_read_tokens": measured(
                sum_usage(assistant_messages, "cacheRead")
            ),
            "cache_write_tokens": measured(
                sum_usage(assistant_messages, "cacheWrite")
            ),
            "total_tokens": measured(
                sum_usage(assistant_messages, "totalTokens")
            ),
        },
        "cost_usd": measured(cost_usd),
        "routing": {
            "tool_calls": tool_calls,
            "non_read_tool_calls": non_read_tool_calls,
            "read_calls": read_calls,
            "successful_read_calls": successful_read_calls,
            "failed_read_calls": failed_read_calls,
            "skill_entrypoint_read_calls": skill_entrypoint_read_calls,
            "skill_tree_read_calls": skill_tree_read_calls,
            "outside_skill_read_calls": outside_skill_read_calls,
            "skill_loaded": skill_entrypoint_read_calls > 0,
        },
    }


def json_type_matches(value, expected_type):
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "null":
        return value is None
    raise ValueError(f"unsupported JSON property type: {expected_type}")


def unique_json_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate object key {key!r}")
        value[key] = item
    return value


def strict_json_loads(text):
    return json.loads(
        text,
        object_pairs_hook=unique_json_object,
        parse_constant=lambda constant: (_ for _ in ()).throw(
            ValueError(f"nonstandard constant {constant}")
        ),
    )


def evaluate_output_contract(text, contract):
    contract_type = contract["type"]
    violations = []
    if contract_type == "text":
        if not text.strip():
            violations.append({"rule": "nonempty-text", "message": "Output is empty."})
        for pattern in contract.get("forbidden_patterns", []):
            if re.search(pattern, text):
                violations.append(
                    {
                        "rule": "forbidden-pattern",
                        "message": "Output contains forbidden framing text.",
                        "pattern": pattern,
                    }
                )
    elif contract_type == "json_object":
        parsed = True
        try:
            value = strict_json_loads(text)
        except (json.JSONDecodeError, ValueError) as error:
            detail = error.msg if isinstance(error, json.JSONDecodeError) else str(error)
            violations.append(
                {
                    "rule": "valid-json",
                    "message": f"Output is not valid JSON: {detail}.",
                }
            )
            parsed = False
            value = None
        if parsed and not isinstance(value, dict):
            violations.append(
                {"rule": "object-root", "message": "JSON root is not an object."}
            )
        if isinstance(value, dict):
            required = set(contract.get("required_keys", []))
            missing = sorted(required - set(value))
            if missing:
                violations.append(
                    {
                        "rule": "required-keys",
                        "message": "JSON object is missing required keys.",
                        "keys": missing,
                    }
                )
            if contract.get("additional_properties") is False:
                allowed = set(contract.get("property_types", {})) | required
                extra = sorted(set(value) - allowed)
                if extra:
                    violations.append(
                        {
                            "rule": "additional-properties",
                            "message": "JSON object contains additional properties.",
                            "keys": extra,
                        }
                    )
            for key, expected_type in contract.get("property_types", {}).items():
                if key in value and not json_type_matches(value[key], expected_type):
                    violations.append(
                        {
                            "rule": "property-type",
                            "message": f"JSON property {key!r} has the wrong type.",
                            "key": key,
                            "expected": expected_type,
                        }
                    )
            for key, expected_value in contract.get("property_values", {}).items():
                if key in value and value[key] != expected_value:
                    violations.append(
                        {
                            "rule": "property-value",
                            "message": f"JSON property {key!r} has the wrong value.",
                            "key": key,
                            "expected": expected_value,
                        }
                    )
    else:
        raise ValueError(f"unsupported output contract: {contract_type}")
    return {
        "type": contract_type,
        "passed": not violations,
        "violations": violations,
    }


def evaluate_candidate(fixture, text, output_contract, candidate):
    score = score_fixtures.score_rewrite(fixture, text, candidate)
    contract = evaluate_output_contract(text, output_contract)
    return {
        "semantic": score["semantic"],
        "procedure": score["procedure"],
        "output_contract": contract,
        "semantic_gate_passed": (
            score["semantic"]["gate_passed"] and contract["passed"]
        ),
        "style": score["style"],
        "disclaimer": score["disclaimer"],
    }


def evaluate_scenario(scenario, text, default_contract, candidate):
    fixture = (
        scenario
        if "invariants" in scenario
        else scenario.get("fixture")
    )
    contract = scenario.get("output_contract", default_contract)
    if fixture is not None:
        return evaluate_candidate(fixture, text, contract, candidate)

    metric_names = (
        "protected_span_equality",
        "required_fact_retention",
        "forbidden_fact_invention",
        "modality_and_certainty_preservation",
        "repository_term_preservation",
    )
    output_contract = evaluate_output_contract(text, contract)
    return {
        "semantic": {
            "gate_passed": True,
            "failed_rule_ids": [],
            "metrics": {
                name: score_fixtures.empty_metric() for name in metric_names
            },
        },
        "procedure": {
            "applicable": False,
            "passed": None,
            "required_rules": score_fixtures.empty_metric(),
            "warning_count": 0,
            "warnings": [],
        },
        "output_contract": output_contract,
        "semantic_gate_passed": output_contract["passed"],
        "style": {
            "advisory": True,
            "warning_count": 0,
            "warnings_by_rule": {},
            "findings": [],
        },
        "disclaimer": score_fixtures.DISCLAIMER,
    }


def invoke_pi(
    command,
    timeout_seconds,
    run_command=subprocess.run,
    monotonic=time.monotonic,
):
    environment = os.environ.copy()
    environment.update(PI_TELEMETRY="0", PI_SKIP_VERSION_CHECK="1")
    started = monotonic()
    with tempfile.TemporaryDirectory(prefix="pi-ste-bench-") as directory:
        try:
            process = run_command(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                cwd=directory,
                env=environment,
            )
        except subprocess.TimeoutExpired:
            return {
                "status": "failure",
                "duration_ms": round(1000 * (monotonic() - started)),
                "error": {
                    "kind": "timeout",
                    "message": f"Pi call exceeded {timeout_seconds} seconds.",
                },
            }
        except OSError as error:
            return {
                "status": "failure",
                "duration_ms": round(1000 * (monotonic() - started)),
                "error": {"kind": "process", "message": str(error)},
            }
    duration_ms = round(1000 * (monotonic() - started))
    skill_path = SKILL_PATH
    if "--skill" in command:
        skill_path = Path(command[command.index("--skill") + 1]) / "SKILL.md"
    if process.returncode != 0:
        detail = process.stderr.strip()[:2000]
        failure = {
            "status": "failure",
            "duration_ms": duration_ms,
            "error": {
                "kind": "process",
                "message": f"Pi exited with exit {process.returncode}: {detail}",
            },
        }
        try:
            failure["partial_response"] = parse_pi_json_events(
                process.stdout,
                skill_path=skill_path,
            )
        except RuntimeError:
            pass
        return failure
    try:
        response = parse_pi_json_events(process.stdout, skill_path=skill_path)
    except RuntimeError as error:
        return {
            "status": "failure",
            "duration_ms": duration_ms,
            "error": {"kind": "output", "message": str(error)},
        }
    if error := response_error(response, "Pi response"):
        return {
            "status": "failure",
            "duration_ms": duration_ms,
            "error": {"kind": "output", "message": error},
        }
    if response["stop_reason"] != "stop":
        return {
            "status": "failure",
            "duration_ms": duration_ms,
            "error": {
                "kind": "stop-reason",
                "message": f"Pi stopped with {response['stop_reason']!r}.",
            },
            "partial_response": response,
        }
    return {
        "status": "success",
        "duration_ms": duration_ms,
        "response": response,
    }


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write_json_atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(value, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(path)


def measurement_error(measurement, name):
    metadata = {}
    if name == "output_tokens":
        metadata = {"includes_reasoning": True}
    elif name == "visible_output_tokens":
        metadata = {"derived": True}
    expected_keys = {"value", "available", *metadata}
    if not isinstance(measurement, dict) or set(measurement) != expected_keys:
        return f"{name} measurement fields are invalid"
    if not isinstance(measurement.get("available"), bool):
        return f"{name} availability is invalid"
    if any(measurement.get(key) is not value for key, value in metadata.items()):
        return f"{name} metadata is invalid"
    if "value" not in measurement:
        return f"{name} value is missing"
    value = measurement["value"]
    if measurement["available"]:
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            or value < 0
            or (name.endswith("_tokens") and not isinstance(value, int))
        ):
            return f"{name} value is invalid"
    elif value is not None:
        return f"{name} unavailable value must be null"
    return None


def metric_error(metric, name):
    if not isinstance(metric, dict):
        return f"metric {name} must be an object"
    applicable = metric.get("applicable")
    passed = metric.get("passed")
    if not isinstance(applicable, bool):
        return f"metric {name} applicable is invalid"
    if passed is not None and not isinstance(passed, bool):
        return f"metric {name} passed is invalid"
    if applicable and passed is None:
        return f"metric {name} applicable result needs pass state"
    for key in ("rules_total", "rules_passed", "rules_failed"):
        value = metric.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            return f"metric {name} {key} is invalid"
    if metric["rules_passed"] + metric["rules_failed"] != metric["rules_total"]:
        return f"metric {name} rule counts are inconsistent"
    pass_rate = metric.get("pass_rate")
    if pass_rate is not None and (
        not isinstance(pass_rate, (int, float))
        or isinstance(pass_rate, bool)
        or not math.isfinite(pass_rate)
        or not 0 <= pass_rate <= 1
    ):
        return f"metric {name} pass_rate is invalid"
    if not isinstance(metric.get("failures"), list):
        return f"metric {name} failures must be an array"
    return None


def evaluation_error(evaluation):
    if not isinstance(evaluation, dict):
        return "evaluation must be an object"
    semantic = evaluation.get("semantic")
    procedure = evaluation.get("procedure")
    contract = evaluation.get("output_contract")
    style = evaluation.get("style")
    if (
        not isinstance(evaluation.get("semantic_gate_passed"), bool)
        or not isinstance(semantic, dict)
        or not isinstance(semantic.get("gate_passed"), bool)
        or not isinstance(semantic.get("failed_rule_ids"), list)
        or not all(
            isinstance(rule_id, str) for rule_id in semantic["failed_rule_ids"]
        )
        or not isinstance(semantic.get("metrics"), dict)
    ):
        return "semantic evaluation is invalid"
    expected_metrics = {
        "protected_span_equality",
        "required_fact_retention",
        "forbidden_fact_invention",
        "modality_and_certainty_preservation",
        "repository_term_preservation",
    }
    if set(semantic["metrics"]) != expected_metrics:
        return "semantic metric set is invalid"
    for name, metric in semantic["metrics"].items():
        if error := metric_error(metric, name):
            return error
    if not isinstance(procedure, dict) or not isinstance(
        procedure.get("applicable"), bool
    ):
        return "procedure evaluation is invalid"
    if procedure.get("passed") is not None and not isinstance(
        procedure["passed"], bool
    ):
        return "procedure pass state is invalid"
    if error := metric_error(procedure.get("required_rules"), "procedure"):
        return error
    if (
        not isinstance(procedure.get("warning_count"), int)
        or isinstance(procedure.get("warning_count"), bool)
        or procedure["warning_count"] < 0
        or not isinstance(procedure.get("warnings"), list)
    ):
        return "procedure warnings are invalid"
    if (
        not isinstance(contract, dict)
        or not isinstance(contract.get("type"), str)
        or not isinstance(contract.get("passed"), bool)
        or not isinstance(contract.get("violations"), list)
    ):
        return "output contract evaluation is invalid"
    if (
        not isinstance(style, dict)
        or style.get("advisory") is not True
        or not isinstance(style.get("warning_count"), int)
        or isinstance(style.get("warning_count"), bool)
        or style["warning_count"] < 0
        or not isinstance(style.get("warnings_by_rule"), dict)
        or not all(
            isinstance(rule, str)
            and isinstance(count, int)
            and not isinstance(count, bool)
            and count >= 0
            for rule, count in style["warnings_by_rule"].items()
        )
        or not isinstance(style.get("findings"), list)
    ):
        return "style evaluation is invalid"
    if not isinstance(evaluation.get("disclaimer"), str):
        return "evaluation disclaimer is invalid"
    return None


def response_error(response, name, require_stop=False):
    expected_keys = {
        "text",
        "provider",
        "model",
        "response_model",
        "stop_reason",
        "usage",
        "cost_usd",
        "routing",
    }
    if not isinstance(response, dict) or set(response) != expected_keys:
        return f"{name} fields are invalid"
    for key in ("text", "provider", "model", "stop_reason"):
        if not isinstance(response.get(key), str) or not response[key]:
            return f"{name} {key} must be nonempty text"
    if require_stop and response["stop_reason"] != "stop":
        return f"{name} stop_reason must be stop"
    if response.get("response_model") is not None and (
        not isinstance(response["response_model"], str)
        or not response["response_model"]
    ):
        return f"{name} response_model is invalid"
    if not all(
        isinstance(response.get(key), dict)
        for key in ("usage", "cost_usd", "routing")
    ):
        return f"{name} measurements are incomplete"
    usage = response["usage"]
    measurement_names = (
        "input_tokens",
        "output_tokens",
        "reasoning_tokens",
        "visible_output_tokens",
        "cache_read_tokens",
        "cache_write_tokens",
        "total_tokens",
    )
    if set(usage) != set(measurement_names):
        return f"{name} usage fields are invalid"
    for measurement_name in measurement_names:
        if error := measurement_error(
            usage.get(measurement_name),
            measurement_name,
        ):
            return error
    if error := measurement_error(response["cost_usd"], "cost_usd"):
        return error
    routing = response["routing"]
    if set(routing) != {
        "tool_calls",
        "non_read_tool_calls",
        "read_calls",
        "successful_read_calls",
        "failed_read_calls",
        "skill_entrypoint_read_calls",
        "skill_tree_read_calls",
        "outside_skill_read_calls",
        "skill_loaded",
    }:
        return f"{name} routing fields are invalid"
    if (
        not isinstance(routing.get("tool_calls"), int)
        or isinstance(routing.get("tool_calls"), bool)
        or routing["tool_calls"] < 0
        or not isinstance(routing.get("non_read_tool_calls"), int)
        or isinstance(routing.get("non_read_tool_calls"), bool)
        or routing["non_read_tool_calls"] < 0
        or not isinstance(routing.get("read_calls"), int)
        or isinstance(routing.get("read_calls"), bool)
        or routing["read_calls"] < 0
        or routing["tool_calls"]
        != routing["read_calls"] + routing["non_read_tool_calls"]
        or any(
            not isinstance(routing.get(key), int)
            or isinstance(routing.get(key), bool)
            or routing[key] < 0
            for key in (
                "successful_read_calls",
                "failed_read_calls",
                "skill_entrypoint_read_calls",
                "skill_tree_read_calls",
                "outside_skill_read_calls",
            )
        )
        or routing["read_calls"]
        != routing["successful_read_calls"] + routing["failed_read_calls"]
        or routing["successful_read_calls"]
        != routing["skill_tree_read_calls"] + routing["outside_skill_read_calls"]
        or routing["skill_entrypoint_read_calls"] > routing["skill_tree_read_calls"]
        or not isinstance(routing.get("skill_loaded"), bool)
        or routing["skill_loaded"]
        != (routing["skill_entrypoint_read_calls"] > 0)
    ):
        return f"{name} routing is invalid"
    return None


def attempt_error(attempt, index):
    if not isinstance(attempt, dict):
        return f"attempt {index} must be an object"
    if (
        not isinstance(attempt.get("number"), int)
        or isinstance(attempt.get("number"), bool)
        or attempt["number"] < 1
        or not isinstance(attempt.get("started_at"), str)
        or not attempt["started_at"]
        or not isinstance(attempt.get("duration_ms"), (int, float))
        or isinstance(attempt.get("duration_ms"), bool)
        or not math.isfinite(attempt["duration_ms"])
        or attempt["duration_ms"] < 0
        or attempt.get("status") not in {"success", "failure"}
    ):
        return f"attempt {index} fields are invalid"
    expected_keys = {"number", "started_at", "status", "duration_ms"}
    if attempt["status"] == "failure":
        expected_keys.add("error")
        if "partial_response" in attempt or "partial_evaluation" in attempt:
            expected_keys.update(("partial_response", "partial_evaluation"))
    if set(attempt) != expected_keys:
        return f"attempt {index} fields are invalid for its status"
    if attempt["status"] == "failure":
        error = attempt.get("error")
        if (
            not isinstance(error, dict)
            or set(error) != {"kind", "message"}
            or not isinstance(error.get("kind"), str)
            or not error["kind"]
            or not isinstance(error.get("message"), str)
            or not error["message"]
        ):
            return f"attempt {index} error is invalid"
    partial_response = attempt.get("partial_response")
    partial_evaluation = attempt.get("partial_evaluation")
    if (partial_response is None) != (partial_evaluation is None):
        return f"attempt {index} partial evidence is incomplete"
    if partial_response is not None:
        if error := response_error(
            partial_response,
            f"attempt {index} partial response",
        ):
            return error
        if error := evaluation_error(partial_evaluation):
            return f"attempt {index} partial {error}"
    return None


def routing_safety_passed(cell, response):
    routing = response.get("routing", {})
    if cell["condition"] == "native-skill":
        return (
            routing.get("non_read_tool_calls") == 0
            and routing.get("failed_read_calls") == 0
            and routing.get("outside_skill_read_calls") == 0
            and routing.get("successful_read_calls")
            == routing.get("skill_tree_read_calls")
        )
    return (
        routing.get("tool_calls") == 0
        and routing.get("non_read_tool_calls") == 0
        and routing.get("read_calls") == 0
        and routing.get("successful_read_calls") == 0
        and routing.get("failed_read_calls") == 0
        and routing.get("skill_entrypoint_read_calls") == 0
        and routing.get("skill_tree_read_calls") == 0
        and routing.get("outside_skill_read_calls") == 0
        and routing.get("skill_loaded") is False
    )


def expected_condition_integrity(cell, scenario, response):
    expected_skill_loaded = (
        cell["condition"] == "native-skill"
        and scenario.get("expect_skill_loaded", True)
    )
    response_model = response.get("response_model")
    model_identity_passed = (
        response.get("provider") == cell["provider"]
        and response.get("model") == cell["model"]
        and (response_model is None or response_model == cell["model"])
    )
    routing = response.get("routing", {})
    skill_loading_passed = routing_safety_passed(cell, response) and (
        routing.get("skill_loaded") == expected_skill_loaded
        if cell["condition"] == "native-skill"
        else True
    )
    return {
        "model_identity_passed": model_identity_passed,
        "expected_skill_loaded": expected_skill_loaded,
        "skill_loading_passed": skill_loading_passed,
        "passed": model_identity_passed and skill_loading_passed,
    }


def expected_prompt_sha256(cell, matrix, scenario, skill_text):
    task_input = build_task_input(scenario)
    prompt = build_condition_prompt(task_input, cell["condition"], skill_text)
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def raw_evidence_error(
    document,
    cell,
    matrix,
    scenario,
    skill_text,
):
    expected_prompt = expected_prompt_sha256(
        cell,
        matrix,
        scenario,
        skill_text,
    )
    if document.get("prompt_sha256") != expected_prompt:
        return "prompt_sha256 does not match benchmark input"
    for attempt in document["attempts"]:
        response = attempt.get("partial_response")
        if response is None:
            continue
        expected_evaluation = evaluate_scenario(
            scenario,
            response["text"],
            matrix["output_contract"],
            raw_result_name(cell),
        )
        if attempt.get("partial_evaluation") != expected_evaluation:
            return "partial evaluation does not match completed output"
    if document["status"] != "success":
        return None
    response = document["response"]
    expected_evaluation = evaluate_scenario(
        scenario,
        response["text"],
        matrix["output_contract"],
        raw_result_name(cell),
    )
    if document.get("evaluation") != expected_evaluation:
        return "evaluation does not match completed output"
    if document.get("condition_integrity") != expected_condition_integrity(
        cell,
        scenario,
        response,
    ):
        return "condition integrity does not match response evidence"
    return None


def raw_document_error(document):
    if not isinstance(document, dict):
        return "root must be an object"
    if document.get("schema_version") != 1:
        return "schema_version must be 1"
    if document.get("status") not in {"success", "failure"}:
        return "status must be success or failure"
    common_keys = {
        "schema_version",
        "status",
        "cell",
        "provenance",
        "prompt_sha256",
        "attempts",
        "updated_at",
    }
    status_keys = (
        {"last_error"}
        if document["status"] == "failure"
        else {"duration_ms", "response", "condition_integrity", "evaluation"}
    )
    allowed_keys = common_keys | status_keys
    if not set(document) <= allowed_keys:
        return "document contains unexpected fields"
    if not isinstance(document.get("cell"), dict):
        return "cell must be an object"
    if not isinstance(document.get("provenance"), dict):
        return "provenance must be an object"
    attempts = document.get("attempts")
    if not isinstance(attempts, list) or not attempts:
        return "attempts must be a nonempty array"
    for index, attempt in enumerate(attempts, 1):
        if error := attempt_error(attempt, index):
            return error
        if attempt["number"] != index:
            return "attempt numbers must be contiguous"
        if index < len(attempts) and attempt["status"] != "failure":
            return "only final attempt may be successful"
    if document["status"] == "failure":
        if attempts[-1]["status"] != "failure":
            return "failed document needs a final failed attempt"
        last_error = document.get("last_error")
        if (
            not isinstance(last_error, dict)
            or set(last_error) != {"kind", "message"}
            or not isinstance(last_error.get("kind"), str)
            or not last_error["kind"]
            or not isinstance(last_error.get("message"), str)
            or not last_error["message"]
        ):
            return "failed last_error is invalid"
        if last_error != attempts[-1].get("error"):
            return "failed last_error does not match final attempt"
        return None
    if attempts[-1]["status"] != "success":
        return "successful document needs a final successful attempt"

    response = document.get("response")
    evaluation = document.get("evaluation")
    integrity = document.get("condition_integrity")
    duration_ms = document.get("duration_ms")
    if (
        not isinstance(duration_ms, (int, float))
        or isinstance(duration_ms, bool)
        or not math.isfinite(duration_ms)
        or duration_ms < 0
    ):
        return "successful duration_ms must be nonnegative and finite"
    if duration_ms != attempts[-1]["duration_ms"]:
        return "successful duration_ms does not match final attempt"
    if error := response_error(
        response,
        "successful response",
        require_stop=True,
    ):
        return error
    if "last_error" in document:
        return "successful document contains last_error"
    if error := evaluation_error(evaluation):
        return error
    integrity_fields = (
        "model_identity_passed",
        "expected_skill_loaded",
        "skill_loading_passed",
        "passed",
    )
    if not isinstance(integrity, dict) or not all(
        isinstance(integrity.get(key), bool) for key in integrity_fields
    ):
        return "successful condition_integrity is incomplete"
    if integrity["passed"] != (
        integrity["model_identity_passed"]
        and integrity["skill_loading_passed"]
    ):
        return "successful condition_integrity is inconsistent"
    return None


def run_cell(
    cell,
    matrix,
    fixture,
    skill_text,
    provenance,
    raw_path,
    invoke=None,
    pause=time.sleep,
    now=utc_now,
    skill_dir=SKILL_DIR,
):
    task_input = build_task_input(fixture)
    prompt = build_condition_prompt(task_input, cell["condition"], skill_text)
    prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    attempts = []
    if raw_path.exists():
        try:
            existing = strict_json_loads(raw_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError) as error:
            raise RuntimeError(f"invalid raw result cannot be reused: {raw_path}: {error}") from error
        if error := raw_document_error(existing):
            raise RuntimeError(
                f"invalid raw result cannot be reused: {raw_path}: {error}"
            )
        if existing.get("cell") != cell or existing.get("provenance") != provenance:
            raise RuntimeError(f"stale raw result cannot be reused: {raw_path}")
        if error := raw_evidence_error(
            existing,
            cell,
            matrix,
            fixture,
            skill_text,
        ):
            raise RuntimeError(
                f"invalid raw result cannot be reused: {raw_path}: {error}"
            )
        attempts = list(existing.get("attempts", []))
        if existing.get("status") == "success":
            return {"action": "skipped", "path": str(raw_path)}

    if invoke is None:
        invoke = invoke_pi
    command = build_pi_command(cell, matrix, prompt, skill_dir=skill_dir)
    document = {
        "schema_version": 1,
        "status": "failure",
        "cell": cell,
        "provenance": provenance,
        "prompt_sha256": prompt_sha256,
        "attempts": attempts,
    }
    for attempt_in_run in range(1, matrix["retry_limit"] + 1):
        started_at = now()
        call = invoke(command, matrix["timeout_seconds"])
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
                attempt["partial_evaluation"] = evaluate_scenario(
                    fixture,
                    call["partial_response"]["text"],
                    matrix["output_contract"],
                    raw_result_name(cell),
                )
            document["attempts"].append(attempt)
            document["last_error"] = call["error"]
            document["updated_at"] = now()
            write_json_atomic(raw_path, document)
            if attempt_in_run < matrix["retry_limit"]:
                pause(matrix["inter_call_delay_seconds"])
            continue

        response = call["response"]
        condition_integrity = expected_condition_integrity(
            cell,
            fixture,
            response,
        )
        evaluation = evaluate_scenario(
            fixture,
            response["text"],
            matrix["output_contract"],
            raw_result_name(cell),
        )
        if (
            not condition_integrity["model_identity_passed"]
            or not routing_safety_passed(cell, response)
        ):
            error = {
                "kind": "condition-integrity",
                "message": "Model identity or routing safety did not pass.",
            }
            attempt.update(
                status="failure",
                error=error,
                partial_response=response,
                partial_evaluation=evaluation,
            )
            document["attempts"].append(attempt)
            document["last_error"] = error
            document["updated_at"] = now()
            write_json_atomic(raw_path, document)
            if attempt_in_run < matrix["retry_limit"]:
                pause(matrix["inter_call_delay_seconds"])
            continue

        attempt["status"] = "success"
        document["attempts"].append(attempt)
        document.update(
            status="success",
            updated_at=now(),
            duration_ms=call["duration_ms"],
            response=response,
            condition_integrity=condition_integrity,
            evaluation=evaluation,
        )
        document.pop("last_error", None)
        write_json_atomic(raw_path, document)
        return {"action": "completed", "path": str(raw_path)}
    return {"action": "failed", "path": str(raw_path)}


def build_task_input(fixture):
    contract = fixture.get("output_contract")
    contract_text = ""
    final_instruction = "Return only the requested rewritten text."
    if isinstance(contract, dict) and contract.get("type") == "json_object":
        contract_lines = [
            "Output contract:",
            "- Return one JSON object.",
            "- Required keys: " + json.dumps(contract.get("required_keys", [])),
            "- Property types: "
            + json.dumps(contract.get("property_types", {}), sort_keys=True),
            "- Exact property values: "
            + json.dumps(contract.get("property_values", {}), sort_keys=True),
        ]
        if contract.get("additional_properties") is False:
            contract_lines.append("- No additional properties.")
        contract_text = "\n\n" + "\n".join(contract_lines)
        final_instruction = "Return only the requested JSON object."
    return (
        f"{fixture['task']}\n\n"
        "Source:\n\n"
        f"{fixture['source']}"
        f"{contract_text}\n\n"
        f"{final_instruction}"
    )


def build_condition_prompt(task_input, condition, skill_text):
    if condition in {"baseline", "native-skill"}:
        return task_input
    if condition == "direct-prompt":
        return (
            "Follow these technical-writing instructions for the task below:\n\n"
            f"{skill_text}\n\n"
            "---\n\n"
            f"{task_input}"
        )
    raise ValueError(f"unknown benchmark condition: {condition}")


def build_pi_command(cell, matrix, prompt, skill_dir=SKILL_DIR):
    command = [
        "pi",
        "--print",
        "--mode",
        "json",
        "--provider",
        cell["provider"],
        "--model",
        cell["model"],
        "--thinking",
        cell["thinking"],
        "--system-prompt",
        matrix["system_prompt"],
    ]
    isolation = matrix["isolation"]
    resource_flags = {
        "extensions": "--no-extensions",
        "prompt_templates": "--no-prompt-templates",
        "themes": "--no-themes",
        "context_files": "--no-context-files",
    }
    for setting, flag in resource_flags.items():
        if isolation[setting] is False:
            command.append(flag)

    if isolation["skills"] == "explicit-only":
        command.append("--no-skills")
        if cell["condition"] == "native-skill":
            command.extend(["--skill", str(skill_dir)])

    tools = isolation["tools_by_condition"][cell["condition"]]
    if tools:
        command.extend(["--tools", ",".join(tools)])
    else:
        command.append("--no-tools")
    if isolation["session_persistence"] is False:
        command.append("--no-session")
    if isolation["project_trust"] is False:
        command.append("--no-approve")
    if isolation["startup_network"] is False:
        command.append("--offline")
    command.append(prompt)
    return command


def numeric_summary(rows, value_getter):
    values = [value_getter(row) for row in rows]
    available = [value for value in values if value is not None]
    return {
        "available_runs": len(available),
        "missing_runs": len(values) - len(available),
        "sum": round(sum(available), 12) if available else None,
        "mean": round(statistics.mean(available), 6) if available else None,
        "stddev": (
            round(statistics.pstdev(available), 6) if available else None
        ),
    }


def aggregate_semantic(rows):
    metric_names = (
        "protected_span_equality",
        "required_fact_retention",
        "forbidden_fact_invention",
        "modality_and_certainty_preservation",
        "repository_term_preservation",
    )
    metrics = {}
    for name in metric_names:
        reports = [row["evaluation"]["semantic"]["metrics"][name] for row in rows]
        applicable = [report for report in reports if report["applicable"]]
        total = sum(report["rules_total"] for report in applicable)
        failed = sum(report["rules_failed"] for report in applicable)
        metrics[name] = {
            "applicable_samples": len(applicable),
            "rules_total": total,
            "rules_failed": failed,
            "pass_rate": round((total - failed) / total, 6) if total else None,
        }

    procedure_reports = [row["evaluation"]["procedure"] for row in rows]
    applicable_procedures = [
        report for report in procedure_reports if report["applicable"]
    ]
    output_contracts = [row["evaluation"]["output_contract"] for row in rows]
    return {
        "samples_passed": sum(
            row["evaluation"]["semantic_gate_passed"] for row in rows
        ),
        "samples_failed": sum(
            not row["evaluation"]["semantic_gate_passed"] for row in rows
        ),
        "metrics": metrics,
        "procedure": {
            "applicable_samples": len(applicable_procedures),
            "passed_samples": sum(
                report["passed"] is True for report in applicable_procedures
            ),
            "failed_samples": sum(
                report["passed"] is False for report in applicable_procedures
            ),
        },
        "output_contract": {
            "passed_samples": sum(report["passed"] for report in output_contracts),
            "failed_samples": sum(
                not report["passed"] for report in output_contracts
            ),
        },
    }


def aggregate_style(rows):
    warning_counts = Counter()
    for row in rows:
        warning_counts.update(
            row["evaluation"]["style"]["warnings_by_rule"]
        )
    return {
        "advisory": True,
        "warning_count": sum(warning_counts.values()),
        "warnings_by_rule": dict(sorted(warning_counts.items())),
    }


def measured_value(row, section, name):
    measurement = row["response"][section][name]
    return measurement["value"] if measurement["available"] else None


def aggregate_operations(rows):
    operations = {
        name: numeric_summary(
            rows,
            lambda row, metric=name: measured_value(
                row, "usage", metric
            ),
        )
        for name in (
            "input_tokens",
            "output_tokens",
            "reasoning_tokens",
            "visible_output_tokens",
        )
    }
    operations["cost_usd"] = numeric_summary(
        rows,
        lambda row: (
            row["response"]["cost_usd"]["value"]
            if row["response"]["cost_usd"]["available"]
            else None
        ),
    )
    operations["duration_ms"] = numeric_summary(
        rows, lambda row: row.get("duration_ms")
    )
    native_rows = [
        row for row in rows if row["cell"]["condition"] == "native-skill"
    ]
    operations["routing"] = {
        "applicable_runs": len(native_rows),
        "skill_loaded_runs": sum(
            row["response"]["routing"]["skill_loaded"] for row in native_rows
        ),
    }
    operations["response_models"] = dict(
        sorted(
            Counter(
                row["response"].get("response_model")
                or row["response"].get("model")
                or "unreported"
                for row in rows
            ).items()
        )
    )
    return operations


def aggregate_activation(matrix, fixtures, successes):
    groups = []
    for model in matrix["models"]:
        for scenario_id in matrix["scenario_ids"]:
            rows = [
                row
                for row in successes
                if row["cell"]["provider"] == model["provider"]
                and row["cell"]["model"] == model["model"]
                and row["cell"]["thinking"] == model["thinking"]
                and row["cell"]["condition"] == "native-skill"
                and row["cell"]["scenario_id"] == scenario_id
            ]
            expected_loaded = fixtures[scenario_id].get(
                "expect_skill_loaded", True
            )
            loaded = sum(
                row["response"]["routing"]["skill_loaded"] for row in rows
            )
            required = (
                math.ceil(2 * matrix["repetitions"] / 3)
                if expected_loaded
                else 0
            )
            passed = len(rows) == matrix["repetitions"] and (
                loaded >= required if expected_loaded else loaded == 0
            )
            groups.append(
                {
                    "provider": model["provider"],
                    "model": model["model"],
                    "thinking": model["thinking"],
                    "scenario_id": scenario_id,
                    "expected_skill_loaded": expected_loaded,
                    "successful_samples": len(rows),
                    "loaded_samples": loaded,
                    "required_loaded_samples": required,
                    "passed": passed,
                }
            )
    passed = sum(group["passed"] for group in groups)
    return {
        "groups_expected": len(groups),
        "groups_passed": passed,
        "accepted": passed == len(groups),
        "groups": groups,
    }


def aggregate_results(
    matrix,
    fixtures,
    provenance,
    raw_directory,
    generated_at=None,
    skill_text=None,
):
    if skill_text is None:
        skill_text = SKILL_PATH.read_text(encoding="utf-8")
    successes = []
    partial_outputs = []
    unresolved = []
    counts = Counter()
    cells = list(iter_cells(matrix, fixtures))
    for cell in cells:
        path = raw_directory / raw_result_name(cell)
        if not path.exists():
            counts["missing"] += 1
            unresolved.append({"kind": "missing", "cell": cell})
            continue
        try:
            document = strict_json_loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError) as error:
            counts["invalid"] += 1
            unresolved.append(
                {"kind": "invalid", "cell": cell, "error": str(error)}
            )
            continue
        if error := raw_document_error(document):
            counts["invalid"] += 1
            unresolved.append(
                {"kind": "invalid", "cell": cell, "error": error}
            )
            continue
        if document.get("cell") != cell or document.get("provenance") != provenance:
            counts["stale"] += 1
            unresolved.append({"kind": "stale", "cell": cell})
            continue
        if error := raw_evidence_error(
            document,
            cell,
            matrix,
            fixtures[cell["scenario_id"]],
            skill_text,
        ):
            counts["invalid"] += 1
            unresolved.append(
                {"kind": "invalid", "cell": cell, "error": error}
            )
            continue
        completed_outputs = 0
        for attempt in document.get("attempts", []):
            response = attempt.get("partial_response")
            evaluation = attempt.get("partial_evaluation")
            if not response or not evaluation:
                continue
            completed_outputs += 1
            partial_outputs.append(
                {
                    "cell": cell,
                    "attempt": attempt.get("number"),
                    "stop_reason": response.get("stop_reason"),
                    "semantic_gate_passed": evaluation.get(
                        "semantic_gate_passed"
                    ),
                }
            )
        if document.get("status") != "success":
            counts["failed"] += 1
            unresolved.append(
                {
                    "kind": "failed",
                    "cell": cell,
                    "error": document.get("last_error"),
                    "attempts": len(document.get("attempts", [])),
                    "completed_outputs": completed_outputs,
                }
            )
            continue
        successes.append(document)
        counts["successful"] += 1

    condition_results = []
    for model in matrix["models"]:
        for condition in matrix["conditions"]:
            rows = [
                row
                for row in successes
                if row["cell"]["provider"] == model["provider"]
                and row["cell"]["model"] == model["model"]
                and row["cell"]["thinking"] == model["thinking"]
                and row["cell"]["condition"] == condition
            ]
            condition_results.append(
                {
                    "provider": model["provider"],
                    "model": model["model"],
                    "thinking": model["thinking"],
                    "condition": condition,
                    "runs": len(rows),
                    "semantic": aggregate_semantic(rows),
                    "style": aggregate_style(rows),
                    "operations": aggregate_operations(rows),
                }
            )

    expected = len(cells)
    completeness = {
        "expected": expected,
        "successful": counts["successful"],
        "failed": counts["failed"],
        "missing": counts["missing"],
        "stale": counts["stale"],
        "invalid": counts["invalid"],
        "complete": counts["successful"] == expected,
    }
    gate_conditions = matrix["semantic_gate_conditions"]
    gate_rows = [
        row for row in successes if row["cell"]["condition"] in gate_conditions
    ]
    expected_gate_samples = (
        len(matrix["models"])
        * len(gate_conditions)
        * len(matrix["scenario_ids"])
        * matrix["repetitions"]
    )
    passed_gate_samples = sum(
        row["evaluation"]["semantic_gate_passed"] for row in gate_rows
    )
    failed_gate_samples = sum(
        not row["evaluation"]["semantic_gate_passed"] for row in gate_rows
    )
    semantic_acceptance = {
        "conditions": gate_conditions,
        "expected_samples": expected_gate_samples,
        "successful_samples": len(gate_rows),
        "passed_samples": passed_gate_samples,
        "failed_samples": failed_gate_samples,
        "accepted": (
            len(gate_rows) == expected_gate_samples and failed_gate_samples == 0
        ),
    }
    model_identity_passed_samples = sum(
        row["condition_integrity"].get(
            "model_identity_passed",
            row["response"].get("provider") == row["cell"]["provider"]
            and row["response"].get("model") == row["cell"]["model"],
        )
        for row in successes
    )
    native_rows = [
        row for row in successes if row["cell"]["condition"] == "native-skill"
    ]
    expected_native_samples = (
        len(matrix["models"])
        * len(matrix["scenario_ids"])
        * matrix["repetitions"]
    )
    expected_skill_loaded_samples = (
        len(matrix["models"])
        * sum(
            fixtures[scenario_id].get("expect_skill_loaded", True)
            for scenario_id in matrix["scenario_ids"]
        )
        * matrix["repetitions"]
    )
    skill_loaded_samples = sum(
        row["response"]["routing"]["skill_loaded"] for row in native_rows
    )
    integrity_passed_samples = sum(
        row["condition_integrity"]["passed"] for row in successes
    )
    routing_safety_passed_samples = sum(
        routing_safety_passed(row["cell"], row["response"])
        for row in successes
    )
    activation = aggregate_activation(matrix, fixtures, successes)
    condition_integrity = {
        "expected_samples": expected,
        "successful_samples": len(successes),
        "integrity_passed_samples": integrity_passed_samples,
        "model_identity_passed_samples": model_identity_passed_samples,
        "routing_safety_passed_samples": routing_safety_passed_samples,
        "activation_groups_expected": activation["groups_expected"],
        "activation_groups_passed": activation["groups_passed"],
        "expected_native_samples": expected_native_samples,
        "successful_native_samples": len(native_rows),
        "expected_skill_loaded_samples": expected_skill_loaded_samples,
        "skill_loaded_samples": skill_loaded_samples,
        "accepted": (
            len(successes) == expected
            and model_identity_passed_samples == expected
            and routing_safety_passed_samples == expected
            and activation["accepted"]
        ),
    }
    return {
        "schema_version": 1,
        "generated_at": generated_at or utc_now(),
        "provenance": provenance,
        "matrix": {
            "id": matrix["matrix_id"],
            "version": matrix["version"],
            "conditions": matrix["conditions"],
            "repetitions": matrix["repetitions"],
        },
        "completeness": completeness,
        "condition_integrity": condition_integrity,
        "semantic_acceptance": semantic_acceptance,
        "condition_results": condition_results,
        "partial_outputs": partial_outputs,
        "unresolved": unresolved,
    }


def display_path(path):
    path = Path(path).resolve()
    try:
        return str(path.relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


def format_number(value, digits=2):
    if value is None:
        return "n/a"
    if isinstance(value, int):
        return str(value)
    return f"{value:.{digits}f}"


def write_reports(results, results_directory, matrix_path=DEFAULT_MATRIX_PATH):
    results_directory.mkdir(parents=True, exist_ok=True)
    write_json_atomic(results_directory / "results.json", results)
    failures_path = results_directory / "failures.json"
    if results["unresolved"]:
        write_json_atomic(failures_path, results["unresolved"])
    elif failures_path.exists():
        failures_path.unlink()

    completeness = results["completeness"]
    status = "COMPLETE" if completeness["complete"] else "INCOMPLETE"
    provenance = results["provenance"]
    lines = [
        "# Pi benchmark results",
        "",
        f"**{status}: {completeness['successful']}/{completeness['expected']} cells successful.**",
        "",
        "## Provenance",
        "",
        f"- Matrix: `{results['matrix']['id']}` version {results['matrix']['version']}",
        f"- Matrix SHA-256: `{provenance['matrix_sha256']}`",
        f"- Package commit: `{provenance['package_commit']}`",
        f"- Package dirty: `{str(provenance['package_dirty']).lower()}`",
        f"- Skill SHA-256: `{provenance.get('skill_sha256', 'unavailable')}`",
        f"- Pi version: `{provenance['pi_version']}`",
        f"- Runner version: `{provenance['runner_version']}`",
        "",
        "## Semantic results",
        "",
        (
            "**Condition integrity: "
            + ("ACCEPTED" if results["condition_integrity"]["accepted"] else "NOT ACCEPTED")
            + ".**"
        ),
        (
            "Model identity matches: "
            f"{results['condition_integrity']['model_identity_passed_samples']}/"
            f"{results['condition_integrity']['expected_samples']}."
        ),
        (
            "Routing safety passes: "
            f"{results['condition_integrity']['routing_safety_passed_samples']}/"
            f"{results['condition_integrity']['expected_samples']}."
        ),
        (
            "Native skill loads: "
            f"{results['condition_integrity']['skill_loaded_samples']}/"
            f"{results['condition_integrity']['expected_skill_loaded_samples']}."
        ),
        (
            "Activation groups passing threshold: "
            f"{results['condition_integrity']['activation_groups_passed']}/"
            f"{results['condition_integrity']['activation_groups_expected']}."
        ),
        "",
        (
            "**Semantic acceptance: "
            + ("ACCEPTED" if results["semantic_acceptance"]["accepted"] else "NOT ACCEPTED")
            + ".**"
        ),
        "",
        "| Model | Condition | Runs | Gate pass/fail | Procedure pass/fail | Output-contract pass/fail |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in results["condition_results"]:
        semantic = row["semantic"]
        procedure = semantic["procedure"]
        contract = semantic["output_contract"]
        model = f"{row['provider']}/{row['model']}:{row['thinking']}"
        lines.append(
            f"| `{model}` | {row['condition']} | {row['runs']} | "
            f"{semantic['samples_passed']}/{semantic['samples_failed']} | "
            f"{procedure['passed_samples']}/{procedure['failed_samples']} | "
            f"{contract['passed_samples']}/{contract['failed_samples']} |"
        )

    metric_rows = []
    for row in results["condition_results"]:
        model = f"{row['provider']}/{row['model']}:{row['thinking']}"
        for name, metric in row["semantic"]["metrics"].items():
            metric_rows.append(
                f"| `{model}` | {row['condition']} | `{name}` | "
                f"{metric['rules_total']} | {metric['rules_failed']} | "
                f"{format_number(metric['pass_rate'], 4)} |"
            )
    if metric_rows:
        lines.extend(
            [
                "",
                "### Deterministic semantic metrics",
                "",
                "| Model | Condition | Metric | Rules | Failed | Pass rate |",
                "|---|---|---|---:|---:|---:|",
                *metric_rows,
            ]
        )

    lines.extend(
        [
            "",
            "## Style results",
            "",
            "Style findings are advisory and cannot override semantic failures.",
            "",
            "| Model | Condition | Runs | Mechanical warnings |",
            "|---|---|---:|---:|",
        ]
    )
    for row in results["condition_results"]:
        model = f"{row['provider']}/{row['model']}:{row['thinking']}"
        lines.append(
            f"| `{model}` | {row['condition']} | {row['runs']} | "
            f"{row['style']['warning_count']} |"
        )

    lines.extend(
        [
            "",
            "## Usage, cost, and duration",
            "",
            "Means and population standard deviations use available successful samples only.",
            "",
            "| Model | Condition | Input mean±sd | Output mean±sd | Reasoning mean±sd | Cost sum | Duration mean±sd (ms) |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in results["condition_results"]:
        operations = row["operations"]
        model = f"{row['provider']}/{row['model']}:{row['thinking']}"
        lines.append(
            f"| `{model}` | {row['condition']} | "
            f"{format_number(operations['input_tokens']['mean'])}±{format_number(operations['input_tokens']['stddev'])} | "
            f"{format_number(operations['output_tokens']['mean'])}±{format_number(operations['output_tokens']['stddev'])} | "
            f"{format_number(operations['reasoning_tokens']['mean'])}±{format_number(operations['reasoning_tokens']['stddev'])} | "
            f"{format_number(operations['cost_usd']['sum'], 6)} | "
            f"{format_number(operations['duration_ms']['mean'])}±{format_number(operations['duration_ms']['stddev'])} |"
        )

    lines.extend(["", "## Unresolved cells", ""])
    if results.get("partial_outputs"):
        lines.append(
            f"Completed non-stop outputs retained as failure evidence: {len(results['partial_outputs'])}."
        )
        lines.append("")
    if results["unresolved"]:
        for item in results["unresolved"]:
            cell = item["cell"]
            lines.append(
                f"- {item['kind']}: `{cell['provider']}/{cell['model']}:{cell['thinking']}` "
                f"{cell['condition']} {cell['scenario_id']} repetition {cell['repetition']}"
            )
    else:
        lines.append("None.")

    lines.extend(
        [
            "",
            "## Reproduce",
            "",
            "```bash",
            "python3 evals/run_pi_bench.py \\",
            f"  --matrix {display_path(matrix_path)} \\",
            f"  --results-dir {display_path(results_directory)}",
            "```",
            "",
            "Existing matching successful raw cells are skipped. Failed cells retain attempt history and are retried.",
            "",
            "## Limits",
            "",
            "- Deterministic fixture checks cover enumerated properties only; open prose still needs attested semantic review.",
            "- Provider reasoning metadata can be unavailable. Missing values remain `null` in raw and aggregate JSON.",
            "- Hidden reasoning content is not stored.",
            "- This benchmark is advisory and does not certify ASD-STE100 compliance.",
        ]
    )
    (results_directory / "RESULTS.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def file_slug(value):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value)


def raw_result_name(cell):
    model_spec = f"{cell['provider']}_{cell['model']}_{cell['thinking']}"
    return (
        f"{file_slug(model_spec)}__{file_slug(cell['condition'])}__"
        f"{file_slug(cell['scenario_id'])}__r{cell['repetition']:02d}.json"
    )


def execute_benchmark(
    matrix_path,
    results_directory,
    report_only=False,
    provenance=None,
    run_cell_function=run_cell,
    pause=time.sleep,
    emit=print,
):
    matrix_path = Path(matrix_path)
    results_directory = Path(results_directory)
    matrix = load_matrix(matrix_path)
    fixtures, scenarios = load_matrix_scenarios(matrix)
    if not report_only:
        score_fixtures.load_linter()
    provenance = provenance or collect_provenance(matrix_path)
    raw_directory = results_directory / "raw"
    raw_directory.mkdir(parents=True, exist_ok=True)

    if not report_only:
        if provenance["package_dirty"]:
            raise RuntimeError(
                "benchmark generation requires a clean git working tree"
            )
        with tempfile.TemporaryDirectory(prefix="pi-ste-snapshot-") as directory:
            skill_snapshot = Path(directory) / "clear-technical-writing"
            shutil.copytree(
                SKILL_DIR,
                skill_snapshot,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
            )
            if tree_sha256(skill_snapshot) != provenance.get("skill_sha256"):
                raise RuntimeError(
                    "skill resources changed after provenance capture"
                )
            skill_text = (skill_snapshot / "SKILL.md").read_text(
                encoding="utf-8"
            )
            cells = list(iter_cells(matrix, scenarios))
            for index, cell in enumerate(cells, 1):
                raw_path = raw_directory / raw_result_name(cell)
                emit(
                    f"[{index}/{len(cells)}] {cell['provider']}/{cell['model']}:"
                    f"{cell['thinking']} {cell['condition']} "
                    f"{cell['scenario_id']} r{cell['repetition']}"
                )
                try:
                    outcome = run_cell_function(
                        cell,
                        matrix,
                        scenarios[cell["scenario_id"]],
                        skill_text,
                        provenance,
                        raw_path,
                        pause=pause,
                        skill_dir=skill_snapshot,
                    )
                except RuntimeError as error:
                    emit(f"  STALE {error}")
                    continue
                emit(f"  {outcome['action'].upper()}")
                if outcome["action"] != "skipped" and index < len(cells):
                    pause(matrix["inter_call_delay_seconds"])

    results = aggregate_results(
        matrix,
        scenarios,
        provenance,
        raw_directory,
        skill_text=skill_text if not report_only else None,
    )
    write_reports(results, results_directory, matrix_path)
    return results


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--matrix",
        type=Path,
        default=DEFAULT_MATRIX_PATH,
        help=f"benchmark matrix (default: {DEFAULT_MATRIX_PATH})",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help=f"raw and aggregate result directory (default: {DEFAULT_RESULTS_DIR})",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="aggregate existing raw cells without model calls",
    )
    return parser


def benchmark_accepted(results):
    return (
        results["completeness"]["complete"]
        and results["condition_integrity"]["accepted"]
        and results["semantic_acceptance"]["accepted"]
    )


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        results = execute_benchmark(
            args.matrix,
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
    report = (args.results_dir / "RESULTS.md").read_text(encoding="utf-8")
    print(report, end="")
    return 0 if benchmark_accepted(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
