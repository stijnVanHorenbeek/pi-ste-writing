import re
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = (
    ROOT / "skills" / "clear-technical-writing" / "references" / "use-cases.md"
)
EXAMPLE_HEADINGS = [
    "## READMEs and API guides",
    "## Setup procedures and runbooks",
    "## User-facing CLI errors",
    "## Incident reports and postmortems",
    "## Release notes and changelogs",
    "## Patch and test summaries",
    "## Destructive operations and security warnings",
    "## Translation preparation",
]
SCOPE_HEADING = "## Scope boundaries"
NUMERIC_TOKEN_PATTERN = re.compile(
    r"(?<![\w.])(?:\d{1,2}:\d{2}(?::\d{2})?|"
    r"v?\d[\d,]*(?:\.\d+)*(?:-\d[\d,]*(?:\.\d+)*)*%?"
    r"(?:\s*(?:ms|seconds?|minutes?|hours?|days?|MB|GB|TB))?)",
    re.IGNORECASE,
)


def section_for(text, heading):
    start = text.index(heading)
    end = text.find("\n## ", start + len(heading))
    return text[start:] if end == -1 else text[start:end]


def fenced_example(section, label):
    match = re.search(
        rf"\*\*{re.escape(label)}\*\*\n\n```text\n(.*?)\n```",
        section,
        re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"missing {label} text fence")
    return match.group(1)


class UseCasesReferenceTest(unittest.TestCase):
    def test_required_use_cases_are_complete_and_ordered(self):
        text = REFERENCE.read_text()
        headings = [*EXAMPLE_HEADINGS, SCOPE_HEADING]
        positions = [text.find(heading) for heading in headings]

        self.assertNotIn(-1, positions)
        self.assertEqual(positions, sorted(positions))

    def test_examples_have_source_rewrite_and_protected_value_equality(self):
        text = REFERENCE.read_text()

        for heading in EXAMPLE_HEADINGS:
            with self.subTest(heading=heading):
                example = section_for(text, heading)
                self.assertIn("**Mode:**", example)
                self.assertIn("**Preservation check:**", example)
                source = fenced_example(example, "Source text")
                rewrite = fenced_example(example, "Safe rewrite")
                self.assertTrue(source.strip())
                self.assertTrue(rewrite.strip())
                self.assertEqual(
                    Counter(re.findall(r"`[^`\n]+`", source)),
                    Counter(re.findall(r"`[^`\n]+`", rewrite)),
                )
                self.assertEqual(
                    Counter(NUMERIC_TOKEN_PATTERN.findall(source)),
                    Counter(NUMERIC_TOKEN_PATTERN.findall(rewrite)),
                )

    def test_high_risk_examples_keep_required_action_order(self):
        text = REFERENCE.read_text()
        ordered_phrases = {
            "## Setup procedures and runbooks": [
                "obtain approval",
                "WARNING:",
                "If `acme check` succeeds",
                "run `acme migrate --database orders`",
            ],
            "## Destructive operations and security warnings": [
                "WARNING: Snapshot",
                "must be approved",
                "kubectl delete namespace payments",
                "kubectl get namespace payments",
                "SECURITY WARNING:",
                "Revoke the token",
                "rotate `PAYMENTS_API_KEY`",
            ],
        }

        for heading, phrases in ordered_phrases.items():
            rewrite = fenced_example(section_for(text, heading), "Safe rewrite")
            positions = [rewrite.find(phrase) for phrase in phrases]
            with self.subTest(heading=heading):
                self.assertNotIn(-1, positions)
                self.assertEqual(positions, sorted(positions))

    def test_scope_table_matches_activation_contract(self):
        section = section_for(REFERENCE.read_text(), SCOPE_HEADING)
        rows = {}
        for line in section.splitlines():
            if not line.startswith("|") or line.startswith("|---"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if cells[0] != "Context":
                rows[cells[0]] = cells[1]

        self.assertEqual(
            rows,
            {
                "Documentation or README": "Activate",
                "API guide": "Activate",
                "Setup procedure or runbook": "Activate",
                "Destructive operation or security warning": "Do not auto-activate",
                "User-facing error message or CLI help": "Activate",
                "Incident report, postmortem, release note, changelog": "Activate",
                "Translation-ready technical prose": "Activate",
                "Code review finding": "Do not auto-activate",
                "Debugging hypothesis": "Do not auto-activate",
                "Architecture analysis or design tradeoff": "Do not auto-activate",
                "Test-result interpretation": "Do not auto-activate",
                "Patch or test summary": "Do not auto-activate",
                "Raw tool output, log, or quoted diagnostic": "Do not auto-activate",
                "JSON, XML, YAML, CSV, or schema-constrained output": "Do not auto-activate",
                "Source code or generated code": "Do not auto-activate",
                "Marketing, editorial, or brand writing": "Do not auto-activate",
            },
        )


if __name__ == "__main__":
    unittest.main()
