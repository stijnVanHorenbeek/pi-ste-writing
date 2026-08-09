import re
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = (
    ROOT / "skills" / "clear-technical-writing" / "references" / "ste-rules.md"
)
EXPECTED_RULES = {
    *(f"1.{number}" for number in range(1, 15)),
    *(f"2.{number}" for number in range(1, 3)),
    *(f"3.{number}" for number in range(1, 8)),
    *(f"4.{number}" for number in range(1, 6)),
    *(f"5.{number}" for number in range(1, 6)),
    *(f"6.{number}" for number in range(1, 7)),
    *(f"7.{number}" for number in range(1, 4)),
    *(f"8.{number}" for number in range(1, 8)),
    *(f"9.{number}" for number in range(1, 5)),
}
CRITICAL_RULE_TEXT = {
    "1.11": "Use one name for one item or concept.",
    "3.6": (
        "Use active voice; descriptive text can use passive voice when the agent "
        "is unknown."
    ),
    "5.4": (
        "Put an action-controlling condition before its instruction and separate "
        "it with a comma."
    ),
    "7.2": (
        "Begin with a clear command, or with a condition that is followed by its command."
    ),
    "7.3": "Give the risk or possible result after the required command.",
}


def catalog_rows(text):
    return dict(
        re.findall(
            r"^\|\s*((?:\d+\.\d+)|(?:GR-\d+))\s*\|\s*(.*?)\s*\|$",
            text,
            re.MULTILINE,
        )
    )


class STERulesReferenceTest(unittest.TestCase):
    def test_catalog_has_every_issue_9_rule_once(self):
        rules = re.findall(
            r"^\|\s*(\d+\.\d+)\s*\|",
            REFERENCE.read_text(),
            re.MULTILINE,
        )

        self.assertEqual(set(rules), EXPECTED_RULES)
        self.assertEqual(len(rules), len(EXPECTED_RULES))

    def test_catalog_has_every_general_recommendation_once(self):
        recommendations = re.findall(
            r"^\|\s*(GR-[1-8])\s*\|",
            REFERENCE.read_text(),
            re.MULTILINE,
        )

        self.assertEqual(Counter(recommendations), Counter(f"GR-{n}" for n in range(1, 9)))

    def test_safety_critical_rule_mappings_do_not_drift(self):
        rows = catalog_rows(REFERENCE.read_text())

        for rule_id, expected_text in CRITICAL_RULE_TEXT.items():
            with self.subTest(rule_id=rule_id):
                self.assertEqual(rows[rule_id], expected_text)

    def test_reference_rejects_unsafe_certification_claims(self):
        text = REFERENCE.read_text()

        self.assertIn("cannot certify ASD-STE100 compliance", text)
        for pattern in (
            r"\bis ASD-STE100 compliant\b",
            r"\bis ASD-STE100 certified\b",
            r"\bcertifies ASD-STE100 compliance\b",
            r"\bproves ASD-STE100 compliance\b",
        ):
            with self.subTest(pattern=pattern):
                self.assertIsNone(re.search(pattern, text, re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
