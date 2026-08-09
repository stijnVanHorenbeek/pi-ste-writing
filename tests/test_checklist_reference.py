import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = (
    ROOT
    / "skills"
    / "clear-technical-writing"
    / "references"
    / "checklist.md"
)
PRIORITY_HEADINGS = [
    "## 1. Semantic fidelity",
    "## 2. Protected-span equality",
    "## 3. Exact output-contract preservation",
    "## 4. Repository terminology",
    "## 5. Procedural safety and action ordering",
    "## 6. Mechanical clarity warnings",
    "## 7. Strict STE rules when requested",
]
DECISION_HIERARCHY = [
    "1. Technical correctness.",
    "2. Source facts and meaning.",
    "3. Safety information and risk level.",
    "4. User intent and exact output contracts.",
    "5. Certainty, permission, recommendation, and obligation.",
    "6. Repository and product terminology.",
    "7. Clarity and structure.",
    "8. Mode-specific style rules.",
]


class ChecklistReferenceTest(unittest.TestCase):
    def test_priority_sections_exist_in_required_order(self):
        text = REFERENCE.read_text()
        positions = [text.find(heading) for heading in PRIORITY_HEADINGS]

        self.assertNotIn(-1, positions)
        self.assertEqual(positions, sorted(positions))

    def test_governing_decision_hierarchy_overrides_check_sequence(self):
        text = REFERENCE.read_text()
        positions = [text.find(item) for item in DECISION_HIERARCHY]

        self.assertNotIn(-1, positions)
        self.assertEqual(positions, sorted(positions))
        self.assertIn(
            "Checklist sequence does not let an output contract override safety",
            text,
        )
        semantic_section = text[
            text.index("## 1. Semantic fidelity") : text.index(
                "## 2. Protected-span equality"
            )
        ]
        self.assertIn("technical correctness", semantic_section)
        self.assertIn("safety information and risk level", semantic_section)

    def test_markdown_tables_have_consistent_columns_and_balanced_fences(self):
        text = REFERENCE.read_text()
        expected_pipes = None
        for line_number, line in enumerate(text.splitlines(), start=1):
            if not line.startswith("|"):
                expected_pipes = None
                continue
            pipe_count = len(re.findall(r"(?<!\\)\|", line))
            if expected_pipes is None:
                expected_pipes = pipe_count
            self.assertEqual(
                pipe_count,
                expected_pipes,
                f"malformed Markdown table at line {line_number}",
            )

        fence_count = sum(line.startswith("```") for line in text.splitlines())
        self.assertEqual(fence_count % 2, 0)
        table_lines = [line for line in text.splitlines() if line.startswith("|")]
        self.assertTrue(
            any(re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+", line) for line in table_lines)
        )

    def test_high_priority_gates_require_semantic_and_exact_comparison(self):
        text = REFERENCE.read_text()
        required = [
            "Build or reuse the semantic ledger",
            "added claims",
            "lost qualifiers",
            "causality",
            "permission, recommendation, and obligation",
            "value, occurrence count, container, and semantic role",
            "--source",
            "Parse or validate structured output",
            "exact schema",
            "Do not rewrite machine-readable output",
            "concept-to-term ledger",
            "distinct concepts",
        ]

        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_procedure_and_mixed_mode_checks_are_scoped(self):
        text = REFERENCE.read_text()
        required = [
            "Put the warning block before the dangerous operation",
            "preconditions and approvals",
            "action-controlling condition before its command",
            "required command before the risk or possible consequence",
            "verification step follows the action",
            "recovery requirement",
            "one action per numbered step",
            "20-word target",
            "## Mixed-mode handling",
            "Classify each passage separately",
            "A note inside a procedure is descriptive",
            "Quoted, code, and structured passages",
            "Strict checks activate only after an explicit strict STE request",
        ]

        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_searches_and_strict_checks_are_advisory_and_mode_aware(self):
        text = REFERENCE.read_text()
        required = [
            "### Searchable patterns",
            "A search hit is not automatically a violation",
            "Contractions",
            "Perfect constructions",
            "Progressive passive",
            "`-ing` clause",
            "Semicolon",
            "Latin abbreviation",
            "Filler candidate",
            "Modal candidate",
            "Condition candidate",
            "Clear mode",
            "Procedure mode",
            "Strict mode",
            "references/ste-rules.md",
            "20-word procedural and 25-word descriptive limits",
            "dictionary-dependent",
            "A strict audit cannot receive full `pass` for dictionary-dependent rules",
            "Retain the source and report an unresolved conflict",
            "does not check the official dictionary",
            "does not implement the `would` modal candidate or the `unless` condition candidate",
            "Zero linter warnings do not prove semantic correctness or compliance",
            "`--strict-gate`",
        ]

        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_search_patterns_compile_and_cover_documented_candidates(self):
        text = REFERENCE.read_text()

        def pattern_for(label):
            match = re.search(rf"\*\*{re.escape(label)}:\*\* `([^`]+)`", text)
            self.assertIsNotNone(match, label)
            return re.compile(match.group(1), re.IGNORECASE)

        quantity = pattern_for("Quantities")
        sample = "2026-07-14 v3.8.2 48,120 2.4% 100-500 ms 12:30"
        self.assertEqual(
            [match.group(0) for match in quantity.finditer(sample)],
            ["2026-07-14", "v3.8.2", "48,120", "2.4%", "100-500 ms", "12:30"],
        )

        contractions = pattern_for("Contractions")
        for value in ["don't", "we're", "that's", "there's", "who'll"]:
            with self.subTest(value=value):
                self.assertIsNotNone(contractions.fullmatch(value))
        self.assertIsNone(contractions.fullmatch("operator's"))

        for label in [
            "Modality",
            "Scope",
            "Evidence",
            "Causality",
            "Negation",
            "Perfect constructions",
            "Progressive passive",
            "Latin abbreviation",
            "Filler candidate",
            "Modal candidate",
            "Condition candidate",
        ]:
            with self.subTest(label=label):
                pattern_for(label)

    def test_audit_format_blocks_style_success_on_higher_priority_failures(self):
        text = REFERENCE.read_text()
        required = [
            "## Delivery gate",
            "Do not continue to lower-priority style fixes",
            "Semantic fidelity: `pass`",
            "Protected-span equality: `pass`",
            "Output contract: `pass`",
            "Repository terminology: `pass`",
            "Procedural safety: `pass`",
            "## Audit-report format",
            "Status: `pass | fail | needs-review | not-applicable`",
            "Priority and category:",
            "Source evidence:",
            "Draft text:",
            "Semantic or operational risk:",
            "Safe action:",
            "Dictionary coverage:",
            "Do not label output `compliant` or `certified`",
            "This audit is advisory and cannot certify ASD-STE100 compliance",
            "## Provenance",
            "59bf6702197a5aadc96d197ea17f290d8d50dcd3",
        ]

        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

        self.assertNotIn("`not applicable`", text)
        positive_claims = [
            r"\bis ASD-STE100 compliant\b",
            r"\bis ASD-STE100 certified\b",
            r"\bcertifies ASD-STE100 compliance\b",
            r"\bproves ASD-STE100 compliance\b",
        ]
        for pattern in positive_claims:
            with self.subTest(pattern=pattern):
                self.assertIsNone(re.search(pattern, text, re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
