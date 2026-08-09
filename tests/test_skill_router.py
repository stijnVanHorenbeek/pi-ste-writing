import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "clear-technical-writing" / "SKILL.md"
STRICT_REFERENCE = (
    ROOT
    / "skills"
    / "clear-technical-writing"
    / "references"
    / "ste-rules.md"
)


def section(text, heading):
    match = re.search(
        rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"missing section: {heading}")
    return match.group("body")


def frontmatter(text):
    _, value, _ = text.split("---", 2)
    return value


def folded_description(value):
    match = re.search(
        r"^description: >-\n(?P<body>(?:  .+\n)+)",
        value.lstrip(),
        re.MULTILINE,
    )
    if match is None:
        raise AssertionError("missing folded description")
    return " ".join(line.strip() for line in match.group("body").splitlines())


class SkillRouterTest(unittest.TestCase):
    def test_frontmatter_is_valid_and_routing_description_is_bounded(self):
        text = SKILL.read_text()
        metadata = frontmatter(text)
        description = folded_description(metadata)

        self.assertRegex(metadata, r"(?m)^name: clear-technical-writing$")
        self.assertRegex(metadata, r"(?m)^license: MIT$")
        self.assertLessEqual(len(description), 1_024)
        for routing_term in (
            "documentation",
            "runbooks",
            "code review",
            "schema-constrained output",
            "source or generated code",
        ):
            with self.subTest(routing_term=routing_term):
                self.assertIn(routing_term, description)

    def test_router_has_only_an_upper_size_budget(self):
        self.assertLessEqual(len(SKILL.read_bytes()), 4_000)

    def test_modes_keep_strict_rules_explicit_and_procedure_safety_ordered(self):
        modes = section(SKILL.read_text(), "Modes")
        normalized = " ".join(modes.split())

        self.assertRegex(normalized, r"Strict STE.*explicit")
        self.assertIn("conditions before commands", normalized)
        self.assertIn("warnings before dangerous actions", normalized)
        self.assertIn("official Issue 9 dictionary", normalized)

    def test_protected_content_covers_semantic_and_literal_boundaries(self):
        protected = section(SKILL.read_text(), "Protected content")

        for modal in ("must", "should", "can", "may", "might", "could"):
            with self.subTest(modal=modal):
                self.assertIn(f"`{modal}`", protected)

        for boundary in (
            "code",
            "identifiers",
            "commands",
            "paths",
            "quoted",
            "numbers",
            "link",
            "schemas",
            "semantic role",
        ):
            with self.subTest(boundary=boundary):
                self.assertIn(boundary, protected.lower())

    def test_progressive_references_exist_and_have_narrow_loading_rules(self):
        text = SKILL.read_text()
        references = set(re.findall(r"`(references/[^`]+\.md)`", text))

        self.assertEqual(
            references,
            {
                "references/semantic-preservation.md",
                "references/use-cases.md",
                "references/checklist.md",
                "references/ste-rules.md",
            },
        )
        for relative_path in references:
            self.assertTrue((SKILL.parent / relative_path).is_file(), relative_path)
        loading = section(text, "Progressive references")
        self.assertNotIn("final verification", loading.lower())
        self.assertRegex(loading, r"semantic-preservation\.md`.*every source")
        self.assertRegex(loading, r"ste-rules\.md`.*strict")

    def test_hot_path_excludes_project_metadata_and_duplicated_legal_text(self):
        text = SKILL.read_text()

        for excluded in (
            "## Scope",
            "## Strict limit",
            "AminBlg",
            "59bf670",
            "registered trademark",
            "not affiliated",
        ):
            with self.subTest(excluded=excluded):
                self.assertNotIn(excluded, text)
        self.assertIn("cannot certify ASD-STE100 compliance", STRICT_REFERENCE.read_text())


if __name__ == "__main__":
    unittest.main()
