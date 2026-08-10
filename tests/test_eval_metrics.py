import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "evals" / "score_fixtures.py"
CORPUS_PATH = ROOT / "evals" / "fixtures" / "semantic-preservation.json"
INDEPENDENT_CORPUS_PATH = ROOT / "evals" / "fixtures" / "independent-review.json"
PRE_RELEASE_EVIDENCE = (
    ROOT / "archive" / "pre-release" / "evals" / "evidence"
)
INDEPENDENT_RESULTS_PATH = PRE_RELEASE_EVIDENCE / "independent-review"
ADJUDICATION_PATH = INDEPENDENT_RESULTS_PATH / "adjudication" / "summary.json"
SEMANTIC_PROBES_PATH = (
    PRE_RELEASE_EVIDENCE
    / "development"
    / "post-adjudication-semantic-probes.json"
)
sys.path.insert(0, str(ROOT / "evals"))

import score_fixtures

LINTER_CACHE = (
    ROOT / "skills" / "clear-technical-writing" / "scripts" / "__pycache__"
)


def load_corpus():
    return json.loads(CORPUS_PATH.read_text())


def fixture_by_id(fixture_id):
    return next(
        fixture
        for fixture in load_corpus()["fixtures"]
        if fixture["id"] == fixture_id
    )


def independent_fixture_by_id(fixture_id):
    corpus = json.loads(INDEPENDENT_CORPUS_PATH.read_text(encoding="utf-8"))
    return next(
        fixture for fixture in corpus["fixtures"] if fixture["id"] == fixture_id
    )


def candidate_by_id(fixture, candidate_id):
    return next(
        candidate
        for group in ("passing_rewrites", "failing_baselines")
        for candidate in fixture[group]
        if candidate["id"] == candidate_id
    )


def run_cli(fixture_id, rewrite, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), fixture_id, "--format", "json", *args, "-"],
        input=rewrite,
        text=True,
        capture_output=True,
        check=False,
    )


class SemanticParaphraseRegressionTest(unittest.TestCase):
    def test_scope_invariant_accepts_never_affects(self):
        fixture = independent_fixture_by_id(
            "ledger-archive-purge-destructive-procedure"
        )
        rewrite = fixture["passing_rewrites"][0]["rewrite"].replace(
            "leaves active ledger snapshots untouched",
            "never affects active ledger snapshots",
        )

        metric = score_fixtures.metric_from_invariants(fixture, rewrite, {"fact"})

        self.assertTrue(metric["passed"])

    def test_forbidden_snapshot_pattern_respects_explicit_negation(self):
        fixture = independent_fixture_by_id(
            "ledger-archive-purge-destructive-procedure"
        )

        metric = score_fixtures.forbidden_claim_metric(
            fixture,
            "The archive purge job never affects active ledger snapshots.",
        )

        self.assertTrue(metric["passed"])

    def test_colon_ended_action_before_numbered_step_still_requires_number(self):
        text = "Delete the archive:\n1. Confirm that deletion succeeded."

        findings = score_fixtures.step_numbering_findings(
            text,
            "candidate",
            score_fixtures.load_linter(),
        )

        self.assertEqual(
            [finding["rule"] for finding in findings],
            ["step-numbering"],
        )

    def test_numbered_substep_lead_in_does_not_require_own_number(self):
        text = (
            "Before running the command, confirm both conditions:\n\n"
            "1. Confirm that the export is complete.\n"
            "2. Confirm that the ticket has approval."
        )

        findings = score_fixtures.step_numbering_findings(
            text,
            "candidate",
            score_fixtures.load_linter(),
        )

        self.assertEqual(findings, [])

    def test_warning_invariant_accepts_restoration_noun(self):
        fixture = independent_fixture_by_id(
            "ledger-archive-purge-destructive-procedure"
        )
        rewrite = fixture["passing_rewrites"][0]["rewrite"].replace(
            "recovering afterward requires restoring from cold storage",
            "recovery requires restoration from cold storage",
        )

        metric = score_fixtures.metric_from_invariants(
            fixture,
            rewrite,
            {"procedure"},
        )

        self.assertTrue(metric["passed"])

    def test_forbidden_recovery_pattern_rejects_restoration_noun(self):
        fixture = independent_fixture_by_id(
            "ledger-archive-purge-destructive-procedure"
        )

        metric = score_fixtures.forbidden_claim_metric(
            fixture,
            "Recovery does not require restoration from cold storage.",
        )

        self.assertFalse(metric["passed"])
        self.assertEqual(
            [failure["rule_id"] for failure in metric["failures"]],
            ["purge.forbidden-recovery"],
        )

    def test_forbidden_snapshot_pattern_rejects_positive_affect(self):
        fixture = independent_fixture_by_id(
            "ledger-archive-purge-destructive-procedure"
        )

        metric = score_fixtures.forbidden_claim_metric(
            fixture,
            "The archive purge job affects active ledger snapshots.",
        )

        self.assertFalse(metric["passed"])
        self.assertEqual(
            [failure["rule_id"] for failure in metric["failures"]],
            ["purge.forbidden-snapshot-impact"],
        )


class PassingScoreContractTest(unittest.TestCase):
    def test_independent_sources_and_passing_rewrites_clear_full_semantic_gate(self):
        corpus = json.loads(INDEPENDENT_CORPUS_PATH.read_text(encoding="utf-8"))

        for fixture in corpus["fixtures"]:
            candidates = [
                {"id": "source", "rewrite": fixture["source"]},
                *fixture["passing_rewrites"],
            ]
            for candidate in candidates:
                with self.subTest(fixture=fixture["id"], candidate=candidate["id"]):
                    report = score_fixtures.score_rewrite(
                        fixture,
                        candidate["rewrite"],
                        candidate=candidate["id"],
                    )
                    self.assertTrue(report["semantic"]["gate_passed"])
                    if report["procedure"]["applicable"]:
                        self.assertTrue(report["procedure"]["passed"])

    def test_independent_failing_baselines_match_full_scorer_failures(self):
        corpus = json.loads(INDEPENDENT_CORPUS_PATH.read_text(encoding="utf-8"))

        for fixture in corpus["fixtures"]:
            for baseline in fixture["failing_baselines"]:
                with self.subTest(fixture=fixture["id"], baseline=baseline["id"]):
                    report = score_fixtures.score_rewrite(
                        fixture,
                        baseline["rewrite"],
                        candidate=baseline["id"],
                    )
                    self.assertEqual(
                        set(report["semantic"]["failed_rule_ids"]),
                        set(
                            baseline.get(
                                "expected_full_scorer_violations",
                                baseline["expected_violations"],
                            )
                        ),
                    )

    def test_independent_forbidden_claims_catch_obvious_sibling_phrasings(self):
        fixtures = {
            fixture["id"]: fixture
            for fixture in json.loads(
                INDEPENDENT_CORPUS_PATH.read_text(encoding="utf-8")
            )["fixtures"]
        }
        cases = [
            (
                "helios-transcoder-confirmed-and-unconfirmed-cause",
                "helios.forbidden-worker-cause",
                "The worker-pool resize caused the failure-rate drop.",
            ),
            (
                "helios-transcoder-confirmed-and-unconfirmed-cause",
                "helios.forbidden-all-leases",
                "Expired GPU leases caused every failed segment.",
            ),
            (
                "orbital-greenhouse-modal-policy",
                "greenhouse.forbidden-calibration-required",
                "Habitat stewards are required to calibrate nutrient pumps quarterly.",
            ),
            (
                "orbital-greenhouse-modal-policy",
                "greenhouse.forbidden-suspension-required",
                "Flight horticulturists are required to suspend dosing.",
            ),
            (
                "orbital-greenhouse-modal-policy",
                "greenhouse.forbidden-sync-certain",
                "Canopy sensor synchronization takes 17 minutes.",
            ),
            (
                "orbital-greenhouse-modal-policy",
                "greenhouse.forbidden-restart-certain",
                "Dormant grow bays restart without a spectral scan during eclipse mode.",
            ),
            (
                "helios-transcoder-confirmed-and-unconfirmed-cause",
                "helios.forbidden-denied-confirmed-cause",
                "Expired GPU leases were unrelated to 61% of the failed segments.",
            ),
            (
                "orbital-greenhouse-modal-policy",
                "greenhouse.forbidden-sync-negated",
                "Canopy sensor synchronization might not require 17 minutes.",
            ),
            (
                "broker-failover-correlation-unknown-cause",
                "broker.forbidden-no-cause",
                "The failover did not cause the queue-depth increase.",
            ),
        ]

        for fixture_id, rule_id, contradiction in cases:
            fixture = fixtures[fixture_id]
            rewrite = fixture["passing_rewrites"][0]["rewrite"] + " " + contradiction
            with self.subTest(fixture=fixture_id, rule=rule_id):
                report = score_fixtures.score_rewrite(fixture, rewrite)
                self.assertIn(rule_id, report["semantic"]["failed_rule_ids"])

    def test_adjudicated_false_positives_pass_and_genuine_failures_still_fail(self):
        fixtures = {
            fixture["id"]: fixture
            for fixture in json.loads(
                INDEPENDENT_CORPUS_PATH.read_text(encoding="utf-8")
            )["fixtures"]
        }
        adjudication = json.loads(ADJUDICATION_PATH.read_text(encoding="utf-8"))

        self.assertEqual(
            adjudication["counts"],
            {
                "total": 18,
                "genuine_failure": 6,
                "evaluator_false_positive": 12,
                "ambiguous": 0,
            },
        )
        genuine_rule_ids = {
            "case-03": {"protected.source-equality", "purge.verify-command"},
            "case-04": {"protected.source-equality", "purge.verify-command"},
            "case-05": {"protected.source-equality"},
            "case-07": {"protected.source-equality", "vesper.protected-identifier"},
            "case-08": {"protected.source-equality", "vesper.protected-repeated-path"},
            "case-09": {"broker.unknown-cause"},
        }
        for case in adjudication["cases"]:
            raw = json.loads(
                (INDEPENDENT_RESULTS_PATH / "raw" / case["raw_file"]).read_text(
                    encoding="utf-8"
                )
            )
            report = score_fixtures.score_rewrite(
                fixtures[case["scenario_id"]],
                raw["response"]["text"],
                candidate=case["case_id"],
            )
            with self.subTest(case=case["case_id"], verdict=case["verdict"]):
                if case["verdict"] == "evaluator_false_positive":
                    self.assertTrue(report["semantic"]["gate_passed"])
                else:
                    self.assertFalse(report["semantic"]["gate_passed"])
                    self.assertTrue(
                        genuine_rule_ids[case["case_id"]]
                        & set(report["semantic"]["failed_rule_ids"])
                    )

    def test_safe_broker_development_probes_pass_without_hiding_procedure_failures(self):
        fixtures = {
            fixture["id"]: fixture
            for fixture in json.loads(
                INDEPENDENT_CORPUS_PATH.read_text(encoding="utf-8")
            )["fixtures"]
        }
        probes = json.loads(SEMANTIC_PROBES_PATH.read_text(encoding="utf-8"))

        for probe in probes["results"]:
            report = score_fixtures.score_rewrite(
                fixtures[probe["scenario_id"]],
                probe["text"],
            )
            with self.subTest(
                scenario=probe["scenario_id"],
                repetition=probe["repetition"],
            ):
                if probe["scenario_id"] == "broker-failover-correlation-unknown-cause":
                    self.assertTrue(report["semantic"]["gate_passed"])
                elif (
                    probe["scenario_id"]
                    == "ledger-archive-purge-destructive-procedure"
                    and probe["repetition"] in {2, 3}
                ):
                    self.assertFalse(report["semantic"]["gate_passed"])
                    self.assertIn(
                        "protected.source-equality",
                        report["semantic"]["failed_rule_ids"],
                    )

    def test_passing_rewrite_reports_separate_semantic_procedure_and_style_results(self):
        fixture = fixture_by_id("repository-terms-and-protected-spans")
        candidate = candidate_by_id(fixture, "protected-valid-reordered-note")

        result = run_cli(fixture["id"], candidate["rewrite"])

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["fixture_id"], fixture["id"])
        self.assertEqual(report["mode"], "clear")
        self.assertTrue(report["semantic"]["gate_passed"])
        self.assertEqual(report["semantic"]["failed_rule_ids"], [])
        self.assertEqual(
            set(report["semantic"]["metrics"]),
            {
                "protected_span_equality",
                "required_fact_retention",
                "forbidden_fact_invention",
                "modality_and_certainty_preservation",
                "repository_term_preservation",
            },
        )
        self.assertTrue(
            report["semantic"]["metrics"]["protected_span_equality"]["passed"]
        )
        self.assertTrue(
            report["semantic"]["metrics"]["repository_term_preservation"]["passed"]
        )
        self.assertFalse(report["procedure"]["applicable"])
        self.assertIsNone(report["procedure"]["passed"])
        self.assertTrue(report["style"]["advisory"])
        self.assertEqual(report["style"]["warning_count"], 0)
        self.assertIn("do not prove full semantic equivalence", report["disclaimer"])


class SemanticFailureClassificationTest(unittest.TestCase):
    def test_protected_spans_and_repository_terms_fail_independently(self):
        fixture = fixture_by_id("repository-terms-and-protected-spans")
        candidate = candidate_by_id(fixture, "protected-normalization")

        result = run_cli(fixture["id"], candidate["rewrite"])

        self.assertEqual(result.returncode, 1, result.stderr)
        metrics = json.loads(result.stdout)["semantic"]["metrics"]
        protected = metrics["protected_span_equality"]
        terms = metrics["repository_term_preservation"]
        self.assertFalse(protected["passed"])
        self.assertEqual(protected["rules_total"], 11)
        self.assertEqual(protected["rules_failed"], 11)
        self.assertEqual(
            {failure["rule_id"] for failure in protected["failures"]},
            {
                "protected.identifier",
                "protected.api-field",
                "protected.url",
                "protected.ui-label",
                "protected.path",
                "protected.command",
                "protected.code",
                "protected.error",
                "protected.log",
                "protected.test-output",
                "protected.source-equality",
            },
        )
        self.assertFalse(terms["passed"])
        self.assertEqual(
            [failure["rule_id"] for failure in terms["failures"]],
            ["terms.distinct"],
        )

    def test_added_protected_values_fail_source_equality_by_container(self):
        fixture = fixture_by_id("repository-terms-and-protected-spans")
        candidate = candidate_by_id(fixture, "protected-valid-reordered-note")[
            "rewrite"
        ]
        candidate += "\n\nRun `rm -rf /srv/acme`."

        result = run_cli(fixture["id"], candidate)

        self.assertEqual(result.returncode, 1, result.stderr)
        metric = json.loads(result.stdout)["semantic"]["metrics"][
            "protected_span_equality"
        ]
        self.assertFalse(metric["passed"])
        source_failure = next(
            failure
            for failure in metric["failures"]
            if failure["rule_id"] == "protected.source-equality"
        )
        self.assertEqual(
            set(source_failure["changed_kinds"]),
            {"inline-code", "path"},
        )

    def test_protected_source_equality_crosses_invariant_categories(self):
        fixture = fixture_by_id("mixed-destructive-procedure")
        candidate = candidate_by_id(fixture, "procedure-valid-rewrite")[
            "rewrite"
        ].replace("snap-2026-07-14", "snap-2026-07-15")

        result = run_cli(fixture["id"], candidate)

        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertIn(
            "protected.source-equality",
            report["semantic"]["failed_rule_ids"],
        )
        self.assertIn(
            "procedure.snapshot",
            report["semantic"]["failed_rule_ids"],
        )

    def test_equivalent_repository_term_relationship_is_not_a_false_failure(self):
        fixture = fixture_by_id("repository-terms-and-protected-spans")
        candidate = candidate_by_id(fixture, "protected-valid-reordered-note")[
            "rewrite"
        ].replace(
            "File-backed service values are called `config`, UI preferences are called `settings`, and request-scoped overrides are called `options`.",
            "This repository uses `config` for file-backed service values, `settings` for UI preferences, and `options` for request-scoped overrides.",
        )

        result = run_cli(fixture["id"], candidate)

        self.assertEqual(result.returncode, 0, result.stderr)
        metric = json.loads(result.stdout)["semantic"]["metrics"][
            "repository_term_preservation"
        ]
        self.assertTrue(metric["passed"])

    def test_missing_facts_and_causal_certainty_fail_separate_metrics(self):
        fixture = fixture_by_id("release-facts-and-causes")
        candidate = candidate_by_id(fixture, "release-numbers-drift")

        result = run_cli(fixture["id"], candidate["rewrite"])

        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        metrics = report["semantic"]["metrics"]
        self.assertFalse(report["semantic"]["gate_passed"])
        self.assertEqual(
            {
                failure["rule_id"]
                for failure in metrics["required_fact_retention"]["failures"]
            },
            {
                "release.date-version-volume",
                "release.error-rate",
                "release.retry-range",
            },
        )
        self.assertEqual(
            {
                failure["rule_id"]
                for failure in metrics[
                    "modality_and_certainty_preservation"
                ]["failures"]
            },
            {
                "release.ttl-sequence",
                "release.confirmed-cause",
                "release.unknown-cause",
            },
        )
        self.assertTrue(metrics["forbidden_fact_invention"]["passed"])
        self.assertEqual(metrics["required_fact_retention"]["pass_rate"], 0.0)
        self.assertEqual(
            metrics["modality_and_certainty_preservation"]["pass_rate"],
            0.0,
        )

    def test_forbidden_claims_fail_invention_metric_with_match_evidence(self):
        fixture = fixture_by_id("release-facts-and-causes")
        candidate = candidate_by_id(fixture, "release-causality-invention")

        result = run_cli(fixture["id"], candidate["rewrite"])

        self.assertEqual(result.returncode, 1, result.stderr)
        metric = json.loads(result.stdout)["semantic"]["metrics"][
            "forbidden_fact_invention"
        ]
        self.assertFalse(metric["passed"])
        self.assertEqual(
            {failure["rule_id"] for failure in metric["failures"]},
            {
                "release.forbidden-ttl-cause",
                "release.forbidden-all-stale",
                "release.forbidden-remaining-cause",
            },
        )
        for failure in metric["failures"]:
            self.assertTrue(failure["description"])
            self.assertTrue(failure["evidence"])
            for evidence in failure["evidence"]:
                self.assertTrue(evidence["pattern"])
                self.assertTrue(evidence["text"])
                self.assertGreaterEqual(evidence["line"], 1)
                self.assertGreaterEqual(evidence["column"], 1)

    def test_modality_metric_keeps_six_distinct_modal_roles(self):
        fixture = fixture_by_id("modal-policy-distinctions")
        candidate = candidate_by_id(fixture, "modal-collapse")

        result = run_cli(fixture["id"], candidate["rewrite"])

        self.assertEqual(result.returncode, 1, result.stderr)
        metric = json.loads(result.stdout)["semantic"]["metrics"][
            "modality_and_certainty_preservation"
        ]
        self.assertFalse(metric["passed"])
        self.assertEqual(metric["rules_total"], 6)
        self.assertEqual(metric["rules_passed"], 0)
        self.assertEqual(
            {failure["rule_id"] for failure in metric["failures"]},
            {
                "modal.must",
                "modal.should",
                "modal.can",
                "modal.may",
                "modal.might",
                "modal.could",
            },
        )


class ProcedureMetricTest(unittest.TestCase):
    def test_unsafe_procedure_fails_required_structure_rules(self):
        fixture = fixture_by_id("mixed-destructive-procedure")
        candidate = candidate_by_id(fixture, "procedure-unsafe-ordering")

        result = run_cli(fixture["id"], candidate["rewrite"])

        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        procedure = report["procedure"]
        self.assertTrue(procedure["applicable"])
        self.assertFalse(procedure["passed"])
        self.assertEqual(
            {
                failure["rule_id"]
                for failure in procedure["required_rules"]["failures"]
            },
            {
                "procedure.snapshot",
                "procedure.warning",
                "procedure.approval",
            },
        )
        self.assertLessEqual(
            {
                "procedure.snapshot",
                "procedure.warning",
                "procedure.approval",
            },
            set(report["semantic"]["failed_rule_ids"]),
        )

    def test_condition_leading_action_must_remain_a_numbered_step(self):
        fixture = fixture_by_id("mixed-destructive-procedure")
        candidate = candidate_by_id(fixture, "procedure-valid-rewrite")[
            "rewrite"
        ].replace(
            "3. After change request",
            "After change request",
        )

        result = run_cli(fixture["id"], candidate)

        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["procedure"]["required_rules"]["failures"], [])
        self.assertEqual(
            [warning["rule"] for warning in report["procedure"]["warnings"]],
            ["step-numbering"],
        )
        self.assertIn(
            "linter.step-numbering",
            report["semantic"]["failed_rule_ids"],
        )

    def test_unnumbered_instruction_steps_fail_procedure_structure(self):
        fixture = fixture_by_id("mixed-destructive-procedure")
        candidate = candidate_by_id(fixture, "procedure-valid-rewrite")[
            "rewrite"
        ]
        for ordinal in ("1. ", "2. ", "3. ", "4. "):
            candidate = candidate.replace(ordinal, "")

        result = run_cli(fixture["id"], candidate)

        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["procedure"]["required_rules"]["failures"], [])
        self.assertEqual(
            [warning["rule"] for warning in report["procedure"]["warnings"]],
            ["step-numbering", "step-numbering", "step-numbering"],
        )
        self.assertIn(
            "linter.step-numbering",
            report["semantic"]["failed_rule_ids"],
        )

    def test_trailing_action_condition_is_a_procedure_gate_failure(self):
        fixture = fixture_by_id("mixed-destructive-procedure")
        candidate = candidate_by_id(fixture, "procedure-valid-rewrite")[
            "rewrite"
        ].replace(
            "Check the status with `kubectl get namespace payments`.",
            "Check the status with `kubectl get namespace payments` if deletion finishes.",
        )

        result = run_cli(fixture["id"], candidate)

        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertFalse(report["procedure"]["passed"])
        self.assertEqual(report["procedure"]["required_rules"]["failures"], [])
        self.assertEqual(report["procedure"]["warning_count"], 1)
        self.assertEqual(
            report["procedure"]["warnings"][0]["rule"],
            "condition-order",
        )
        self.assertIn(
            "linter.condition-order",
            report["semantic"]["failed_rule_ids"],
        )


class ObservedParaphraseRegressionTest(unittest.TestCase):
    def test_safe_observed_paraphrases_pass_closed_world_semantics(self):
        terms_source = fixture_by_id(
            "repository-terms-and-protected-spans"
        )["source"]
        cases = {
            "release-facts-and-causes": (
                "On 2026-07-14, Acme API v3.8.2 processed 48,120 requests. "
                "The team changed the cache TTL from 5 to 15 minutes. After this "
                "change, the error rate fell from 2.4% to 0.7%. Of the 860 failed "
                "requests, trace data confirmed that stale cache entries caused 73%. "
                "The cause of the remaining failed requests remains unknown. The supported "
                "retry-delay range is 100-500 ms."
            ),
            "modal-policy-distinctions": (
                "Operators must keep backups for 30 days. Operators should test "
                "restoration every month. Administrators can rotate keys in Security "
                "settings. A key rotation may interrupt active sessions. Propagation "
                "might require up to 10 minutes. If you use `--force`, older clients could "
                "reconnect without cached credentials."
            ),
            "repository-terms-and-protected-spans": terms_source.replace(
                "In this repository, `config` means file-backed service values, "
                "`settings` means UI preferences, and `options` means request-scoped "
                "overrides.",
                "In this repository, `config` defines file-backed service values, "
                "`settings` defines UI preferences, and `options` defines "
                "request-scoped overrides.",
            ),
            "correlation-with-unknown-root-cause": (
                "During the 12-minute deployment window, p95 latency rose from 180 ms "
                "to 260 ms, but no evidence establishes causation. The root cause is "
                "unknown. "
                "Packet loss has been ruled out."
            ),
            "mixed-destructive-procedure": (
                "The cleanup job removes expired preview data. It does not delete "
                "production records.\n\n"
                "1. Confirm that snapshot `snap-2026-07-14` is complete.\n\n"
                "> **WARNING:** The next command permanently deletes namespace "
                "`payments`. Recovery requires restoring this snapshot.\n\n"
                "2. Confirm that change request `CHG-4821` is approved.\n\n"
                "3. Run:\n\n   ```bash\n   kubectl delete namespace payments\n   ```\n\n"
                "4. Verify the status with `kubectl get namespace payments`."
            ),
        }

        for fixture_id, rewrite in cases.items():
            with self.subTest(fixture_id=fixture_id):
                result = run_cli(fixture_id, rewrite)
                self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads(result.stdout)
                self.assertTrue(report["semantic"]["gate_passed"])
                if report["procedure"]["applicable"]:
                    self.assertIs(report["procedure"]["passed"], True)

    def test_ttl_change_stated_as_cause_is_forbidden(self):
        rewrite = (
            "On 2026-07-14, Acme API v3.8.2 processed 48,120 requests. Changing "
            "the cache TTL from 5 to 15 minutes dropped the error rate from 2.4% "
            "to 0.7%. Trace data confirmed that stale cache entries caused 73% of "
            "860 failed requests. The cause of the remaining failures is unknown. "
            "The supported retry-delay range is 100-500 ms."
        )

        result = run_cli("release-facts-and-causes", rewrite)
        report = json.loads(result.stdout)
        failures = {
            failure["rule_id"]
            for failure in report["semantic"]["metrics"][
                "forbidden_fact_invention"
            ]["failures"]
        }

        self.assertIn("release.forbidden-ttl-cause", failures)


class CorpusRegressionScoringTest(unittest.TestCase):
    def test_all_passing_rewrites_pass_semantic_and_procedure_gates(self):
        for fixture in load_corpus()["fixtures"]:
            for candidate in fixture["passing_rewrites"]:
                with self.subTest(fixture=fixture["id"], candidate=candidate["id"]):
                    result = run_cli(fixture["id"], candidate["rewrite"])
                    self.assertEqual(result.returncode, 0, result.stderr)
                    report = json.loads(result.stdout)
                    self.assertTrue(report["semantic"]["gate_passed"])
                    if report["procedure"]["applicable"]:
                        self.assertTrue(report["procedure"]["passed"])

    def test_all_failing_baselines_expose_every_declared_violation(self):
        for fixture in load_corpus()["fixtures"]:
            for candidate in fixture["failing_baselines"]:
                with self.subTest(fixture=fixture["id"], candidate=candidate["id"]):
                    result = run_cli(fixture["id"], candidate["rewrite"])
                    self.assertEqual(result.returncode, 1, result.stderr)
                    report = json.loads(result.stdout)
                    self.assertFalse(report["semantic"]["gate_passed"])
                    self.assertLessEqual(
                        set(candidate["expected_violations"]),
                        set(report["semantic"]["failed_rule_ids"]),
                    )


class MechanicalStyleMetricTest(unittest.TestCase):
    def test_style_warnings_are_advisory_and_do_not_fail_semantic_gate(self):
        fixture = fixture_by_id("modal-policy-distinctions")
        candidate = candidate_by_id(fixture, "modal-valid-active-passive-mix")[
            "rewrite"
        ].replace(
            "Monthly restoration testing is recommended for operators.",
            "Operators should test restoration monthly, etc.",
        )
        candidate += " It's available to administrators."

        result = run_cli(fixture["id"], candidate)

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["semantic"]["gate_passed"])
        self.assertTrue(report["style"]["advisory"])
        self.assertEqual(report["style"]["warning_count"], 2)
        self.assertEqual(
            report["style"]["warnings_by_rule"],
            {"contraction": 1, "latin-abbreviation": 1},
        )
        self.assertEqual(
            {finding["category"] for finding in report["style"]["findings"]},
            {"style"},
        )


class HumanOutputAndErrorTest(unittest.TestCase):
    def test_loading_linter_does_not_add_bytecode_to_packaged_skill(self):
        shutil.rmtree(LINTER_CACHE, ignore_errors=True)
        fixture = fixture_by_id("release-facts-and-causes")
        candidate = candidate_by_id(fixture, "release-valid-paraphrase")

        result = run_cli(fixture["id"], candidate["rewrite"])

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(LINTER_CACHE.exists())

    def test_text_output_lists_semantic_failures_before_advisory_style(self):
        fixture = fixture_by_id("release-facts-and-causes")
        candidate = candidate_by_id(fixture, "release-numbers-drift")

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                fixture["id"],
                "--format",
                "text",
                "-",
            ],
            input=candidate["rewrite"],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("semantic gate: FAIL", result.stdout)
        self.assertIn("release.date-version-volume", result.stdout)
        self.assertIn("release.confirmed-cause", result.stdout)
        self.assertLess(
            result.stdout.index("semantic gate"),
            result.stdout.index("mechanical style warnings"),
        )
        self.assertNotIn("overall score", result.stdout.lower())
        self.assertIn("do not prove full semantic equivalence", result.stdout)

    def test_custom_corpus_is_not_an_unvalidated_cli_surface(self):
        result = run_cli(
            "release-facts-and-causes",
            "Text.",
            "--corpus",
            str(CORPUS_PATH),
        )

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("unrecognized arguments: --corpus", result.stderr)

    def test_unknown_fixture_is_an_invocation_error(self):
        result = run_cli("missing-fixture", "Text.")

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("unknown fixture: missing-fixture", result.stderr)


if __name__ == "__main__":
    unittest.main()
