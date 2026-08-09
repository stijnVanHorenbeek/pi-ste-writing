import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = (
    ROOT / "skills" / "clear-technical-writing" / "references" / "checklist.md"
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


class ChecklistReferenceTest(unittest.TestCase):
    def test_priority_sections_are_complete_and_ordered(self):
        text = REFERENCE.read_text()
        positions = [text.find(heading) for heading in PRIORITY_HEADINGS]

        self.assertNotIn(-1, positions)
        self.assertEqual(positions, sorted(positions))

    def test_markdown_tables_and_fences_are_well_formed(self):
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
        self.assertEqual(text.count("```") % 2, 0)

    def test_documented_search_patterns_compile_and_match_examples(self):
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
        for value in ("don't", "we're", "that's", "there's", "who'll"):
            self.assertIsNotNone(contractions.fullmatch(value), value)
        self.assertIsNone(contractions.fullmatch("operator's"))

        for label in (
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
        ):
            with self.subTest(label=label):
                pattern_for(label)


if __name__ == "__main__":
    unittest.main()
