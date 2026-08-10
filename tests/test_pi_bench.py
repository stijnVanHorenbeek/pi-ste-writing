import json
import hashlib
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_CONFIG = ROOT / "archive" / "pre-release" / "evals" / "config"
MATRIX_PATH = ARCHIVE_CONFIG / "initial-skill-matrix.json"
INDEPENDENT_MATRIX_PATH = ARCHIVE_CONFIG / "independent-review-matrix.json"
RELEASE_CANDIDATE_MATRIX_PATH = ROOT / "evals" / "release-candidate-matrix.json"
HYBRID_RELEASE_MATRIX_PATH = ROOT / "evals" / "hybrid-release-candidate-matrix.json"
DEVELOPMENT_SMOKE_MATRIX_PATH = (
    ROOT / "evals" / "development-guard-smoke-matrix.json"
)
CORPUS_PATH = ROOT / "evals" / "fixtures" / "semantic-preservation.json"
RELEASE_CANDIDATE_CORPUS_PATH = ROOT / "evals" / "fixtures" / "release-candidate.json"
RELEASE_CANDIDATE_SCENARIOS_PATH = ROOT / "evals" / "release-candidate-scenarios.json"
HYBRID_RELEASE_SCENARIOS_PATH = ROOT / "evals" / "hybrid-release-candidate-scenarios.json"
BENCHMARK_SCENARIOS_PATH = ROOT / "evals" / "benchmark-scenarios.json"
EVALS_DIR = ROOT / "evals"
sys.path.insert(0, str(EVALS_DIR))

import run_pi_bench


def schema_v3_matrix():
    matrix = json.loads(RELEASE_CANDIDATE_MATRIX_PATH.read_text(encoding="utf-8"))
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
    return matrix


def guarded_event_stream(statuses=("accepted",), final_text="accepted draft"):
    usage = {
        "input": 1,
        "output": 1,
        "reasoning": 0,
        "cacheRead": 0,
        "cacheWrite": 0,
        "totalTokens": 2,
        "cost": {"total": 0},
    }
    events = []
    for attempt, status in enumerate(statuses, 1):
        draft = final_text if status == "accepted" else f"rejected draft {attempt}"
        call_id = f"submit-{attempt}"
        events.extend(
            [
                {
                    "type": "message_end",
                    "message": {
                        "role": "assistant",
                        "provider": "provider",
                        "model": "model",
                        "content": [
                            {"type": "thinking", "thinking": "private"},
                            {
                                "type": "toolCall",
                                "id": call_id,
                                "name": "submit_clear_rewrite",
                                "arguments": {"jobId": "job", "draft": draft},
                            }
                        ],
                        "usage": usage,
                        "stopReason": "toolUse",
                    },
                },
                {
                    "type": "tool_execution_start",
                    "toolCallId": call_id,
                    "toolName": "submit_clear_rewrite",
                    "args": {"jobId": "job", "draft": draft},
                },
                {
                    "type": "tool_execution_end",
                    "toolCallId": call_id,
                    "toolName": "submit_clear_rewrite",
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": draft if status == "accepted" else "repair",
                            }
                        ],
                        "details": {
                            "status": status,
                            "attempt": attempt,
                            **({"draft": draft} if status == "accepted" else {}),
                        },
                    },
                    "isError": False,
                },
            ]
        )
    events.append(
        {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "provider": "provider",
                "model": "model",
                "content": [{"type": "text", "text": final_text}],
                "usage": usage,
                "stopReason": "stop",
            },
        }
    )
    return events


class MatrixLoadingTest(unittest.TestCase):
    def test_matrix_rejects_fewer_than_three_repetitions(self):
        matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        matrix["repetitions"] = 2
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "matrix.json"
            path.write_text(json.dumps(matrix), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "at least 3 repetitions"):
                run_pi_bench.load_matrix(path)

    def test_matrix_rejects_ambiguous_or_unsupported_dimensions(self):
        original = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        cases = []

        matrix = json.loads(json.dumps(original))
        matrix["conditions"].append("baseline")
        cases.append(("conditions", matrix))

        matrix = json.loads(json.dumps(original))
        del matrix["models"][0]["provider"]
        cases.append(("model", matrix))

        matrix = json.loads(json.dumps(original))
        matrix["models"][0]["thinking"] = "extreme"
        cases.append(("thinking", matrix))

        matrix = json.loads(json.dumps(original))
        matrix["scenario_ids"].append(matrix["scenario_ids"][0])
        cases.append(("scenario", matrix))

        matrix = json.loads(json.dumps(original))
        matrix["version"] += 1
        cases.append(("amendment", matrix))

        matrix = json.loads(json.dumps(original))
        del matrix["isolation"]["tools_by_condition"]["baseline"]
        cases.append(("tools_by_condition", matrix))

        matrix = json.loads(json.dumps(original))
        matrix["output_contract"]["forbidden_patterns"] = ["("]
        cases.append(("output contract", matrix))

        matrix = json.loads(json.dumps(original))
        matrix["output_contract"] = {
            "type": "json_object",
            "required_keys": ["status"],
            "additional_properties": False,
            "property_types": {"status": "unsupported"},
        }
        cases.append(("output contract", matrix))

        for phrase, matrix in cases:
            with self.subTest(phrase=phrase):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "matrix.json"
                    path.write_text(json.dumps(matrix), encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, phrase):
                        run_pi_bench.load_matrix(path)

    def test_matrix_data_paths_cannot_escape_evals(self):
        matrix = json.loads(INDEPENDENT_MATRIX_PATH.read_text(encoding="utf-8"))
        matrix["corpus_path"] = "../outside.json"

        with self.assertRaisesRegex(ValueError, "stay within evals"):
            run_pi_bench.load_matrix_scenarios(matrix)

    def test_schema_v2_matrix_supports_guarded_condition_applicability(self):
        matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        matrix["schema_version"] = 2
        matrix["run_kind"] = "release-candidate"
        matrix["judge_config_path"] = "release-candidate-quality-judge.json"
        structured = matrix["scenario_ids"][-1]
        matrix["conditions"] = ["baseline", "native-skill", "guarded"]
        matrix["semantic_gate_conditions"] = ["native-skill", "guarded"]
        matrix["conditions_by_scenario"] = {
            scenario_id: (
                ["baseline", "native-skill"]
                if scenario_id == structured
                else list(matrix["conditions"])
            )
            for scenario_id in matrix["scenario_ids"]
        }
        matrix["isolation"]["tools_by_condition"] = {
            "baseline": [],
            "native-skill": ["read"],
            "guarded": [],
        }
        matrix["max_parallel_calls"] = 3
        matrix["max_parallel_calls_by_provider"] = {
            "openai-codex": 1,
            "github-copilot": 2,
        }
        matrix["acceptance_thresholds"] = {
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
        }

        run_pi_bench.validate_matrix(matrix)
        scenarios = run_pi_bench.load_scenarios(
            run_pi_bench.load_fixtures(CORPUS_PATH),
            BENCHMARK_SCENARIOS_PATH,
        )
        cells = list(run_pi_bench.iter_cells(matrix, scenarios))

        self.assertEqual(len(cells), 153)
        self.assertFalse(
            any(
                cell["scenario_id"] == structured
                and cell["condition"] == "guarded"
                for cell in cells
            )
        )

    def test_schema_v2_matrix_rejects_unknown_scenario_condition(self):
        matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        matrix["schema_version"] = 2
        matrix["run_kind"] = "release-candidate"
        matrix["judge_config_path"] = "release-candidate-quality-judge.json"
        matrix["conditions"] = ["baseline", "native-skill", "guarded"]
        matrix["semantic_gate_conditions"] = ["native-skill", "guarded"]
        matrix["conditions_by_scenario"] = {
            scenario_id: list(matrix["conditions"])
            for scenario_id in matrix["scenario_ids"]
        }
        matrix["conditions_by_scenario"][matrix["scenario_ids"][0]] = ["unknown"]
        matrix["isolation"]["tools_by_condition"] = {
            "baseline": [],
            "native-skill": ["read"],
            "guarded": [],
        }
        matrix["max_parallel_calls"] = 3
        matrix["max_parallel_calls_by_provider"] = {
            "openai-codex": 1,
            "github-copilot": 2,
        }
        matrix["acceptance_thresholds"] = {
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
        }

        with self.assertRaisesRegex(ValueError, "conditions_by_scenario"):
            run_pi_bench.validate_matrix(matrix)

    def test_schema_v2_ragged_gate_denominators_count_only_applicable_cells(self):
        matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        matrix["schema_version"] = 2
        matrix["run_kind"] = "release-candidate"
        matrix["judge_config_path"] = "release-candidate-quality-judge.json"
        matrix["conditions"] = ["baseline", "native-skill", "guarded"]
        matrix["semantic_gate_conditions"] = ["native-skill", "guarded"]
        structured = matrix["scenario_ids"][-1]
        matrix["conditions_by_scenario"] = {
            scenario_id: (
                ["baseline", "native-skill"]
                if scenario_id == structured
                else list(matrix["conditions"])
            )
            for scenario_id in matrix["scenario_ids"]
        }
        matrix["isolation"]["tools_by_condition"] = {
            "baseline": [],
            "native-skill": ["read"],
            "guarded": [],
        }
        matrix["max_parallel_calls"] = 3
        matrix["max_parallel_calls_by_provider"] = {
            "openai-codex": 1,
            "github-copilot": 2,
        }
        matrix["acceptance_thresholds"] = {
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
        }
        scenarios = run_pi_bench.load_scenarios(
            run_pi_bench.load_fixtures(CORPUS_PATH),
            BENCHMARK_SCENARIOS_PATH,
        )
        with tempfile.TemporaryDirectory() as directory:
            results = run_pi_bench.aggregate_results(
                matrix,
                scenarios,
                {"matrix_sha256": "hash"},
                Path(directory),
            )

        self.assertEqual(results["completeness"]["expected"], 153)
        self.assertEqual(results["semantic_acceptance"]["expected_samples"], 99)
        self.assertEqual(results["procedure_acceptance"]["expected_samples"], 18)
        self.assertEqual(
            results["output_contract_acceptance"]["expected_samples"], 99
        )
        self.assertEqual(
            results["condition_integrity"]["expected_native_samples"],
            54,
        )
        self.assertEqual(results["guard_integrity"]["expected_samples"], 45)
        self.assertEqual(results["guard_integrity"]["successful_samples"], 0)
        self.assertEqual(len(results["applicability"]["groups"]), 51)
        self.assertEqual(
            sum(group["expected_samples"] for group in results["applicability"]["groups"]),
            153,
        )
        self.assertFalse(results["guard_integrity"]["accepted"])

    def test_schema_v2_guarded_scenarios_require_command_equivalent_tasks(self):
        matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        matrix["schema_version"] = 2
        matrix["run_kind"] = "release-candidate"
        matrix["judge_config_path"] = "release-candidate-quality-judge.json"
        matrix["conditions"] = ["baseline", "native-skill", "guarded"]
        matrix["semantic_gate_conditions"] = ["native-skill", "guarded"]
        matrix["conditions_by_scenario"] = {
            scenario_id: (
                ["baseline", "native-skill"]
                if scenario_id == matrix["scenario_ids"][-1]
                else ["baseline", "native-skill", "guarded"]
            )
            for scenario_id in matrix["scenario_ids"]
        }
        matrix["isolation"]["tools_by_condition"] = {
            "baseline": [],
            "native-skill": ["read"],
            "guarded": [],
        }
        matrix["max_parallel_calls"] = 3
        matrix["max_parallel_calls_by_provider"] = {
            "openai-codex": 1,
            "github-copilot": 2,
        }
        matrix["acceptance_thresholds"] = {
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
        }
        scenarios = run_pi_bench.load_scenarios(
            run_pi_bench.load_fixtures(CORPUS_PATH),
            BENCHMARK_SCENARIOS_PATH,
        )

        with self.assertRaisesRegex(ValueError, "command-equivalent task"):
            run_pi_bench.validate_scenario_applicability(matrix, scenarios)

        canonical = json.loads(json.dumps(scenarios))
        for scenario_id in matrix["scenario_ids"]:
            mode = canonical[scenario_id]["mode"]
            canonical[scenario_id]["task"] = run_pi_bench.canonical_rewrite_task(mode)
            canonical[scenario_id]["output_contract"] = {
                "type": "text",
                "forbidden_patterns": [],
            }
        run_pi_bench.validate_scenario_applicability(matrix, canonical)

    def test_schema_v1_matrix_rejects_guarded_condition(self):
        matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        matrix["conditions"][-1] = "guarded"
        matrix["isolation"]["tools_by_condition"]["guarded"] = (
            matrix["isolation"]["tools_by_condition"].pop("direct-prompt")
        )

        with self.assertRaisesRegex(ValueError, "schema-v1 conditions"):
            run_pi_bench.validate_matrix(matrix)

    def test_matrix_expands_to_unique_repeated_cells(self):
        matrix = run_pi_bench.load_matrix(MATRIX_PATH)
        fixtures = run_pi_bench.load_fixtures(CORPUS_PATH)
        scenarios = run_pi_bench.load_scenarios(
            fixtures,
            BENCHMARK_SCENARIOS_PATH,
        )

        cells = list(run_pi_bench.iter_cells(matrix, scenarios))

        self.assertEqual(len(cells), 162)
        self.assertEqual(
            cells[0],
            {
                "provider": "openai-codex",
                "model": "gpt-5.6-sol",
                "thinking": "high",
                "condition": "baseline",
                "scenario_id": "release-facts-and-causes",
                "repetition": 1,
            },
        )
        names = [run_pi_bench.raw_result_name(cell) for cell in cells]
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(names[0].endswith("__r01.json"))


class ReleaseCandidateMatrixTest(unittest.TestCase):
    def test_development_smoke_is_three_guarded_calls_on_known_evidence(self):
        matrix = run_pi_bench.load_matrix(DEVELOPMENT_SMOKE_MATRIX_PATH)
        _fixtures, scenarios = run_pi_bench.load_matrix_scenarios(matrix)
        cells = list(run_pi_bench.iter_cells(matrix, scenarios))

        self.assertEqual(matrix["run_kind"], "development-smoke")
        self.assertEqual(len(cells), 3)
        self.assertEqual({cell["condition"] for cell in cells}, {"guarded"})
        self.assertEqual(
            {cell["scenario_id"] for cell in cells},
            {"release-facts-and-causes"},
        )
        self.assertFalse(
            matrix["acceptance_thresholds"]["activation_applicable"]
        )
        self.assertTrue(matrix["evidence_policy"]["development_only"])
        self.assertTrue(
            matrix["evidence_policy"]["must_not_count_as_release_evidence"]
        )

    def test_release_generation_requires_no_prior_output_attestation(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(
                RuntimeError, "attest-no-prior-candidate-output"
            ):
                run_pi_bench.execute_benchmark(
                    RELEASE_CANDIDATE_MATRIX_PATH,
                    Path(directory),
                    provenance={"package_dirty": False},
                    run_cell_function=lambda *_args, **_kwargs: self.fail(
                        "unattested release invoked a model cell"
                    ),
                )

    def test_release_generation_refuses_missing_prerequisite_smoke(self):
        matrix = run_pi_bench.load_matrix(RELEASE_CANDIDATE_MATRIX_PATH)
        with tempfile.TemporaryDirectory(dir=EVALS_DIR) as directory:
            relative = Path(directory).relative_to(EVALS_DIR)
            matrix["prerequisite_smoke"]["results_directory"] = str(relative)
            with self.assertRaisesRegex(RuntimeError, "completed smoke results"):
                run_pi_bench.validate_prerequisite_smoke(
                    matrix,
                    {
                        "runner_version": run_pi_bench.RUNNER_VERSION,
                        "package_commit": "a" * 40,
                        "package_dirty": False,
                        "skill_sha256": "b" * 64,
                        "extension_sha256": "c" * 64,
                        "pi_version": "0.84.1",
                    },
                )

    def test_preregisters_unseen_ragged_release_evidence_design(self):
        matrix = run_pi_bench.load_matrix(RELEASE_CANDIDATE_MATRIX_PATH)
        fixtures, scenarios = run_pi_bench.load_matrix_scenarios(matrix)
        cells = list(run_pi_bench.iter_cells(matrix, scenarios))

        self.assertEqual(matrix["schema_version"], 2)
        self.assertEqual(matrix["version"], 2)
        self.assertEqual(
            matrix["models"],
            [
                {
                    "provider": "openai-codex",
                    "model": "gpt-5.6-sol",
                    "thinking": "high",
                },
                {
                    "provider": "github-copilot",
                    "model": "claude-sonnet-5",
                    "thinking": "low",
                },
                {
                    "provider": "github-copilot",
                    "model": "gemini-3.6-flash",
                    "thinking": "medium",
                },
            ],
        )
        self.assertEqual(len(fixtures), 5)
        self.assertEqual(len(scenarios), 6)
        self.assertEqual(len(cells), 153)
        self.assertEqual(sum(cell["condition"] == "guarded" for cell in cells), 45)
        self.assertEqual(
            matrix["conditions_by_scenario"]["hushvale-spore-transfer-csv"],
            ["baseline", "native-skill"],
        )
        self.assertEqual(matrix["max_parallel_calls_by_provider"], {
            "openai-codex": 1,
            "github-copilot": 2,
        })
        self.assertTrue(
            matrix["evidence_policy"]["no_repairs_based_on_release_candidate_outputs"]
        )
        for scenario_id, scenario in fixtures.items():
            self.assertIs(scenario.get("expect_skill_loaded"), True, scenario_id)
            self.assertEqual(
                scenario["task"],
                run_pi_bench.canonical_rewrite_task(scenario["mode"]),
                scenario_id,
            )
        structured_input = run_pi_bench.build_task_input(
            scenarios["hushvale-spore-transfer-csv"]
        )
        self.assertTrue(structured_input.endswith("Return only the requested output."))
        self.assertNotIn("rewritten text", structured_input)


class IndependentReviewMatrixTest(unittest.TestCase):
    def test_preregisters_unseen_scenarios_before_generation(self):
        matrix = run_pi_bench.load_matrix(INDEPENDENT_MATRIX_PATH)
        fixtures, scenarios = run_pi_bench.load_matrix_scenarios(matrix)

        self.assertEqual(matrix["matrix_id"], "v1-independent-review")
        self.assertEqual(matrix["version"], 1)
        self.assertEqual(
            matrix["scenario_ids"],
            [
                "helios-transcoder-confirmed-and-unconfirmed-cause",
                "orbital-greenhouse-modal-policy",
                "vesper-witness-repository-terms",
                "broker-failover-correlation-unknown-cause",
                "ledger-archive-purge-destructive-procedure",
                "orbital-imager-structured-incident-status",
            ],
        )
        self.assertEqual(matrix["semantic_gate_conditions"], ["native-skill"])
        self.assertEqual(matrix["corpus_path"], "fixtures/independent-review.json")
        self.assertEqual(
            matrix["benchmark_scenarios_path"],
            "independent-review-scenarios.json",
        )
        self.assertEqual(set(fixtures), set(matrix["scenario_ids"][:-1]))
        self.assertEqual(matrix["repetitions"], 3)
        self.assertEqual(len(list(run_pi_bench.iter_cells(matrix, scenarios))), 162)
        self.assertTrue(
            all(scenario_id in scenarios for scenario_id in matrix["scenario_ids"])
        )
        self.assertFalse(
            scenarios["orbital-imager-structured-incident-status"][
                "expect_skill_loaded"
            ]
        )


class PiJsonEventParsingTest(unittest.TestCase):
    def test_aggregates_turn_usage_without_storing_reasoning_content(self):
        events = [
            {"type": "session", "version": 3, "id": "session", "cwd": "/tmp"},
            {
                "type": "message_end",
                "message": {
                    "role": "assistant",
                    "provider": "example-provider",
                    "model": "example-model",
                    "content": [
                        {"type": "thinking", "thinking": "secret chain one"},
                        {
                            "type": "toolCall",
                            "id": "call-1",
                            "name": "read",
                            "arguments": {"path": str(run_pi_bench.SKILL_PATH)},
                        },
                    ],
                    "usage": {
                        "input": 10,
                        "output": 7,
                        "reasoning": 3,
                        "cacheRead": 2,
                        "cacheWrite": 1,
                        "totalTokens": 20,
                        "cost": {"total": 0.1},
                    },
                    "stopReason": "toolUse",
                },
            },
            {
                "type": "tool_execution_start",
                "toolCallId": "call-1",
                "toolName": "read",
                "args": {"path": str(run_pi_bench.SKILL_PATH)},
            },
            {
                "type": "tool_execution_end",
                "toolCallId": "call-1",
                "toolName": "read",
                "result": {"content": "skill"},
                "isError": False,
            },
            {
                "type": "message_end",
                "message": {
                    "role": "assistant",
                    "provider": "example-provider",
                    "model": "example-model",
                    "responseModel": "upstream-example-model",
                    "content": [
                        {"type": "thinking", "thinking": "secret chain two"},
                        {"type": "text", "text": "final text"},
                    ],
                    "usage": {
                        "input": 4,
                        "output": 6,
                        "reasoning": 2,
                        "cacheRead": 0,
                        "cacheWrite": 0,
                        "totalTokens": 10,
                        "cost": {"total": 0.2},
                    },
                    "stopReason": "stop",
                },
            },
        ]

        result = run_pi_bench.parse_pi_json_events(
            "\n".join(json.dumps(event) for event in events)
        )

        self.assertEqual(result["text"], "final text")
        self.assertEqual(result["provider"], "example-provider")
        self.assertEqual(result["model"], "example-model")
        self.assertEqual(result["response_model"], "upstream-example-model")
        self.assertEqual(result["stop_reason"], "stop")
        self.assertEqual(
            result["usage"],
            {
                "input_tokens": {"value": 14, "available": True},
                "output_tokens": {
                    "value": 13,
                    "available": True,
                    "includes_reasoning": True,
                },
                "reasoning_tokens": {"value": 5, "available": True},
                "visible_output_tokens": {
                    "value": 8,
                    "available": True,
                    "derived": True,
                },
                "cache_read_tokens": {"value": 2, "available": True},
                "cache_write_tokens": {"value": 1, "available": True},
                "total_tokens": {"value": 30, "available": True},
            },
        )
        self.assertEqual(
            result["cost_usd"],
            {"value": 0.3, "available": True},
        )
        self.assertEqual(
            result["routing"],
            {
                "tool_calls": 1,
                "non_read_tool_calls": 0,
                "read_calls": 1,
                "successful_read_calls": 1,
                "failed_read_calls": 0,
                "skill_entrypoint_read_calls": 1,
                "skill_tree_read_calls": 1,
                "outside_skill_read_calls": 0,
                "skill_loaded": True,
            },
        )
        serialized = json.dumps(result)
        self.assertNotIn("secret chain", serialized)
        self.assertNotIn("toolCall", serialized)

    def test_records_guard_acceptance_without_storing_submitted_draft(self):
        draft = "Keep `OPS-8842` unchanged."
        events = [
            {
                "type": "message_end",
                "message": {
                    "role": "assistant",
                    "provider": "provider",
                    "model": "model",
                    "content": [
                        {"type": "thinking", "thinking": "private"},
                        {
                            "type": "toolCall",
                            "id": "submit-1",
                            "name": "submit_clear_rewrite",
                            "arguments": {
                                "jobId": "secret-job",
                                "draft": "rejected secret draft",
                            },
                        }
                    ],
                    "usage": {
                        "input": 2,
                        "output": 1,
                        "reasoning": 0,
                        "cacheRead": 0,
                        "cacheWrite": 0,
                        "totalTokens": 3,
                        "cost": {"total": 0.01},
                    },
                    "stopReason": "toolUse",
                },
            },
            {
                "type": "tool_execution_start",
                "toolCallId": "submit-1",
                "toolName": "submit_clear_rewrite",
                "args": {"jobId": "secret-job", "draft": "rejected secret draft"},
            },
            {
                "type": "tool_execution_end",
                "toolCallId": "submit-1",
                "toolName": "submit_clear_rewrite",
                "result": {
                    "content": [{"type": "text", "text": "repair protected content"}],
                    "details": {
                        "status": "retry",
                        "attempt": 1,
                        "violations": [{"kind": "inline-code"}],
                    },
                },
                "isError": False,
            },
            {
                "type": "message_end",
                "message": {
                    "role": "assistant",
                    "provider": "provider",
                    "model": "model",
                    "content": [
                        {"type": "thinking", "thinking": "private"},
                        {
                            "type": "toolCall",
                            "id": "submit-2",
                            "name": "submit_clear_rewrite",
                            "arguments": {"jobId": "secret-job", "draft": draft},
                        }
                    ],
                    "usage": {
                        "input": 2,
                        "output": 1,
                        "reasoning": 0,
                        "cacheRead": 0,
                        "cacheWrite": 0,
                        "totalTokens": 3,
                        "cost": {"total": 0.01},
                    },
                    "stopReason": "toolUse",
                },
            },
            {
                "type": "tool_execution_start",
                "toolCallId": "submit-2",
                "toolName": "submit_clear_rewrite",
                "args": {"jobId": "secret-job", "draft": draft},
            },
            {
                "type": "tool_execution_end",
                "toolCallId": "submit-2",
                "toolName": "submit_clear_rewrite",
                "result": {
                    "content": [{"type": "text", "text": draft}],
                    "details": {
                        "status": "accepted",
                        "attempt": 2,
                        "draft": draft,
                    },
                },
                "isError": False,
            },
            {
                "type": "message_end",
                "message": {
                    "role": "assistant",
                    "provider": "provider",
                    "model": "model",
                    "content": [{"type": "text", "text": draft}],
                    "usage": {
                        "input": 1,
                        "output": 1,
                        "reasoning": 0,
                        "cacheRead": 0,
                        "cacheWrite": 0,
                        "totalTokens": 2,
                        "cost": {"total": 0.01},
                    },
                    "stopReason": "stop",
                },
            },
        ]

        response = run_pi_bench.parse_pi_json_events(
            "\n".join(json.dumps(event) for event in events)
        )

        sha = lambda value: hashlib.sha256(value.encode()).hexdigest()
        self.assertEqual(
            response["guard"],
            {
                "observed": True,
                "max_submissions": 3,
                "submissions": [
                    {
                        "sequence": 1,
                        "tool_call_id_sha256": sha("submit-1"),
                        "job_id_sha256": sha("secret-job"),
                        "draft_sha256": sha("rejected secret draft"),
                        "draft_bytes": len("rejected secret draft".encode()),
                        "result_status": "retry",
                        "result_attempt": 1,
                        "result_draft_sha256": None,
                        "result_text_sha256": sha("repair protected content"),
                        "is_error": False,
                        "submission_message_valid": True,
                    },
                    {
                        "sequence": 2,
                        "tool_call_id_sha256": sha("submit-2"),
                        "job_id_sha256": sha("secret-job"),
                        "draft_sha256": sha(draft),
                        "draft_bytes": len(draft.encode()),
                        "result_status": "accepted",
                        "result_attempt": 2,
                        "result_draft_sha256": sha(draft),
                        "result_text_sha256": sha(draft),
                        "is_error": False,
                        "submission_message_valid": True,
                    },
                ],
                "accepted_submission": 2,
                "accepted_draft_sha256": sha(draft),
                "final_text_sha256": sha(draft),
                "exact_accepted_output": True,
                "malformed_submission_messages": 0,
                "direct_output_messages": 0,
                "unauthorized_tool_calls": 0,
                "unmatched_tool_events": 0,
                "ambient_resources_disabled": True,
                "terminal_artifact_valid": True,
                "same_job_id": True,
                "attempts_contiguous": True,
                "passed": True,
            },
        )
        serialized = json.dumps(response)
        self.assertNotIn("secret-job", serialized)
        self.assertNotIn("rejected secret draft", serialized)

    def test_guarded_integrity_requires_accepted_matching_submit_artifact(self):
        draft = "Preserve `NODE-918` exactly."
        messages = []
        for content, stop_reason in (
            (
                [
                    {"type": "thinking", "thinking": "private"},
                    {
                        "type": "toolCall",
                        "id": "submit-1",
                        "name": "submit_clear_rewrite",
                        "arguments": {"jobId": "job", "draft": draft},
                    }
                ],
                "toolUse",
            ),
            ([{"type": "text", "text": draft}], "stop"),
        ):
            messages.append(
                {
                    "type": "message_end",
                    "message": {
                        "role": "assistant",
                        "provider": "provider",
                        "model": "model",
                        "content": content,
                        "usage": {
                            "input": 1,
                            "output": 1,
                            "reasoning": 0,
                            "cacheRead": 0,
                            "cacheWrite": 0,
                            "totalTokens": 2,
                            "cost": {"total": 0},
                        },
                        "stopReason": stop_reason,
                    },
                }
            )
        events = [
            messages[0],
            {
                "type": "tool_execution_start",
                "toolCallId": "submit-1",
                "toolName": "submit_clear_rewrite",
                "args": {"jobId": "job", "draft": draft},
            },
            {
                "type": "tool_execution_end",
                "toolCallId": "submit-1",
                "toolName": "submit_clear_rewrite",
                "result": {
                    "content": [{"type": "text", "text": draft}],
                    "details": {"status": "accepted", "attempt": 1, "draft": draft},
                },
                "isError": False,
            },
            messages[1],
        ]
        response = run_pi_bench.parse_pi_json_events(
            "\n".join(json.dumps(event) for event in events)
        )
        cell = {"condition": "guarded", "provider": "provider", "model": "model"}

        self.assertIsNone(run_pi_bench.response_error(response, "guarded response"))
        self.assertTrue(
            run_pi_bench.expected_condition_integrity(cell, {}, response)["passed"]
        )

        tampered = json.loads(json.dumps(response))
        tampered["guard"]["exact_accepted_output"] = False
        tampered["guard"]["passed"] = False
        self.assertFalse(
            run_pi_bench.expected_condition_integrity(cell, {}, tampered)["passed"]
        )
        self.assertIn(
            "guard evidence is inconsistent",
            run_pi_bench.response_error(tampered, "tampered guarded response"),
        )

    def test_guarded_mixed_text_and_submit_call_fails_closed(self):
        draft = "Mixed draft"
        usage = {
            "input": 1,
            "output": 1,
            "reasoning": 0,
            "cacheRead": 0,
            "cacheWrite": 0,
            "totalTokens": 2,
            "cost": {"total": 0},
        }
        events = [
            {
                "type": "message_end",
                "message": {
                    "role": "assistant",
                    "provider": "provider",
                    "model": "model",
                    "content": [
                        {"type": "thinking", "thinking": "private"},
                        {"type": "text", "text": "preamble"},
                        {
                            "type": "toolCall",
                            "id": "submit-1",
                            "name": "submit_clear_rewrite",
                            "arguments": {"jobId": "job", "draft": draft},
                        },
                    ],
                    "usage": usage,
                    "stopReason": "toolUse",
                },
            },
            {
                "type": "tool_execution_start",
                "toolCallId": "submit-1",
                "toolName": "submit_clear_rewrite",
                "args": {"jobId": "job", "draft": draft},
            },
            {
                "type": "tool_execution_end",
                "toolCallId": "submit-1",
                "toolName": "submit_clear_rewrite",
                "result": {
                    "content": [{"type": "text", "text": draft}],
                    "details": {"status": "accepted", "attempt": 1, "draft": draft},
                },
                "isError": False,
            },
            {
                "type": "message_end",
                "message": {
                    "role": "assistant",
                    "provider": "provider",
                    "model": "model",
                    "content": [{"type": "text", "text": draft}],
                    "usage": usage,
                    "stopReason": "stop",
                },
            },
        ]

        response = run_pi_bench.parse_pi_json_events(
            "\n".join(json.dumps(event) for event in events),
            expect_guard=True,
        )

        self.assertEqual(response["guard"]["malformed_submission_messages"], 1)
        self.assertFalse(response["guard"]["passed"])
        self.assertFalse(
            run_pi_bench.routing_safety_passed(
                {"condition": "guarded"},
                response,
            )
        )

    def test_guarded_event_protocol_rejects_mismatch_limits_and_post_acceptance(self):
        cases = {}

        mismatched = guarded_event_stream()
        mismatched[1]["args"]["draft"] = "different start draft"
        cases["message-start mismatch"] = mismatched

        sibling = guarded_event_stream()
        sibling[0]["message"]["content"].append(
            {"type": "toolCall", "id": "other", "name": "bash", "arguments": {}}
        )
        cases["sibling call"] = sibling

        cases["too many submissions"] = guarded_event_stream(
            ("retry", "retry", "retry", "accepted")
        )
        cases["blocked"] = guarded_event_stream(("blocked",), "blocked marker")

        direct_output = guarded_event_stream()
        preface = json.loads(json.dumps(direct_output[-1]))
        preface["message"]["content"][0]["text"] = "unverified preface"
        direct_output.insert(0, preface)
        cases["direct output before submit"] = direct_output

        dangling = guarded_event_stream()
        del dangling[1:3]
        cases["dangling submit"] = dangling

        post_accept = guarded_event_stream()
        post_accept[-1:-1] = [
            {
                "type": "tool_execution_start",
                "toolCallId": "post-accept",
                "toolName": "bash",
                "args": {"command": "true"},
            },
            {
                "type": "tool_execution_end",
                "toolCallId": "post-accept",
                "toolName": "bash",
                "result": {"content": []},
                "isError": False,
            },
        ]
        cases["post-accept tool"] = post_accept

        final_sibling = guarded_event_stream()
        final_sibling[-1]["message"]["content"].append(
            {"type": "toolCall", "id": "late", "name": "bash", "arguments": {}}
        )
        cases["final sibling call"] = final_sibling

        orphan_end = guarded_event_stream()
        orphan_end[-1:-1] = [
            {
                "type": "tool_execution_end",
                "toolCallId": "orphan",
                "toolName": "bash",
                "result": {"content": []},
                "isError": False,
            }
        ]
        cases["orphan tool end"] = orphan_end

        for name, events in cases.items():
            with self.subTest(name=name):
                try:
                    response = run_pi_bench.parse_pi_json_events(
                        "\n".join(json.dumps(event) for event in events),
                        expect_guard=True,
                    )
                    guard = response["guard"]
                    self.assertFalse(
                        run_pi_bench.routing_safety_passed(
                            {"condition": "guarded"}, response
                        )
                    )
                except run_pi_bench.PiEventParseError as error:
                    guard = error.guard_failure
                self.assertFalse(guard["passed"])

    def test_native_progressive_reference_read_passes_routing_integrity(self):
        entrypoint = run_pi_bench.SKILL_PATH
        reference = entrypoint.parent / "references" / "semantic-preservation.md"
        events = []
        for call_id, path in (("entrypoint", entrypoint), ("reference", reference)):
            events.extend(
                (
                    {
                        "type": "tool_execution_start",
                        "toolCallId": call_id,
                        "toolName": "read",
                        "args": {"path": str(path)},
                    },
                    {
                        "type": "tool_execution_end",
                        "toolCallId": call_id,
                        "toolName": "read",
                        "isError": False,
                    },
                )
            )
        events.append(
            {
                "type": "message_end",
                "message": {
                    "role": "assistant",
                    "provider": "provider",
                    "model": "model",
                    "content": [{"type": "text", "text": "final"}],
                    "usage": {
                        "input": 1,
                        "output": 1,
                        "reasoning": 0,
                        "cacheRead": 0,
                        "cacheWrite": 0,
                        "totalTokens": 2,
                        "cost": {"total": 0},
                    },
                    "stopReason": "stop",
                },
            }
        )

        response = run_pi_bench.parse_pi_json_events(
            "\n".join(json.dumps(event) for event in events)
        )
        integrity = run_pi_bench.expected_condition_integrity(
            {
                "condition": "native-skill",
                "provider": "provider",
                "model": "model",
            },
            {"expect_skill_loaded": True},
            response,
        )

        self.assertEqual(response["routing"]["skill_entrypoint_read_calls"], 1)
        self.assertEqual(response["routing"]["skill_tree_read_calls"], 2)
        self.assertEqual(response["routing"]["outside_skill_read_calls"], 0)
        self.assertTrue(integrity["passed"])

        outside_read = json.loads(json.dumps(response))
        outside_read["routing"]["skill_tree_read_calls"] = 1
        outside_read["routing"]["outside_skill_read_calls"] = 1
        self.assertFalse(
            run_pi_bench.expected_condition_integrity(
                {
                    "condition": "native-skill",
                    "provider": "provider",
                    "model": "model",
                },
                {"expect_skill_loaded": True},
                outside_read,
            )["passed"]
        )

        non_read_tool = json.loads(json.dumps(response))
        non_read_tool["routing"]["tool_calls"] = 3
        non_read_tool["routing"]["non_read_tool_calls"] = 1
        self.assertFalse(
            run_pi_bench.expected_condition_integrity(
                {
                    "condition": "native-skill",
                    "provider": "provider",
                    "model": "model",
                },
                {"expect_skill_loaded": True},
                non_read_tool,
            )["passed"]
        )

    def test_failed_skill_read_does_not_count_as_loaded(self):
        events = [
            {
                "type": "tool_execution_start",
                "toolCallId": "failed-read",
                "toolName": "read",
                "args": {"path": str(run_pi_bench.SKILL_PATH)},
            },
            {
                "type": "tool_execution_end",
                "toolCallId": "failed-read",
                "toolName": "read",
                "result": {"content": "missing"},
                "isError": True,
            },
            {
                "type": "tool_execution_start",
                "toolCallId": "unexpected-bash",
                "toolName": "bash",
                "args": {"command": "true"},
            },
            {
                "type": "message_end",
                "message": {
                    "role": "assistant",
                    "provider": "provider",
                    "model": "model",
                    "content": [{"type": "text", "text": "final"}],
                    "usage": {
                        "input": 1,
                        "output": 1,
                        "cacheRead": 0,
                        "cacheWrite": 0,
                        "totalTokens": 2,
                        "cost": {"total": 0},
                    },
                    "stopReason": "stop",
                },
            },
        ]

        result = run_pi_bench.parse_pi_json_events(
            "\n".join(json.dumps(event) for event in events)
        )

        self.assertEqual(
            result["routing"],
            {
                "tool_calls": 2,
                "non_read_tool_calls": 1,
                "read_calls": 1,
                "successful_read_calls": 0,
                "failed_read_calls": 1,
                "skill_entrypoint_read_calls": 0,
                "skill_tree_read_calls": 0,
                "outside_skill_read_calls": 0,
                "skill_loaded": False,
            },
        )

    def test_invalid_stream_and_missing_final_text_are_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "invalid JSON.*line 2"):
            run_pi_bench.parse_pi_json_events('{}\nnot-json\n')
        with self.assertRaisesRegex(RuntimeError, "no final assistant text"):
            run_pi_bench.parse_pi_json_events(
                json.dumps(
                    {
                        "type": "message_end",
                        "message": {
                            "role": "assistant",
                            "content": [
                                {"type": "thinking", "thinking": "hidden"}
                            ],
                        },
                    }
                )
            )

        earlier_text = {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": "earlier"}],
                "stopReason": "stop",
            },
        }
        terminal_failure = {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "content": [{"type": "thinking", "thinking": "hidden"}],
                "stopReason": "length",
            },
        }
        with self.assertRaisesRegex(RuntimeError, "no final assistant text"):
            run_pi_bench.parse_pi_json_events(
                "\n".join(
                    (json.dumps(earlier_text), json.dumps(terminal_failure))
                )
            )

    def test_reasoning_metadata_is_null_when_provider_does_not_report_it(self):
        event = {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "provider": "example-provider",
                "model": "example-model",
                "content": [{"type": "text", "text": "final"}],
                "usage": {
                    "input": 2,
                    "output": 3,
                    "cacheRead": 0,
                    "cacheWrite": 0,
                    "totalTokens": 5,
                    "cost": {"total": 0},
                },
                "stopReason": "stop",
            },
        }

        result = run_pi_bench.parse_pi_json_events(json.dumps(event))

        self.assertEqual(
            result["usage"]["reasoning_tokens"],
            {"value": None, "available": False},
        )
        self.assertEqual(
            result["usage"]["visible_output_tokens"],
            {"value": None, "available": False, "derived": True},
        )


class PiInvocationTest(unittest.TestCase):
    def test_success_uses_isolated_cwd_and_returns_sanitized_event_result(self):
        event = {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "provider": "provider",
                "model": "model",
                "content": [
                    {"type": "thinking", "thinking": "never persist this"},
                    {"type": "text", "text": "final"},
                ],
                "usage": {
                    "input": 1,
                    "output": 2,
                    "reasoning": 1,
                    "cacheRead": 0,
                    "cacheWrite": 0,
                    "totalTokens": 3,
                    "cost": {"total": 0.1},
                },
                "stopReason": "stop",
            },
        }
        observed = {}

        def fake_run(command, **kwargs):
            observed["command"] = command
            observed.update(kwargs)
            self.assertEqual(list(Path(kwargs["cwd"]).iterdir()), [])
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=json.dumps(event),
                stderr="",
            )

        clock = iter((10.0, 10.125))
        result = run_pi_bench.invoke_pi(
            ["pi", "--print", "TASK"],
            300,
            run_command=fake_run,
            monotonic=lambda: next(clock),
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["duration_ms"], 125)
        self.assertEqual(result["response"]["text"], "final")
        self.assertNotIn("never persist this", json.dumps(result))
        self.assertEqual(observed["timeout"], 300)
        self.assertEqual(observed["env"]["PI_TELEMETRY"], "0")
        self.assertEqual(observed["env"]["PI_SKIP_VERSION_CHECK"], "1")
        self.assertFalse(observed["check"])

    def test_accepted_guard_tool_result_is_terminal_print_artifact(self):
        draft = "accepted draft"
        events = guarded_event_stream(("accepted",), draft)[:-1]
        command = [
            "pi",
            "--extension",
            str(run_pi_bench.GUARD_EXTENSION_PATH),
            "--no-extensions",
            "--no-skills",
            "--no-builtin-tools",
            "--no-prompt-templates",
            "--no-themes",
            "--no-context-files",
            "--no-session",
            "--no-approve",
            "--offline",
            "TASK",
        ]

        def fake_run(_command, **_kwargs):
            return subprocess.CompletedProcess(
                command,
                0,
                stdout="\n".join(json.dumps(event) for event in events),
                stderr="",
            )

        clock = iter((1.0, 1.1))
        result = run_pi_bench.invoke_pi(
            command,
            5,
            run_command=fake_run,
            monotonic=lambda: next(clock),
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["response"]["text"], draft)
        self.assertEqual(result["response"]["stop_reason"], "toolUse")
        self.assertTrue(result["response"]["guard"]["passed"])
        self.assertTrue(
            result["response"]["guard"]["terminal_artifact_valid"]
        )

    def test_guard_submission_without_final_text_preserves_terminal_guard_evidence(self):
        events = guarded_event_stream(("blocked",), "blocked marker")[:-1]
        command = [
            "pi",
            "--extension",
            str(run_pi_bench.GUARD_EXTENSION_PATH),
            "--no-extensions",
            "--no-skills",
            "--no-builtin-tools",
            "--no-prompt-templates",
            "--no-themes",
            "--no-context-files",
            "--no-session",
            "--no-approve",
            "--offline",
            "TASK",
        ]

        def fake_run(_command, **_kwargs):
            return subprocess.CompletedProcess(
                command,
                0,
                stdout="\n".join(json.dumps(event) for event in events),
                stderr="",
            )

        clock = iter((1.0, 1.1))
        result = run_pi_bench.invoke_pi(
            command,
            5,
            run_command=fake_run,
            monotonic=lambda: next(clock),
        )

        self.assertEqual(result["status"], "failure")
        self.assertTrue(result["guard_failure"]["observed"])
        self.assertFalse(result["guard_failure"]["passed"])
        self.assertEqual(
            result["guard_failure"]["submissions"][0]["result_status"],
            "blocked",
        )

    def test_nonzero_process_failure_keeps_completed_output_evidence(self):
        event = {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "provider": "provider",
                "model": "model",
                "content": [{"type": "text", "text": "partial"}],
                "usage": {
                    "input": 1,
                    "output": 1,
                    "cacheRead": 0,
                    "cacheWrite": 0,
                    "totalTokens": 2,
                    "cost": {"total": 0},
                },
                "stopReason": "stop",
            },
        }

        def fake_run(command, **_kwargs):
            return subprocess.CompletedProcess(
                command,
                7,
                stdout=json.dumps(event),
                stderr="late failure",
            )

        clock = iter((1.0, 1.1))
        result = run_pi_bench.invoke_pi(
            ["pi", "TASK"],
            5,
            run_command=fake_run,
            monotonic=lambda: next(clock),
        )

        self.assertEqual(result["status"], "failure")
        self.assertEqual(result["partial_response"]["text"], "partial")
        self.assertNotIn("thinking", json.dumps(result))
        self.assertNotIn("late failure", json.dumps(result))
        self.assertIn("stderr_sha256", result["error"]["message"])

    def test_nonzero_process_failure_keeps_bounded_error(self):
        def fake_run(command, **_kwargs):
            return subprocess.CompletedProcess(
                command,
                7,
                stdout="",
                stderr="x" * 3000,
            )

        clock = iter((1.0, 1.1))
        result = run_pi_bench.invoke_pi(
            ["pi", "TASK"],
            5,
            run_command=fake_run,
            monotonic=lambda: next(clock),
        )

        self.assertEqual(result["status"], "failure")
        self.assertEqual(result["error"]["kind"], "process")
        self.assertIn("exit 7", result["error"]["message"])
        self.assertLessEqual(len(result["error"]["message"]), 2100)


class ResumableCellTest(unittest.TestCase):
    def setUp(self):
        self.matrix = run_pi_bench.load_matrix(MATRIX_PATH)
        self.fixtures = run_pi_bench.load_fixtures(CORPUS_PATH)
        self.scenarios = run_pi_bench.load_scenarios(
            self.fixtures,
            BENCHMARK_SCENARIOS_PATH,
        )
        self.fixture = self.fixtures["release-facts-and-causes"]
        self.cell = next(run_pi_bench.iter_cells(self.matrix, self.scenarios))
        self.provenance = {
            "runner_version": "1",
            "matrix_sha256": "matrix-hash",
            "package_commit": "commit",
            "package_dirty": False,
            "pi_version": "0.84.1",
        }

    def successful_call(self):
        rewrite = self.fixture["passing_rewrites"][0]["rewrite"]
        return {
            "status": "success",
            "duration_ms": 120,
            "response": {
                "text": rewrite,
                "provider": self.cell["provider"],
                "model": self.cell["model"],
                "response_model": None,
                "stop_reason": "stop",
                "usage": {
                    "input_tokens": {"value": 10, "available": True},
                    "output_tokens": {
                        "value": 8,
                        "available": True,
                        "includes_reasoning": True,
                    },
                    "reasoning_tokens": {"value": 2, "available": True},
                    "visible_output_tokens": {
                        "value": 6,
                        "available": True,
                        "derived": True,
                    },
                    "cache_read_tokens": {"value": 0, "available": True},
                    "cache_write_tokens": {"value": 0, "available": True},
                    "total_tokens": {"value": 18, "available": True},
                },
                "cost_usd": {"value": 0.01, "available": True},
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
            },
        }

    def test_attempt_timestamp_is_captured_before_model_invocation(self):
        with tempfile.TemporaryDirectory() as directory:
            timeline = []

            def now():
                timeline.append("timestamp")
                return "2026-08-09T00:00:00Z"

            def fake_call(*_args):
                self.assertEqual(timeline, ["timestamp"])
                timeline.append("model")
                return self.successful_call()

            run_pi_bench.run_cell(
                self.cell,
                self.matrix,
                self.fixture,
                "SKILL CONTENT",
                self.provenance,
                Path(directory) / "cell.json",
                invoke=fake_call,
                now=now,
            )

        self.assertEqual(timeline[:2], ["timestamp", "model"])

    def test_returned_model_identity_is_part_of_condition_integrity(self):
        with tempfile.TemporaryDirectory() as directory:
            call = self.successful_call()
            call["response"]["provider"] = "unexpected-provider"

            run_pi_bench.run_cell(
                self.cell,
                self.matrix | {"retry_limit": 1},
                self.fixture,
                "SKILL CONTENT",
                self.provenance,
                Path(directory) / "cell.json",
                invoke=lambda *_args: call,
            )
            saved = json.loads(
                (Path(directory) / "cell.json").read_text(encoding="utf-8")
            )

        self.assertEqual(saved["status"], "failure")
        self.assertEqual(saved["last_error"]["kind"], "condition-integrity")
        self.assertEqual(
            saved["attempts"][0]["partial_response"]["provider"],
            "unexpected-provider",
        )
        self.assertNotIn("condition_integrity", saved)

    def test_routing_safety_failure_is_preserved_and_retried(self):
        self.cell = next(
            cell
            for cell in run_pi_bench.iter_cells(self.matrix, self.scenarios)
            if cell["condition"] == "native-skill"
        )
        unsafe = self.successful_call()
        unsafe["response"]["routing"] = {
            "tool_calls": 3,
            "non_read_tool_calls": 0,
            "read_calls": 3,
            "successful_read_calls": 1,
            "failed_read_calls": 2,
            "skill_entrypoint_read_calls": 1,
            "skill_tree_read_calls": 1,
            "outside_skill_read_calls": 0,
            "skill_loaded": True,
        }
        safe = self.successful_call()
        safe["response"]["routing"] = {
            "tool_calls": 2,
            "non_read_tool_calls": 0,
            "read_calls": 2,
            "successful_read_calls": 2,
            "failed_read_calls": 0,
            "skill_entrypoint_read_calls": 1,
            "skill_tree_read_calls": 2,
            "outside_skill_read_calls": 0,
            "skill_loaded": True,
        }
        calls = iter([unsafe, safe])

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cell.json"
            result = run_pi_bench.run_cell(
                self.cell,
                self.matrix,
                self.fixture,
                "SKILL CONTENT",
                self.provenance,
                path,
                invoke=lambda *_args: next(calls),
                pause=lambda _seconds: None,
            )
            document = json.loads(path.read_text())

        self.assertEqual(result["action"], "completed")
        self.assertEqual(
            [attempt["status"] for attempt in document["attempts"]],
            ["failure", "success"],
        )
        self.assertEqual(
            document["attempts"][0]["error"]["kind"], "condition-integrity"
        )
        self.assertIn("partial_response", document["attempts"][0])
        self.assertTrue(document["condition_integrity"]["passed"])

    def test_completed_guard_protocol_failure_is_not_retried_as_fresh_job(self):
        self.cell = self.cell | {"condition": "guarded"}
        matrix = self.matrix | {
            "schema_version": 2,
            "run_kind": "release-candidate",
            "judge_config_path": "release-candidate-quality-judge.json",
            "conditions": ["baseline", "native-skill", "guarded"],
            "conditions_by_scenario": {
                scenario_id: ["baseline", "native-skill", "guarded"]
                for scenario_id in self.matrix["scenario_ids"]
            },
            "semantic_gate_conditions": ["native-skill", "guarded"],
            "max_parallel_calls": 3,
            "max_parallel_calls_by_provider": {
                "openai-codex": 1,
                "github-copilot": 2,
            },
            "acceptance_thresholds": {
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
            "isolation": self.matrix["isolation"]
            | {
                "tools_by_condition": {
                    "baseline": [],
                    "native-skill": ["read"],
                    "guarded": [],
                }
            },
        }
        call = self.successful_call()
        text = "Guard blocked rewrite after one failed submission."
        sha = lambda value: hashlib.sha256(value.encode()).hexdigest()
        call["response"].update(
            text=text,
            guard={
                "observed": True,
                "max_submissions": 3,
                "submissions": [
                    {
                        "sequence": 1,
                        "tool_call_id_sha256": sha("call"),
                        "job_id_sha256": sha("job"),
                        "draft_sha256": sha("rejected"),
                        "draft_bytes": len("rejected"),
                        "result_status": "blocked",
                        "result_attempt": 1,
                        "result_draft_sha256": None,
                        "result_text_sha256": sha(text),
                        "is_error": False,
                        "submission_message_valid": True,
                    }
                ],
                "accepted_submission": None,
                "accepted_draft_sha256": None,
                "final_text_sha256": sha(text),
                "exact_accepted_output": False,
                "malformed_submission_messages": 0,
                "direct_output_messages": 0,
                "unauthorized_tool_calls": 0,
                "unmatched_tool_events": 0,
                "ambient_resources_disabled": True,
                "terminal_artifact_valid": True,
                "same_job_id": True,
                "attempts_contiguous": True,
                "passed": False,
            },
            routing={
                "tool_calls": 1,
                "non_read_tool_calls": 1,
                "read_calls": 0,
                "successful_read_calls": 0,
                "failed_read_calls": 0,
                "skill_entrypoint_read_calls": 0,
                "skill_tree_read_calls": 0,
                "outside_skill_read_calls": 0,
                "skill_loaded": False,
            },
        )
        invocations = 0

        def invoke(*_args):
            nonlocal invocations
            invocations += 1
            return call

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cell.json"
            result = run_pi_bench.run_cell(
                self.cell,
                matrix,
                self.fixture,
                "SKILL CONTENT",
                self.provenance,
                path,
                invoke=invoke,
                pause=lambda _seconds: None,
            )
            document = json.loads(path.read_text())
            resumed = run_pi_bench.run_cell(
                self.cell,
                matrix,
                self.fixture,
                "SKILL CONTENT",
                self.provenance,
                path,
                invoke=lambda *_args: self.fail(
                    "completed guard protocol was invoked after resume"
                ),
            )

        self.assertEqual(result["action"], "failed")
        self.assertEqual(invocations, 1)
        self.assertEqual(len(document["attempts"]), 1)
        self.assertEqual(resumed["action"], "failed")

    def test_failure_is_saved_before_retry_then_success_completes_cell(self):
        with tempfile.TemporaryDirectory() as directory:
            raw_path = Path(directory) / "cell.json"
            calls = []

            def fake_call(command, timeout_seconds):
                calls.append((command, timeout_seconds))
                if len(calls) == 1:
                    return {
                        "status": "failure",
                        "duration_ms": 50,
                        "error": {"kind": "process", "message": "temporary"},
                    }
                saved = json.loads(raw_path.read_text(encoding="utf-8"))
                self.assertEqual(saved["status"], "failure")
                self.assertEqual(len(saved["attempts"]), 1)
                return self.successful_call()

            result = run_pi_bench.run_cell(
                self.cell,
                self.matrix,
                self.fixture,
                "SKILL CONTENT",
                self.provenance,
                raw_path,
                invoke=fake_call,
                pause=lambda _seconds: None,
                now=lambda: "2026-08-09T00:00:00Z",
            )

            saved = json.loads(raw_path.read_text(encoding="utf-8"))

        self.assertEqual(result["action"], "completed")
        self.assertEqual(len(calls), 2)
        self.assertEqual(saved["status"], "success")
        self.assertEqual(saved["cell"], self.cell)
        self.assertEqual(saved["provenance"], self.provenance)
        self.assertEqual(
            [attempt["status"] for attempt in saved["attempts"]],
            ["failure", "success"],
        )
        self.assertTrue(saved["evaluation"]["semantic_gate_passed"])
        self.assertEqual(saved["response"]["text"], self.successful_call()["response"]["text"])
        self.assertEqual(len(saved["prompt_sha256"]), 64)

    def test_partial_completed_output_remains_visible_after_exhausted_retries(self):
        with tempfile.TemporaryDirectory() as directory:
            raw_path = Path(directory) / "cell.json"
            calls = iter(
                (
                    {
                        "status": "failure",
                        "duration_ms": 10,
                        "error": {
                            "kind": "stop-reason",
                            "message": "Pi stopped with 'length'.",
                        },
                        "partial_response": self.successful_call()["response"]
                        | {"stop_reason": "length"},
                    },
                    {
                        "status": "failure",
                        "duration_ms": 20,
                        "error": {"kind": "process", "message": "failed"},
                    },
                )
            )

            result = run_pi_bench.run_cell(
                self.cell,
                self.matrix,
                self.fixture,
                "SKILL CONTENT",
                self.provenance,
                raw_path,
                invoke=lambda *_args: next(calls),
                pause=lambda _seconds: None,
            )
            saved = json.loads(raw_path.read_text(encoding="utf-8"))

        self.assertEqual(result["action"], "failed")
        self.assertEqual(saved["status"], "failure")
        self.assertEqual(
            saved["attempts"][0]["partial_response"]["text"],
            self.successful_call()["response"]["text"],
        )
        self.assertTrue(
            saved["attempts"][0]["partial_evaluation"]["semantic_gate_passed"]
        )
        self.assertNotIn("partial_response", saved["attempts"][1])

    def test_failure_attempt_history_resumes_but_stale_provenance_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            raw_path = Path(directory) / "cell.json"
            failed = {
                "schema_version": 1,
                "status": "failure",
                "cell": self.cell,
                "provenance": self.provenance,
                "prompt_sha256": run_pi_bench.expected_prompt_sha256(
                    self.cell,
                    self.matrix,
                    self.fixture,
                    "SKILL CONTENT",
                ),
                "attempts": [
                    {
                        "number": 1,
                        "started_at": "2026-08-09T00:00:00Z",
                        "status": "failure",
                        "duration_ms": 1,
                        "error": {"kind": "process", "message": "old"},
                    }
                ],
                "last_error": {"kind": "process", "message": "old"},
                "updated_at": "2026-08-09T00:00:01Z",
            }
            raw_path.write_text(json.dumps(failed), encoding="utf-8")

            run_pi_bench.run_cell(
                self.cell,
                self.matrix | {"retry_limit": 1},
                self.fixture,
                "SKILL CONTENT",
                self.provenance,
                raw_path,
                invoke=lambda *_args: self.successful_call(),
            )
            resumed = json.loads(raw_path.read_text(encoding="utf-8"))
            self.assertEqual(
                [attempt["number"] for attempt in resumed["attempts"]],
                [1, 2],
            )

            resumed["provenance"] = self.provenance | {
                "package_commit": "different"
            }
            raw_path.write_text(json.dumps(resumed), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "stale raw result"):
                run_pi_bench.run_cell(
                    self.cell,
                    self.matrix,
                    self.fixture,
                    "SKILL CONTENT",
                    self.provenance,
                    raw_path,
                    invoke=lambda *_args: self.fail("stale cell must not run"),
                )

    def test_invalid_existing_raw_cell_is_reported_without_overwrite(self):
        invalid_documents = (
            "not-json",
            json.dumps([]),
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "success",
                    "cell": self.cell,
                    "provenance": self.provenance,
                    "attempts": [],
                }
            ),
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "failure",
                    "cell": self.cell,
                    "provenance": self.provenance,
                    "attempts": [1],
                }
            ),
        )
        for content in invalid_documents:
            with self.subTest(content=content[:20]):
                with tempfile.TemporaryDirectory() as directory:
                    raw_path = Path(directory) / "cell.json"
                    raw_path.write_text(content, encoding="utf-8")

                    with self.assertRaisesRegex(RuntimeError, "invalid raw result"):
                        run_pi_bench.run_cell(
                            self.cell,
                            self.matrix,
                            self.fixture,
                            "SKILL CONTENT",
                            self.provenance,
                            raw_path,
                            invoke=lambda *_args: self.fail(
                                "invalid cell must not run"
                            ),
                        )
                    self.assertEqual(
                        raw_path.read_text(encoding="utf-8"),
                        content,
                    )

    def test_matching_success_is_recomputed_before_resume_skip(self):
        with tempfile.TemporaryDirectory() as directory:
            raw_path = Path(directory) / "cell.json"
            run_pi_bench.run_cell(
                self.cell,
                self.matrix | {"retry_limit": 1},
                self.fixture,
                "SKILL CONTENT",
                self.provenance,
                raw_path,
                invoke=lambda *_args: self.successful_call(),
            )
            valid = json.loads(raw_path.read_text(encoding="utf-8"))
            mutations = []

            document = json.loads(json.dumps(valid))
            document.pop("prompt_sha256")
            mutations.append(document)

            document = json.loads(json.dumps(valid))
            document["response"]["provider"] = "forged-provider"
            mutations.append(document)

            document = json.loads(json.dumps(valid))
            document["evaluation"]["semantic_gate_passed"] = False
            mutations.append(document)

            document = json.loads(json.dumps(valid))
            document["response"]["stop_reason"] = "length"
            mutations.append(document)

            document = json.loads(json.dumps(valid))
            document["attempts"][-1]["error"] = {
                "kind": "stop-reason",
                "message": "length",
            }
            mutations.append(document)

            document = json.loads(json.dumps(valid))
            document["last_error"] = {
                "kind": "stop-reason",
                "message": "length",
            }
            mutations.append(document)

            document = json.loads(json.dumps(valid))
            document["response"]["routing"] = {
                "tool_calls": 1,
                "non_read_tool_calls": 0,
                "read_calls": 1,
                "successful_read_calls": 1,
                "failed_read_calls": 0,
                "skill_entrypoint_read_calls": 1,
                "skill_tree_read_calls": 1,
                "outside_skill_read_calls": 0,
                "skill_loaded": True,
            }
            mutations.append(document)

            document = json.loads(json.dumps(valid))
            document["response"]["thinking"] = "SECRET CHAIN"
            mutations.append(document)

            for mutation_index, document in enumerate(mutations):
                with self.subTest(mutation=mutation_index):
                    raw_path.write_text(json.dumps(document), encoding="utf-8")
                    with self.assertRaisesRegex(RuntimeError, "invalid raw result"):
                        run_pi_bench.run_cell(
                            self.cell,
                            self.matrix,
                            self.fixture,
                            "SKILL CONTENT",
                            self.provenance,
                            raw_path,
                            invoke=lambda *_args: self.fail(
                                "forged success must not be skipped"
                            ),
                        )

    def test_existing_matching_success_is_skipped_without_model_call(self):
        with tempfile.TemporaryDirectory() as directory:
            raw_path = Path(directory) / "cell.json"
            run_pi_bench.run_cell(
                self.cell,
                self.matrix | {"retry_limit": 1},
                self.fixture,
                "SKILL CONTENT",
                self.provenance,
                raw_path,
                invoke=lambda *_args: self.successful_call(),
            )

            result = run_pi_bench.run_cell(
                self.cell,
                self.matrix,
                self.fixture,
                "SKILL CONTENT",
                self.provenance,
                raw_path,
                invoke=lambda *_args: self.fail("model call must be skipped"),
            )

        self.assertEqual(result["action"], "skipped")


class AggregationTest(unittest.TestCase):
    def test_activation_acceptance_uses_two_of_three_positive_threshold(self):
        matrix = run_pi_bench.load_matrix(MATRIX_PATH) | {
            "models": [run_pi_bench.load_matrix(MATRIX_PATH)["models"][0]],
            "scenario_ids": ["positive"],
            "repetitions": 3,
        }
        fixtures = {"positive": {"expect_skill_loaded": True}}

        def rows(values):
            return [
                {
                    "cell": {
                        "provider": matrix["models"][0]["provider"],
                        "model": matrix["models"][0]["model"],
                        "thinking": matrix["models"][0]["thinking"],
                        "condition": "native-skill",
                        "scenario_id": "positive",
                        "repetition": index,
                    },
                    "response": {"routing": {"skill_loaded": loaded}},
                }
                for index, loaded in enumerate(values, 1)
            ]

        accepted = run_pi_bench.aggregate_activation(
            matrix, fixtures, rows([True, True, False])
        )
        rejected = run_pi_bench.aggregate_activation(
            matrix, fixtures, rows([True, False, False])
        )

        self.assertTrue(accepted["accepted"])
        self.assertEqual(accepted["groups_passed"], 1)
        self.assertFalse(rejected["accepted"])
        self.assertEqual(rejected["groups_passed"], 0)

    def test_activation_acceptance_rejects_any_negative_fixture_load(self):
        matrix = run_pi_bench.load_matrix(MATRIX_PATH) | {
            "models": [run_pi_bench.load_matrix(MATRIX_PATH)["models"][0]],
            "scenario_ids": ["negative"],
            "repetitions": 3,
        }
        fixtures = {"negative": {"expect_skill_loaded": False}}
        rows = [
            {
                "cell": {
                    "provider": matrix["models"][0]["provider"],
                    "model": matrix["models"][0]["model"],
                    "thinking": matrix["models"][0]["thinking"],
                    "condition": "native-skill",
                    "scenario_id": "negative",
                    "repetition": index,
                },
                "response": {"routing": {"skill_loaded": loaded}},
            }
            for index, loaded in enumerate([False, False, True], 1)
        ]

        result = run_pi_bench.aggregate_activation(matrix, fixtures, rows)

        self.assertFalse(result["accepted"])
        self.assertEqual(result["groups_passed"], 0)

    def test_partial_completed_outputs_are_included_as_failure_evidence(self):
        matrix = run_pi_bench.load_matrix(MATRIX_PATH)
        matrix = matrix | {
            "models": [matrix["models"][0]],
            "scenario_ids": ["release-facts-and-causes"],
            "repetitions": 3,
        }
        fixtures = run_pi_bench.load_fixtures(CORPUS_PATH)
        fixture = fixtures["release-facts-and-causes"]
        provenance = {
            "runner_version": "1",
            "matrix_sha256": "hash",
            "package_commit": "commit",
            "package_dirty": False,
            "pi_version": "0.84.1",
        }
        cell = next(run_pi_bench.iter_cells(matrix, fixtures))
        rewrite = fixture["passing_rewrites"][0]["rewrite"]
        partial_evaluation = run_pi_bench.evaluate_candidate(
            fixture,
            rewrite,
            matrix["output_contract"],
            run_pi_bench.raw_result_name(cell),
        )
        document = {
            "schema_version": 1,
            "status": "failure",
            "cell": cell,
            "provenance": provenance,
            "prompt_sha256": run_pi_bench.expected_prompt_sha256(
                cell,
                matrix,
                fixture,
                "SKILL CONTENT",
            ),
            "attempts": [
                {
                    "number": 1,
                    "started_at": "2026-08-09T00:00:00Z",
                    "status": "failure",
                    "duration_ms": 10,
                    "error": {"kind": "stop-reason", "message": "length"},
                    "partial_response": {
                        "text": rewrite,
                        "provider": cell["provider"],
                        "model": cell["model"],
                        "response_model": None,
                        "stop_reason": "length",
                        "usage": {
                            "input_tokens": {"value": 10, "available": True},
                            "output_tokens": {
                                "value": 8,
                                "available": True,
                                "includes_reasoning": True,
                            },
                            "reasoning_tokens": {"value": 2, "available": True},
                            "visible_output_tokens": {
                                "value": 6,
                                "available": True,
                                "derived": True,
                            },
                            "cache_read_tokens": {"value": 0, "available": True},
                            "cache_write_tokens": {"value": 0, "available": True},
                            "total_tokens": {"value": 18, "available": True},
                        },
                        "cost_usd": {"value": 0.01, "available": True},
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
                    },
                    "partial_evaluation": partial_evaluation,
                }
            ],
            "last_error": {"kind": "stop-reason", "message": "length"},
            "updated_at": "2026-08-09T00:00:01Z",
        }

        with tempfile.TemporaryDirectory() as directory:
            raw_directory = Path(directory)
            (raw_directory / run_pi_bench.raw_result_name(cell)).write_text(
                json.dumps(document),
                encoding="utf-8",
            )
            results = run_pi_bench.aggregate_results(
                matrix,
                fixtures,
                provenance,
                raw_directory,
                skill_text="SKILL CONTENT",
            )

        self.assertEqual(
            results["partial_outputs"],
            [
                {
                    "cell": cell,
                    "attempt": 1,
                    "stop_reason": "length",
                    "semantic_gate_passed": True,
                }
            ],
        )
        failed = next(item for item in results["unresolved"] if item["kind"] == "failed")
        self.assertEqual(failed["completed_outputs"], 1)

    def test_aggregation_keeps_incomplete_cells_visible_and_reports_variance(self):
        matrix = run_pi_bench.load_matrix(MATRIX_PATH)
        matrix = matrix | {
            "models": [matrix["models"][0]],
            "scenario_ids": ["release-facts-and-causes"],
            "repetitions": 2,
        }
        fixtures = run_pi_bench.load_fixtures(CORPUS_PATH)
        fixture = fixtures["release-facts-and-causes"]
        provenance = {
            "runner_version": "1",
            "matrix_sha256": "hash",
            "package_commit": "commit",
            "package_dirty": False,
            "pi_version": "0.84.1",
        }
        rewrite = fixture["passing_rewrites"][0]["rewrite"]

        with tempfile.TemporaryDirectory() as directory:
            raw_directory = Path(directory)
            cells = list(run_pi_bench.iter_cells(matrix, fixtures))
            for index, cell in enumerate(cells[:-1], 1):
                evaluation = run_pi_bench.evaluate_candidate(
                    fixture,
                    rewrite,
                    matrix["output_contract"],
                    run_pi_bench.raw_result_name(cell),
                )
                document = {
                    "schema_version": 1,
                    "status": "success",
                    "cell": cell,
                    "provenance": provenance,
                    "prompt_sha256": run_pi_bench.expected_prompt_sha256(
                        cell,
                        matrix,
                        fixture,
                        "SKILL CONTENT",
                    ),
                    "duration_ms": 100 * index,
                    "attempts": (
                        (
                            [
                                {
                                    "number": 1,
                                    "started_at": "2026-08-09T00:00:00Z",
                                    "status": "failure",
                                    "duration_ms": 20,
                                    "error": {
                                        "kind": "stop-reason",
                                        "message": "length",
                                    },
                                    "partial_response": {
                                        "text": rewrite,
                                        "provider": cell["provider"],
                                        "model": cell["model"],
                                        "response_model": None,
                                        "stop_reason": "length",
                                        "usage": {
                                            "input_tokens": {
                                                "value": 10,
                                                "available": True,
                                            },
                                            "output_tokens": {
                                                "value": 8,
                                                "available": True,
                                                "includes_reasoning": True,
                                            },
                                            "reasoning_tokens": {
                                                "value": 2,
                                                "available": True,
                                            },
                                            "visible_output_tokens": {
                                                "value": 6,
                                                "available": True,
                                                "derived": True,
                                            },
                                            "cache_read_tokens": {
                                                "value": 0,
                                                "available": True,
                                            },
                                            "cache_write_tokens": {
                                                "value": 0,
                                                "available": True,
                                            },
                                            "total_tokens": {
                                                "value": 18,
                                                "available": True,
                                            },
                                        },
                                        "cost_usd": {
                                            "value": 0.01,
                                            "available": True,
                                        },
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
                                    },
                                    "partial_evaluation": evaluation,
                                }
                            ]
                            if index == 1
                            else []
                        )
                        + [
                            {
                                "number": 2 if index == 1 else 1,
                                "started_at": "2026-08-09T00:00:01Z",
                                "status": "success",
                                "duration_ms": 100 * index,
                            }
                        ]
                    ),
                    "condition_integrity": {
                        "model_identity_passed": True,
                        "expected_skill_loaded": cell["condition"] == "native-skill",
                        "skill_loading_passed": True,
                        "passed": True,
                    },
                    "response": {
                        "text": rewrite,
                        "provider": cell["provider"],
                        "model": cell["model"],
                        "response_model": None,
                        "stop_reason": "stop",
                        "usage": {
                            "input_tokens": {"value": 10 * index, "available": True},
                            "output_tokens": {
                                "value": 8,
                                "available": True,
                                "includes_reasoning": True,
                            },
                            "reasoning_tokens": {
                                "value": None if index == 1 else 2,
                                "available": index != 1,
                            },
                            "visible_output_tokens": {
                                "value": None if index == 1 else 6,
                                "available": index != 1,
                                "derived": True,
                            },
                            "cache_read_tokens": {"value": 0, "available": True},
                            "cache_write_tokens": {"value": 0, "available": True},
                            "total_tokens": {"value": 18, "available": True},
                        },
                        "cost_usd": {"value": 0.01 * index, "available": True},
                        "routing": {
                            "tool_calls": 1 if cell["condition"] == "native-skill" else 0,
                            "non_read_tool_calls": 0,
                            "read_calls": 1 if cell["condition"] == "native-skill" else 0,
                            "successful_read_calls": 1 if cell["condition"] == "native-skill" else 0,
                            "failed_read_calls": 0,
                            "skill_entrypoint_read_calls": 1 if cell["condition"] == "native-skill" else 0,
                            "skill_tree_read_calls": 1 if cell["condition"] == "native-skill" else 0,
                            "outside_skill_read_calls": 0,
                            "skill_loaded": cell["condition"] == "native-skill",
                        },
                    },
                    "evaluation": evaluation,
                    "updated_at": "2026-08-09T00:00:02Z",
                }
                path = raw_directory / run_pi_bench.raw_result_name(cell)
                path.write_text(json.dumps(document), encoding="utf-8")

            results = run_pi_bench.aggregate_results(
                matrix,
                fixtures,
                provenance,
                raw_directory,
                generated_at="2026-08-09T00:00:00Z",
                skill_text="SKILL CONTENT",
            )

        self.assertEqual(
            results["completeness"],
            {
                "expected": 6,
                "successful": 5,
                "failed": 0,
                "missing": 1,
                "stale": 0,
                "invalid": 0,
                "complete": False,
            },
        )
        self.assertEqual(
            results["condition_integrity"],
            {
                "expected_samples": 6,
                "successful_samples": 5,
                "integrity_passed_samples": 5,
                "model_identity_passed_samples": 5,
                "routing_safety_passed_samples": 5,
                "activation_groups_expected": 1,
                "activation_groups_passed": 1,
                "expected_native_samples": 2,
                "successful_native_samples": 2,
                "expected_skill_loaded_samples": 2,
                "skill_loaded_samples": 2,
                "accepted": False,
            },
        )
        self.assertEqual(
            results["semantic_acceptance"],
            {
                "conditions": ["native-skill"],
                "expected_samples": 2,
                "successful_samples": 2,
                "passed_samples": 2,
                "failed_samples": 0,
                "accepted": True,
            },
        )
        self.assertEqual(len(results["partial_outputs"]), 1)
        self.assertEqual(results["partial_outputs"][0]["cell"], cells[0])
        self.assertEqual(len(results["condition_results"]), 3)
        baseline = results["condition_results"][0]
        keys = list(baseline)
        self.assertLess(keys.index("semantic"), keys.index("style"))
        self.assertLess(keys.index("style"), keys.index("operations"))
        self.assertEqual(baseline["runs"], 2)
        self.assertEqual(baseline["semantic"]["samples_passed"], 2)
        self.assertEqual(baseline["style"]["warning_count"], 0)
        self.assertEqual(
            baseline["operations"]["input_tokens"],
            {
                "available_runs": 2,
                "missing_runs": 0,
                "sum": 30,
                "mean": 15,
                "stddev": 5.0,
            },
        )
        self.assertEqual(
            baseline["operations"]["reasoning_tokens"]["available_runs"],
            1,
        )
        self.assertEqual(results["unresolved"][0]["kind"], "missing")


class CliTest(unittest.TestCase):
    def test_exit_acceptance_requires_completeness_integrity_and_semantics(self):
        base = {
            "completeness": {"complete": True},
            "condition_integrity": {"accepted": True},
            "semantic_acceptance": {"accepted": True},
        }

        self.assertTrue(run_pi_bench.benchmark_accepted(base))
        for section, key in (
            ("completeness", "complete"),
            ("condition_integrity", "accepted"),
            ("semantic_acceptance", "accepted"),
        ):
            with self.subTest(section=section):
                result = json.loads(json.dumps(base))
                result[section][key] = False
                self.assertFalse(run_pi_bench.benchmark_accepted(result))

    def test_report_only_cli_writes_report_and_exits_one_when_incomplete(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [
                    sys.executable,
                    str(EVALS_DIR / "run_pi_bench.py"),
                    "--matrix",
                    str(MATRIX_PATH),
                    "--results-dir",
                    directory,
                    "--report-only",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            results = json.loads(
                (Path(directory) / "results.json").read_text(encoding="utf-8")
            )

        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertFalse(results["completeness"]["complete"])
        self.assertIn("INCOMPLETE", result.stdout)


class OrchestrationTest(unittest.TestCase):
    def test_schema_v2_generation_runs_preregistered_cells_in_parallel(self):
        matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        matrix["schema_version"] = 2
        matrix["run_kind"] = "release-candidate"
        matrix["judge_config_path"] = "release-candidate-quality-judge.json"
        matrix["scenario_ids"] = [matrix["scenario_ids"][0]]
        matrix["conditions"] = ["baseline", "native-skill", "guarded"]
        matrix["conditions_by_scenario"] = {
            matrix["scenario_ids"][0]: ["baseline", "native-skill"],
        }
        matrix["semantic_gate_conditions"] = ["native-skill"]
        matrix["isolation"]["tools_by_condition"] = {
            "baseline": [],
            "native-skill": ["read"],
            "guarded": [],
        }
        matrix["max_parallel_calls"] = 3
        matrix["max_parallel_calls_by_provider"] = {
            "openai-codex": 1,
            "github-copilot": 2,
        }
        matrix["acceptance_thresholds"] = {
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
        }
        provenance = {
            "runner_version": "1",
            "matrix_sha256": "hash",
            "package_commit": "commit",
            "package_dirty": False,
            "skill_sha256": run_pi_bench.tree_sha256(run_pi_bench.SKILL_DIR),
            "extension_sha256": run_pi_bench.tree_sha256(ROOT / "extensions"),
            "pi_version": "0.84.1",
        }
        lock = threading.Lock()
        active = 0
        max_active = 0

        snapshot_extensions = set()

        def fake_cell(*_args, guard_extension_path, **_kwargs):
            nonlocal active, max_active
            snapshot_extensions.add(guard_extension_path)
            self.assertNotEqual(
                guard_extension_path,
                run_pi_bench.GUARD_EXTENSION_PATH,
            )
            self.assertEqual(
                run_pi_bench.tree_sha256(guard_extension_path.parent),
                provenance["extension_sha256"],
            )
            with lock:
                active += 1
                max_active = max(max_active, active)
            time.sleep(0.03)
            with lock:
                active -= 1
            return {"action": "skipped", "path": "unused"}

        with tempfile.TemporaryDirectory(dir=EVALS_DIR) as directory:
            matrix_path = Path(directory) / "parallel-matrix.json"
            matrix_path.write_text(json.dumps(matrix), encoding="utf-8")
            provenance.update(run_pi_bench.evaluation_resource_hashes(matrix))
            run_pi_bench.execute_benchmark(
                matrix_path,
                Path(directory) / "results",
                provenance=provenance,
                run_cell_function=fake_cell,
                pause=lambda _seconds: None,
                emit=lambda _message: None,
                attest_no_prior_candidate_output=True,
            )

        self.assertEqual(max_active, 3)
        self.assertEqual(len(snapshot_extensions), 1)

    def test_generation_uses_immutable_skill_snapshot_for_every_cell(self):
        provenance = {
            "runner_version": "1",
            "matrix_sha256": hashlib.sha256(MATRIX_PATH.read_bytes()).hexdigest(),
            "package_commit": "commit",
            "package_dirty": False,
            "skill_sha256": run_pi_bench.tree_sha256(run_pi_bench.SKILL_DIR),
            "pi_version": "0.84.1",
        }
        snapshots = set()

        def fake_cell(*_args, skill_dir, **_kwargs):
            snapshots.add(skill_dir)
            self.assertNotEqual(skill_dir, run_pi_bench.SKILL_DIR)
            self.assertEqual(
                run_pi_bench.tree_sha256(skill_dir),
                provenance["skill_sha256"],
            )
            return {"action": "skipped", "path": "unused"}

        with tempfile.TemporaryDirectory() as directory:
            run_pi_bench.execute_benchmark(
                MATRIX_PATH,
                Path(directory),
                provenance=provenance,
                run_cell_function=fake_cell,
                pause=lambda _seconds: None,
                emit=lambda _message: None,
            )

        self.assertEqual(len(snapshots), 1)

    def test_generation_refuses_dirty_package_provenance(self):
        provenance = {
            "runner_version": "1",
            "matrix_sha256": "hash",
            "package_commit": "commit",
            "package_dirty": True,
            "pi_version": "0.84.1",
        }

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "clean git working tree"):
                run_pi_bench.execute_benchmark(
                    MATRIX_PATH,
                    Path(directory),
                    provenance=provenance,
                    run_cell_function=lambda *_args, **_kwargs: self.fail(
                        "dirty run must not invoke a model"
                    ),
                    pause=lambda _seconds: None,
                    emit=lambda _message: None,
                )

    def test_report_only_never_invokes_model_and_returns_incomplete_results(self):
        provenance = {
            "runner_version": "1",
            "matrix_sha256": hashlib.sha256(MATRIX_PATH.read_bytes()).hexdigest(),
            "package_commit": "commit",
            "package_dirty": True,
            "pi_version": "0.84.1",
        }

        with tempfile.TemporaryDirectory() as directory:
            results = run_pi_bench.execute_benchmark(
                MATRIX_PATH,
                Path(directory),
                report_only=True,
                provenance=provenance,
                run_cell_function=lambda *_args, **_kwargs: self.fail(
                    "report-only must not invoke a model"
                ),
                emit=lambda _message: None,
            )

        self.assertFalse(results["completeness"]["complete"])
        self.assertEqual(results["completeness"]["missing"], 162)


class ReportWritingTest(unittest.TestCase):
    def test_report_puts_semantics_before_style_and_keeps_failures_visible(self):
        operations = {
            name: {
                "available_runs": 1,
                "missing_runs": 0,
                "sum": 1,
                "mean": 1,
                "stddev": 0.0,
            }
            for name in (
                "input_tokens",
                "output_tokens",
                "reasoning_tokens",
                "visible_output_tokens",
                "cost_usd",
                "duration_ms",
            )
        }
        operations["routing"] = {"applicable_runs": 0, "skill_loaded_runs": 0}
        results = {
            "schema_version": 1,
            "generated_at": "2026-08-09T00:00:00Z",
            "provenance": {
                "runner_version": "1",
                "matrix_sha256": "hash",
                "package_commit": "commit",
                "package_dirty": False,
                "pi_version": "0.84.1",
            },
            "matrix": {
                "id": "v1",
                "version": 1,
                "conditions": ["baseline"],
                "repetitions": 3,
            },
            "completeness": {
                "expected": 2,
                "successful": 1,
                "failed": 0,
                "missing": 1,
                "stale": 0,
                "invalid": 0,
                "complete": False,
            },
            "condition_integrity": {
                "expected_samples": 2,
                "successful_samples": 1,
                "integrity_passed_samples": 1,
                "model_identity_passed_samples": 1,
                "routing_safety_passed_samples": 1,
                "activation_groups_expected": 1,
                "activation_groups_passed": 0,
                "expected_native_samples": 1,
                "successful_native_samples": 0,
                "expected_skill_loaded_samples": 1,
                "skill_loaded_samples": 0,
                "accepted": False,
            },
            "semantic_acceptance": {
                "conditions": ["native-skill", "direct-prompt"],
                "expected_samples": 2,
                "successful_samples": 1,
                "passed_samples": 1,
                "failed_samples": 0,
                "accepted": False,
            },
            "condition_results": [
                {
                    "provider": "provider",
                    "model": "model",
                    "thinking": "medium",
                    "condition": "baseline",
                    "runs": 1,
                    "semantic": {
                        "samples_passed": 1,
                        "samples_failed": 0,
                        "metrics": {},
                        "procedure": {
                            "applicable_samples": 0,
                            "passed_samples": 0,
                            "failed_samples": 0,
                        },
                        "output_contract": {
                            "passed_samples": 1,
                            "failed_samples": 0,
                        },
                    },
                    "style": {
                        "advisory": True,
                        "warning_count": 2,
                        "warnings_by_rule": {"sentence-length": 2},
                    },
                    "operations": operations,
                }
            ],
            "unresolved": [
                {
                    "kind": "missing",
                    "cell": {
                        "provider": "provider",
                        "model": "model",
                        "thinking": "medium",
                        "condition": "baseline",
                        "scenario_id": "scenario",
                        "repetition": 2,
                    },
                }
            ],
        }

        with tempfile.TemporaryDirectory() as directory:
            results_directory = Path(directory)
            run_pi_bench.write_reports(
                results,
                results_directory,
                matrix_path=MATRIX_PATH,
            )
            markdown = (results_directory / "RESULTS.md").read_text(
                encoding="utf-8"
            )
            saved_json = json.loads(
                (results_directory / "results.json").read_text(encoding="utf-8")
            )
            failures = json.loads(
                (results_directory / "failures.json").read_text(encoding="utf-8")
            )

        self.assertEqual(saved_json, results)
        self.assertEqual(failures, results["unresolved"])
        self.assertIn("INCOMPLETE", markdown)
        self.assertIn("Condition integrity: NOT ACCEPTED", markdown)
        self.assertIn("Semantic acceptance: NOT ACCEPTED", markdown)
        self.assertIn("Model identity matches: 1/2", markdown)
        self.assertIn("Native skill loads: 0/1", markdown)
        self.assertLess(markdown.index("## Semantic"), markdown.index("## Style"))
        self.assertLess(
            markdown.index("## Style"),
            markdown.index("## Usage, cost, and duration"),
        )
        self.assertNotIn("overall score", markdown.lower())
        self.assertIn("python3 evals/run_pi_bench.py", markdown)
        self.assertIn("does not certify ASD-STE100 compliance", markdown)


class ProvenanceTest(unittest.TestCase):
    def test_records_matrix_hash_package_commit_dirty_state_and_pi_version(self):
        calls = []

        def fake_run(command, **kwargs):
            calls.append((command, kwargs))
            outputs = {
                ("git", "rev-parse", "HEAD"): "abc123\n",
                ("git", "status", "--porcelain"): " M file\n",
                ("pi", "--version"): "0.84.1\n",
            }
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=outputs[tuple(command)],
                stderr="",
            )

        provenance = run_pi_bench.collect_provenance(
            MATRIX_PATH,
            run_command=fake_run,
        )

        expected_hash = hashlib.sha256(MATRIX_PATH.read_bytes()).hexdigest()
        self.assertEqual(
            provenance,
            {
                "runner_version": run_pi_bench.RUNNER_VERSION,
                "matrix_sha256": expected_hash,
                "package_commit": "abc123",
                "package_dirty": True,
                "skill_sha256": run_pi_bench.tree_sha256(run_pi_bench.SKILL_DIR),
                "pi_version": "0.84.1",
            },
        )
        self.assertEqual(len(calls), 3)
        self.assertTrue(all(call[1]["check"] for call in calls))


    def test_schema_v2_provenance_hashes_guard_extension_runtime(self):
        matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        matrix["schema_version"] = 2
        matrix["run_kind"] = "release-candidate"
        matrix["judge_config_path"] = "release-candidate-quality-judge.json"
        matrix["conditions"] = ["baseline", "native-skill", "guarded"]
        matrix["conditions_by_scenario"] = {
            scenario_id: ["baseline", "native-skill"]
            for scenario_id in matrix["scenario_ids"]
        }
        matrix["semantic_gate_conditions"] = ["native-skill"]
        matrix["isolation"]["tools_by_condition"] = {
            "baseline": [],
            "native-skill": ["read"],
            "guarded": [],
        }
        matrix["max_parallel_calls"] = 3
        matrix["max_parallel_calls_by_provider"] = {
            "openai-codex": 1,
            "github-copilot": 2,
        }
        matrix["acceptance_thresholds"] = {
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
        }

        def fake_run(command, **_kwargs):
            outputs = {
                ("git", "rev-parse", "HEAD"): "abc123\n",
                ("git", "status", "--porcelain"): "",
                ("pi", "--version"): "0.84.1\n",
            }
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=outputs[tuple(command)],
                stderr="",
            )

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "matrix.json"
            path.write_text(json.dumps(matrix), encoding="utf-8")
            provenance = run_pi_bench.collect_provenance(path, run_command=fake_run)

        self.assertEqual(
            provenance["extension_sha256"],
            run_pi_bench.tree_sha256(ROOT / "extensions"),
        )
        resources = run_pi_bench.evaluation_resource_hashes(matrix)
        self.assertEqual(
            {key: provenance[key] for key in resources},
            resources,
        )
        self.assertEqual(
            provenance["preregistered_judge_config_path"],
            matrix["judge_config_path"],
        )


class OutputContractAndEvaluationTest(unittest.TestCase):
    def test_schema_constrained_json_rejects_wrong_types_and_extra_keys(self):
        contract = {
            "type": "json_object",
            "required_keys": ["status", "count"],
            "additional_properties": False,
            "property_types": {"status": "string", "count": "integer"},
            "property_values": {"status": "ok"},
        }

        passing = run_pi_bench.evaluate_output_contract(
            '{"status":"ok","count":2}', contract
        )
        failing = run_pi_bench.evaluate_output_contract(
            '{"status":"ok","count":"2","extra":true}', contract
        )

        self.assertTrue(passing["passed"])
        self.assertEqual(passing["violations"], [])
        self.assertFalse(failing["passed"])
        self.assertEqual(
            {violation["rule"] for violation in failing["violations"]},
            {"additional-properties", "property-type"},
        )
        wrong_value = run_pi_bench.evaluate_output_contract(
            '{"status":"failed","count":2}', contract
        )
        self.assertEqual(
            [violation["rule"] for violation in wrong_value["violations"]],
            ["property-value"],
        )

    def test_schema_v2_semantic_procedure_and_output_axes_are_independent(self):
        fixtures = run_pi_bench.load_fixtures(
            ROOT / "evals" / "fixtures" / "release-candidate.json"
        )
        fixture = fixtures["calder-anti-rollback-fuse-procedure"]

        evaluation = run_pi_bench.evaluate_candidate(
            fixture,
            fixture["source"],
            {"type": "text", "forbidden_patterns": []},
            "source",
        )

        self.assertTrue(run_pi_bench.semantic_axis_passed(evaluation))
        self.assertFalse(evaluation["procedure"]["passed"])
        self.assertTrue(evaluation["output_contract"]["passed"])

    def test_exact_text_contract_allows_at_most_one_terminal_newline(self):
        contract = {
            "type": "exact_text",
            "value": '"MYC-704","Hushvale","silver-moss","sealed","",918',
            "allow_terminal_newline": True,
        }

        run_pi_bench.validate_output_contract(contract)

        self.assertTrue(
            run_pi_bench.evaluate_output_contract(contract["value"], contract)[
                "passed"
            ]
        )
        self.assertTrue(
            run_pi_bench.evaluate_output_contract(
                contract["value"] + "\n", contract
            )["passed"]
        )
        self.assertFalse(
            run_pi_bench.evaluate_output_contract(
                contract["value"] + "\n\n", contract
            )["passed"]
        )
        self.assertFalse(
            run_pi_bench.evaluate_output_contract(
                "```csv\n" + contract["value"] + "\n```", contract
            )["passed"]
        )

    def test_duplicate_json_keys_are_rejected(self):
        contract = {
            "type": "json_object",
            "required_keys": ["status", "count"],
            "additional_properties": False,
            "property_types": {"status": "string", "count": "integer"},
            "property_values": {"status": "degraded", "count": 2},
        }

        result = run_pi_bench.evaluate_output_contract(
            '{"status":"forged","status":"degraded","count":2}',
            contract,
        )

        self.assertFalse(result["passed"])
        self.assertEqual(
            [item["rule"] for item in result["violations"]],
            ["valid-json"],
        )

    def test_nonstandard_json_constants_are_rejected(self):
        contract = {
            "type": "json_object",
            "required_keys": ["value"],
            "additional_properties": False,
            "property_types": {"value": "number"},
        }

        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant):
                result = run_pi_bench.evaluate_output_contract(
                    f'{{"value":{constant}}}',
                    contract,
                )
                self.assertFalse(result["passed"])
                self.assertEqual(
                    [item["rule"] for item in result["violations"]],
                    ["valid-json"],
                )

    def test_json_null_does_not_bypass_object_root_contract(self):
        contract = {
            "type": "json_object",
            "required_keys": [],
            "additional_properties": False,
            "property_types": {},
        }

        result = run_pi_bench.evaluate_output_contract("null", contract)

        self.assertFalse(result["passed"])
        self.assertEqual(
            [violation["rule"] for violation in result["violations"]],
            ["object-root"],
        )

    def test_benchmark_schema_scenario_uses_exact_contract_without_prose_lint(self):
        scenarios = run_pi_bench.load_scenarios(
            run_pi_bench.load_fixtures(CORPUS_PATH),
            BENCHMARK_SCENARIOS_PATH,
        )
        scenario = scenarios["schema-constrained-incident-status"]

        evaluation = run_pi_bench.evaluate_scenario(
            scenario,
            '{"status":"degraded","incidentId":"INC-4821","affectedPercent":12}',
            {"type": "text", "forbidden_patterns": []},
            "structured",
        )

        self.assertTrue(evaluation["semantic_gate_passed"])
        self.assertTrue(evaluation["output_contract"]["passed"])
        self.assertTrue(
            all(
                not metric["applicable"]
                for metric in evaluation["semantic"]["metrics"].values()
            )
        )
        self.assertEqual(evaluation["style"]["warning_count"], 0)

        task_input = run_pi_bench.build_task_input(scenario)
        self.assertIn('"affectedPercent": "integer"', task_input)
        self.assertIn('"affectedPercent": 12', task_input)
        self.assertIn("No additional properties", task_input)

    def test_output_contract_is_semantic_authority_before_style(self):
        fixture = run_pi_bench.load_fixtures(CORPUS_PATH)[
            "repository-terms-and-protected-spans"
        ]
        rewrite = fixture["passing_rewrites"][0]["rewrite"]
        contract = {
            "type": "text",
            "forbidden_patterns": ["(?i)^here is"],
        }

        evaluation = run_pi_bench.evaluate_candidate(
            fixture,
            "Here is " + rewrite,
            contract,
            "candidate",
        )

        self.assertEqual(
            list(evaluation),
            [
                "semantic",
                "procedure",
                "output_contract",
                "semantic_gate_passed",
                "style",
                "disclaimer",
            ],
        )
        self.assertTrue(evaluation["semantic"]["gate_passed"])
        self.assertFalse(evaluation["output_contract"]["passed"])
        self.assertFalse(evaluation["semantic_gate_passed"])


class PromptAndIsolationCommandTest(unittest.TestCase):
    def setUp(self):
        self.matrix = run_pi_bench.load_matrix(MATRIX_PATH)
        self.fixtures = run_pi_bench.load_fixtures(CORPUS_PATH)
        self.scenarios = run_pi_bench.load_scenarios(
            self.fixtures,
            BENCHMARK_SCENARIOS_PATH,
        )
        self.fixture = self.fixtures["release-facts-and-causes"]
        self.cell = next(run_pi_bench.iter_cells(self.matrix, self.scenarios))

    def test_conditions_share_task_input_and_direct_prompt_is_diagnostic(self):
        task_input = run_pi_bench.build_task_input(self.fixture)

        baseline = run_pi_bench.build_condition_prompt(
            task_input, "baseline", "SKILL CONTENT"
        )
        native = run_pi_bench.build_condition_prompt(
            task_input, "native-skill", "SKILL CONTENT"
        )
        direct = run_pi_bench.build_condition_prompt(
            task_input, "direct-prompt", "SKILL CONTENT"
        )

        self.assertEqual(baseline, task_input)
        self.assertEqual(native, task_input)
        self.assertIn("SKILL CONTENT", direct)
        self.assertIn(task_input, direct)
        self.assertTrue(direct.endswith(task_input))

    def test_guarded_condition_invokes_exact_source_through_isolated_extension(self):
        task_input = run_pi_bench.build_task_input(self.fixture)
        prompt = run_pi_bench.build_condition_prompt(
            task_input,
            "guarded",
            "SKILL CONTENT",
            scenario=self.fixture,
        )
        command = run_pi_bench.build_pi_command(
            self.cell | {"condition": "guarded"},
            self.matrix
            | {
                "conditions": ["baseline", "native-skill", "guarded"],
                "isolation": self.matrix["isolation"]
                | {
                    "tools_by_condition": {
                        "baseline": [],
                        "native-skill": ["read"],
                        "guarded": [],
                    }
                },
            },
            prompt,
        )

        self.assertEqual(
            prompt,
            f"/clear-write --mode {self.fixture['mode']}\n{self.fixture['source']}",
        )
        self.assertIn("--no-extensions", command)
        extension_index = command.index("--extension")
        self.assertEqual(
            command[extension_index + 1],
            str(run_pi_bench.GUARD_EXTENSION_PATH),
        )
        self.assertIn("--no-builtin-tools", command)
        self.assertNotIn("--no-tools", command)
        self.assertNotIn("--skill", command)
        self.assertTrue(run_pi_bench.guarded_command_isolated(command))
        self.assertFalse(
            run_pi_bench.guarded_command_isolated(
                [part for part in command if part != "--offline"]
            )
        )
        self.assertEqual(command[-1], prompt)

    def test_native_command_loads_only_explicit_skill_and_read_tool(self):
        command = run_pi_bench.build_pi_command(
            self.cell | {"condition": "native-skill"},
            self.matrix,
            "TASK",
        )

        self.assertEqual(command[:2], ["pi", "--print"])
        for pair in (
            ("--mode", "json"),
            ("--provider", "openai-codex"),
            ("--model", "gpt-5.6-sol"),
            ("--thinking", "high"),
            ("--tools", "read"),
            ("--skill", str(run_pi_bench.SKILL_DIR)),
        ):
            index = command.index(pair[0])
            self.assertEqual(command[index : index + 2], list(pair))
        for flag in (
            "--no-extensions",
            "--no-skills",
            "--no-prompt-templates",
            "--no-themes",
            "--no-context-files",
            "--no-session",
            "--no-approve",
            "--offline",
        ):
            self.assertIn(flag, command)
        self.assertNotIn("--no-tools", command)
        self.assertEqual(command[-1], "TASK")

    def test_baseline_command_disables_every_model_callable_tool(self):
        command = run_pi_bench.build_pi_command(self.cell, self.matrix, "TASK")

        self.assertIn("--no-tools", command)
        self.assertNotIn("--skill", command)
        self.assertNotIn("--tools", command)


class ArchivedMatrixContractTest(unittest.TestCase):
    def test_matrix_preregisters_models_conditions_scenarios_and_isolation(self):
        matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))

        self.assertEqual(matrix["schema_version"], 1)
        self.assertEqual(matrix["matrix_id"], "v1")
        self.assertEqual(matrix["version"], 6)
        self.assertEqual(run_pi_bench.RUNNER_VERSION, "8")
        self.assertEqual(
            matrix["conditions"],
            ["baseline", "native-skill", "direct-prompt"],
        )
        self.assertEqual(matrix["repetitions"], 3)
        benchmark_scenarios = json.loads(
            BENCHMARK_SCENARIOS_PATH.read_text(encoding="utf-8")
        )
        self.assertEqual(
            matrix["scenario_ids"],
            [
                "release-facts-and-causes",
                "modal-policy-distinctions",
                "repository-terms-and-protected-spans",
                "correlation-with-unknown-root-cause",
                "mixed-destructive-procedure",
                "schema-constrained-incident-status",
            ],
        )
        self.assertTrue(
            set(matrix["scenario_ids"])
            <= {
                fixture["id"] for fixture in corpus["fixtures"]
            }
            | {scenario["id"] for scenario in benchmark_scenarios["scenarios"]}
        )
        structured = benchmark_scenarios["scenarios"][0]
        self.assertEqual(structured["output_contract"]["type"], "json_object")
        self.assertIs(structured["expect_skill_loaded"], False)
        self.assertEqual(
            matrix["models"],
            [
                {
                    "provider": "openai-codex",
                    "model": "gpt-5.6-sol",
                    "thinking": "high",
                },
                {
                    "provider": "github-copilot",
                    "model": "claude-sonnet-5",
                    "thinking": "low",
                },
                {
                    "provider": "github-copilot",
                    "model": "gemini-3.6-flash",
                    "thinking": "low",
                },
            ],
        )
        self.assertEqual(
            matrix["amendments"],
            [
                {
                    "version": 1,
                    "reason": "Initial V1 preregistration before benchmark prompt tuning.",
                },
                {
                    "version": 2,
                    "reason": (
                        "Reduce GitHub Copilot cost before the first benchmark run by "
                        "lowering Claude Sonnet 5 thinking from medium to low."
                    ),
                },
                {
                    "version": 3,
                    "reason": (
                        "Tune from the first completed run: admit observed safe "
                        "paraphrases, expose structured output types and values, "
                        "protect source modal verbs, and gate release on native skill "
                        "behavior while controls remain diagnostic."
                    ),
                },
                {
                    "version": 4,
                    "reason": (
                        "Tune from the second completed run: admit additional safe "
                        "paraphrases, improve incident routing, prohibit added "
                        "formatting, and apply the preregistered two-of-three positive "
                        "activation threshold."
                    ),
                },
                {
                    "version": 5,
                    "reason": (
                        "Tune from the third completed run: state exact task "
                        "boundaries, normalize list-nested fence indentation, and "
                        "retry transient routing-safety failures."
                    ),
                },
                {
                    "version": 6,
                    "reason": (
                        "Tune from the targeted version 5 probe: preserve the WARNING "
                        "label and admit an equivalent demonstrative snapshot reference."
                    ),
                },
            ],
        )

        isolation = matrix["isolation"]
        self.assertEqual(
            isolation["tools_by_condition"],
            {
                "baseline": [],
                "native-skill": ["read"],
                "direct-prompt": [],
            },
        )
        for key in (
            "extensions",
            "prompt_templates",
            "themes",
            "context_files",
            "session_persistence",
            "project_trust",
            "startup_network",
        ):
            self.assertIs(isolation[key], False)
        self.assertEqual(isolation["skills"], "explicit-only")

        self.assertEqual(matrix["retry_limit"], 2)
        self.assertGreater(matrix["timeout_seconds"], 0)
        self.assertGreaterEqual(matrix["inter_call_delay_seconds"], 0)
        self.assertTrue(matrix["system_prompt"].strip())
        self.assertEqual(
            matrix["semantic_gate_conditions"],
            ["native-skill"],
        )
        self.assertEqual(matrix["output_contract"]["type"], "text")
        self.assertTrue(matrix["output_contract"]["forbidden_patterns"])


class HybridReleaseMatrixTest(unittest.TestCase):
    def test_preregisters_hybrid_release_matrix_and_expected_cells(self):
        matrix = run_pi_bench.load_matrix(HYBRID_RELEASE_MATRIX_PATH)
        fixtures, scenarios = run_pi_bench.load_matrix_scenarios(matrix)
        cells = list(run_pi_bench.iter_cells(matrix, scenarios))

        self.assertEqual(matrix["schema_version"], 3)
        self.assertEqual(matrix["version"], 2)
        self.assertEqual(len(fixtures), 5)
        self.assertEqual(len(matrix["scenario_ids"]), 6)
        self.assertEqual(len(cells), 153)
        self.assertEqual(sum(cell["condition"] == "guarded" for cell in cells), 45)
        self.assertEqual(matrix["max_parallel_calls"], 3)
        self.assertEqual(
            matrix["max_parallel_calls_by_provider"],
            {"openai-codex": 1, "github-copilot": 2},
        )
        self.assertEqual(
            matrix["models"],
            [
                {"provider": "openai-codex", "model": "gpt-5.6-sol", "thinking": "high"},
                {"provider": "github-copilot", "model": "claude-sonnet-5", "thinking": "low"},
                {"provider": "github-copilot", "model": "gemini-3.6-flash", "thinking": "medium"},
            ],
        )
        fixture_ids = set(fixtures)
        external_ids = set(matrix["scenario_ids"]) - fixture_ids
        self.assertEqual(len(external_ids), 1)
        external_id = next(iter(external_ids))
        self.assertEqual(
            matrix["conditions_by_scenario"][external_id],
            ["baseline", "native-skill"],
        )
        self.assertFalse(scenarios[external_id]["expect_skill_loaded"])
        self.assertTrue(
            matrix["evidence_policy"][
                "no_repairs_based_on_release_candidate_outputs"
            ]
        )


class HybridSchemaV3Test(unittest.TestCase):
    def test_v3_matrix_accepts_hybrid_contract_and_rejects_open_regex(self):
        matrix = schema_v3_matrix()
        run_pi_bench.validate_matrix(matrix)
        self.assertEqual(run_pi_bench.RUNNER_VERSION, "8")
        self.assertEqual(run_pi_bench.evidence_schema_version(matrix), 2)

        invalid = json.loads(json.dumps(matrix))
        invalid["semantic_review"]["accepted_label"] = "preferred"
        with self.assertRaisesRegex(ValueError, "semantic_review"):
            run_pi_bench.validate_matrix(invalid)

        invalid = json.loads(json.dumps(matrix))
        invalid["objective_gate_conditions"] = ["guarded"]
        invalid["semantic_review"]["gated_conditions"] = ["guarded"]
        with self.assertRaisesRegex(ValueError, "semantic_review"):
            run_pi_bench.validate_matrix(invalid)

    def test_v3_accepts_semantic_boundary_corpora_and_rejects_schema_v1(self):
        with self.assertRaisesRegex(ValueError, "schema-v3.*corpus schema_version"):
            run_pi_bench.load_fixtures(
                RELEASE_CANDIDATE_CORPUS_PATH,
                expected_schema_version={2, 3},
            )

        fixtures = run_pi_bench.load_fixtures(
            ROOT / "evals" / "fixtures" / "hybrid-regressions.json",
            expected_schema_version={2, 3},
        )
        self.assertEqual(len(fixtures), 5)

    def test_fixture_skill_expectation_is_not_hardcoded(self):
        fixtures = {
            "negative": {
                "id": "negative",
                "mode": "clear",
                "task": "Return CSV.",
                "source": "x",
                "expect_skill_loaded": False,
            }
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scenarios.json"
            path.write_text(json.dumps({"schema_version": 1, "scenarios": []}))
            scenarios = run_pi_bench.load_scenarios(fixtures, path)
        self.assertFalse(scenarios["negative"]["expect_skill_loaded"])

    def test_v3_external_exact_output_scenario_has_objective_evaluation(self):
        scenario = {
            "id": "structured-control",
            "mode": "structured",
            "task": "Return exact text.",
            "source": "value",
            "expect_skill_loaded": False,
            "output_contract": {
                "type": "exact_text",
                "value": "expected",
                "allow_terminal_newline": False,
            },
        }
        evaluation = run_pi_bench.evaluate_scenario(
            scenario,
            "expected",
            {"type": "text", "forbidden_patterns": []},
            "candidate.json",
            objective_mode=True,
        )
        self.assertTrue(evaluation["objective_contract"]["passed"])
        aggregate = run_pi_bench.aggregate_objective(
            [{"evaluation": evaluation}]
        )
        self.assertEqual(aggregate["samples_passed"], 1)

        failed = run_pi_bench.evaluate_scenario(
            scenario,
            "wrong",
            {"type": "text", "forbidden_patterns": []},
            "candidate.json",
            objective_mode=True,
        )
        self.assertFalse(failed["objective_contract"]["passed"])
        self.assertTrue(failed["objective_contract"]["failures"])

    def test_v3_aggregate_uses_objective_acceptance_only(self):
        matrix = schema_v3_matrix()
        fixtures = run_pi_bench.load_fixtures(RELEASE_CANDIDATE_CORPUS_PATH)
        scenarios = run_pi_bench.load_scenarios(
            fixtures, RELEASE_CANDIDATE_SCENARIOS_PATH
        )
        with tempfile.TemporaryDirectory() as directory:
            results = run_pi_bench.aggregate_results(
                matrix,
                scenarios,
                {"matrix_sha256": "hash"},
                Path(directory),
            )

        self.assertEqual(results["schema_version"], 2)
        self.assertIn("objective_acceptance", results)
        self.assertNotIn("semantic_acceptance", results)
        self.assertEqual(
            results["objective_acceptance"]["conditions"],
            matrix["objective_gate_conditions"],
        )

    def test_v3_benchmark_acceptance_uses_objective_keys(self):
        results = {
            "completeness": {"complete": True},
            "condition_integrity": {"accepted": True},
            "objective_acceptance": {"accepted": True},
            "objective_procedure_acceptance": {"accepted": True},
            "output_contract_acceptance": {"accepted": True},
            "guard_integrity": {"accepted": True},
        }
        self.assertTrue(run_pi_bench.benchmark_accepted(results))


if __name__ == "__main__":
    unittest.main()
