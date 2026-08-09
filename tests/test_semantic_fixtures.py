import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / "evals" / "fixtures" / "semantic-preservation.json"

REQUIRED_TAGS = {
    "fact",
    "number",
    "date",
    "version",
    "percentage",
    "range",
    "causal_chain",
    "modality_must",
    "modality_should",
    "modality_can",
    "modality_may",
    "modality_might",
    "modality_could",
    "recommendation_vs_requirement",
    "correlation_not_causation",
    "unknown_vs_confirmed_cause",
    "repository_term",
    "protected_code",
    "protected_command",
    "protected_path",
    "protected_url",
    "protected_identifier",
    "protected_api_field",
    "protected_ui_label",
    "protected_error",
    "protected_log",
    "protected_test_output",
    "mixed_passage",
    "destructive_warning",
}
PROTECTED_TAGS = {tag for tag in REQUIRED_TAGS if tag.startswith("protected_")}
ALLOWED_MODES = {"clear", "procedure", "strict"}
ALLOWED_CATEGORIES = {
    "fact",
    "modality",
    "causality",
    "repository_term",
    "protected_span",
    "procedure",
}
CHECK_FIELDS = {
    "contains": {"type", "value", "count"},
    "regex": {"type", "pattern"},
    "precedes_regex": {"type", "before_pattern", "after_pattern"},
    "inline_code": {"type", "value", "count"},
    "fenced_code": {"type", "value", "count"},
    "markdown_link": {"type", "label", "destination", "count"},
    "bold_text": {"type", "value", "count"},
}


def extracted_values(text, check_type):
    if check_type == "inline_code":
        return re.findall(r"(?<!`)`([^`\n]+)`(?!`)", text)
    if check_type == "fenced_code":
        return re.findall(r"```[^\n]*\n(.*?)\n```", text, flags=re.DOTALL)
    if check_type == "markdown_link":
        return re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)
    if check_type == "bold_text":
        return re.findall(r"\*\*([^*\n]+)\*\*", text)
    raise AssertionError(f"unsupported extractor: {check_type}")


def check_passes(text, check):
    check_type = check["type"]
    if check_type == "contains":
        count = text.count(check["value"])
        return count == check["count"] if "count" in check else count > 0
    if check_type == "regex":
        return re.search(check["pattern"], text) is not None
    if check_type == "precedes_regex":
        before = re.search(check["before_pattern"], text)
        after = re.search(check["after_pattern"], text)
        return before is not None and after is not None and before.start() < after.start()

    values = extracted_values(text, check_type)
    if check_type == "markdown_link":
        expected = (check["label"], check["destination"])
    else:
        expected = check["value"]
    return values.count(expected) == check.get("count", 1)


def violated_rules(fixture, rewrite):
    violations = {
        invariant["id"]
        for invariant in fixture["invariants"]
        if not all(check_passes(rewrite, check) for check in invariant["checks"])
    }
    violations.update(
        claim["id"]
        for claim in fixture["forbidden_claims"]
        if any(re.search(pattern, rewrite) for pattern in claim["patterns"])
    )
    return violations


class SemanticFixtureCorpusTest(unittest.TestCase):
    def load_corpus(self):
        self.assertTrue(
            CORPUS_PATH.is_file(),
            f"semantic fixture corpus must exist at {CORPUS_PATH}",
        )
        return json.loads(CORPUS_PATH.read_text())

    def test_corpus_declares_version_and_nonempty_fixtures(self):
        corpus = self.load_corpus()

        self.assertEqual(corpus["schema_version"], 1)
        self.assertTrue(corpus["description"].strip())
        self.assertTrue(corpus["fixtures"])

    def test_corpus_covers_every_required_semantic_risk(self):
        corpus = self.load_corpus()
        covered_tags = {
            tag for fixture in corpus["fixtures"] for tag in fixture["tags"]
        }
        protected_rule_coverage = {
            tag
            for fixture in corpus["fixtures"]
            for invariant in fixture["invariants"]
            for tag in invariant.get("covers", [])
        }

        self.assertEqual(REQUIRED_TAGS - covered_tags, set())
        self.assertEqual(PROTECTED_TAGS - protected_rule_coverage, set())
        self.assertEqual(
            {fixture["mode"] for fixture in corpus["fixtures"]},
            ALLOWED_MODES,
        )

    def test_fixture_contract_is_closed_world_and_uniquely_identified(self):
        corpus = self.load_corpus()
        fixture_ids = [fixture["id"] for fixture in corpus["fixtures"]]

        self.assertEqual(len(fixture_ids), len(set(fixture_ids)))
        for fixture in corpus["fixtures"]:
            with self.subTest(fixture=fixture["id"]):
                self.assertIn("forbidden_claims", fixture)
                self.assertIn("passing_rewrites", fixture)
                self.assertIn(fixture["mode"], ALLOWED_MODES)
                self.assertTrue(fixture["title"].strip())
                self.assertTrue(fixture["task"].strip())
                self.assertTrue(fixture["source"].strip())
                self.assertTrue(fixture["allowed_claims"])
                self.assertTrue(fixture["forbidden_claims"])
                self.assertTrue(fixture["invariants"])
                self.assertTrue(fixture["passing_rewrites"])
                self.assertNotIn("expected_rewrite", fixture)

                claim_ids = [claim["id"] for claim in fixture["allowed_claims"]]
                forbidden_ids = [
                    claim["id"] for claim in fixture["forbidden_claims"]
                ]
                invariant_ids = [item["id"] for item in fixture["invariants"]]
                all_rule_ids = forbidden_ids + invariant_ids

                self.assertEqual(len(claim_ids), len(set(claim_ids)))
                self.assertEqual(len(all_rule_ids), len(set(all_rule_ids)))
                for claim in fixture["allowed_claims"]:
                    self.assertTrue(claim["description"].strip())
                for claim in fixture["forbidden_claims"]:
                    self.assertTrue(claim["description"].strip())
                    self.assertTrue(claim["patterns"])
                    for pattern in claim["patterns"]:
                        re.compile(pattern)

    def test_high_risk_tasks_state_exact_preservation_boundaries(self):
        fixtures = {
            fixture["id"]: fixture for fixture in self.load_corpus()["fixtures"]
        }

        release_task = fixtures["release-facts-and-causes"]["task"]
        self.assertIn("100-500 ms", release_task)
        self.assertIn("hyphen", release_task)
        self.assertIn(
            "correlation only",
            fixtures["correlation-with-unknown-root-cause"]["task"].lower(),
        )
        procedure_task = fixtures["mixed-destructive-procedure"]["task"].lower()
        self.assertIn("fenced", procedure_task)
        self.assertIn("inline", procedure_task)
        self.assertIn("warning", procedure_task)
        self.assertIn("note", procedure_task)

    def test_invariants_define_machine_readable_checks(self):
        corpus = self.load_corpus()

        for fixture in corpus["fixtures"]:
            fixture_tags = set(fixture["tags"])
            for invariant in fixture["invariants"]:
                with self.subTest(fixture=fixture["id"], invariant=invariant["id"]):
                    self.assertIn(invariant["category"], ALLOWED_CATEGORIES)
                    self.assertTrue(invariant["description"].strip())
                    self.assertTrue(invariant["checks"])
                    self.assertLessEqual(
                        set(invariant.get("covers", [])), fixture_tags
                    )

                    for check in invariant["checks"]:
                        self.assertIn(check["type"], CHECK_FIELDS)
                        self.assertLessEqual(set(check), CHECK_FIELDS[check["type"]])
                        self.assertEqual(
                            set(check) - {"count"},
                            CHECK_FIELDS[check["type"]] - {"count"},
                        )
                        if "count" in check:
                            self.assertIsInstance(check["count"], int)
                            self.assertGreater(check["count"], 0)
                        for key in set(check) - {"type", "count"}:
                            self.assertTrue(check[key])
                        if check["type"] == "regex":
                            re.compile(check["pattern"])
                        elif check["type"] == "precedes_regex":
                            re.compile(check["before_pattern"])
                            re.compile(check["after_pattern"])

    def test_sources_and_alternate_rewrites_satisfy_every_rule(self):
        corpus = self.load_corpus()

        for fixture in corpus["fixtures"]:
            candidates = [
                {"id": "source", "rewrite": fixture["source"]},
                *fixture["passing_rewrites"],
            ]
            for candidate in candidates:
                with self.subTest(fixture=fixture["id"], candidate=candidate["id"]):
                    self.assertTrue(candidate["rewrite"].strip())
                    if candidate["id"] != "source":
                        self.assertNotEqual(candidate["rewrite"], fixture["source"])
                    self.assertEqual(violated_rules(fixture, candidate["rewrite"]), set())

    def test_baselines_are_intentionally_failing_and_map_to_rules(self):
        corpus = self.load_corpus()

        for fixture in corpus["fixtures"]:
            rule_ids = {item["id"] for item in fixture["invariants"]}
            rule_ids.update(item["id"] for item in fixture["forbidden_claims"])
            self.assertTrue(fixture["failing_baselines"])

            baseline_ids = [item["id"] for item in fixture["failing_baselines"]]
            self.assertEqual(len(baseline_ids), len(set(baseline_ids)))
            for baseline in fixture["failing_baselines"]:
                with self.subTest(fixture=fixture["id"], baseline=baseline["id"]):
                    self.assertTrue(baseline["rewrite"].strip())
                    self.assertNotEqual(baseline["rewrite"], fixture["source"])
                    expected = set(baseline["expected_violations"])
                    self.assertTrue(expected)
                    self.assertLessEqual(expected, rule_ids)
                    self.assertEqual(violated_rules(fixture, baseline["rewrite"]), expected)


if __name__ == "__main__":
    unittest.main()
