import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "clear-technical-writing" / "SKILL.md"
README = ROOT / "README.md"
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


def normalized_text(text):
    lines = [re.sub(r"^\s*>\s?", "", line) for line in text.splitlines()]
    return " ".join("\n".join(lines).split())


def frontmatter_description(text):
    match = re.search(
        r"^description: >-\n(?P<body>(?:  .+\n)+)",
        text.split("---", 2)[1].lstrip(),
        re.MULTILINE,
    )
    if match is None:
        raise AssertionError("missing folded description")
    return " ".join(line.strip() for line in match.group("body").splitlines())


class SkillRouterTest(unittest.TestCase):
    def test_skill_exists_below_hard_progressive_disclosure_budget(self):
        size = len(SKILL.read_bytes())

        self.assertLessEqual(size, 6_000)

    def test_frontmatter_is_pi_compatible_and_activation_is_narrow(self):
        text = SKILL.read_text()
        frontmatter = text.split("---", 2)[1]
        description = frontmatter_description(text)

        self.assertIn("name: clear-technical-writing", frontmatter)
        self.assertIn("license: MIT", frontmatter)
        self.assertIn("compatibility:", frontmatter)
        self.assertIn("Pi", frontmatter)
        self.assertNotIn("metadata:", frontmatter)
        self.assertNotIn("AminBlg/SimpleEnglish", frontmatter)
        self.assertNotIn("59bf6702197a5aadc96d197ea17f290d8d50dcd3", frontmatter)
        self.assertLessEqual(len(description), 1_024)

        included = [
            "documentation and READMEs",
            "API guides",
            "setup procedures and runbooks",
            "user-facing error messages and CLI help",
            "incident reports and postmortems",
            "release notes and changelogs",
            "translation-ready prose",
            "explicit STE, ASD-STE100, or STE-compliance audits",
        ]
        excluded = [
            "code review",
            "debugging",
            "architecture analysis or design tradeoffs",
            "test-result interpretation",
            "patch summaries without a writing-pass request",
            "raw tool output, logs, and quoted diagnostics",
            "JSON, XML, YAML, CSV, or schema-constrained output",
            "source or generated code",
            "marketing",
            "brand, or editorial voice",
        ]
        for phrase in included + excluded:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, description)

        self.assertNotIn("destructive operations", description)
        self.assertNotIn("or compliance audits", description)

    def test_decision_hierarchy_is_complete_and_authoritative(self):
        text = SKILL.read_text()
        positions = [text.find(item) for item in DECISION_HIERARCHY]

        self.assertNotIn(-1, positions)
        self.assertEqual(positions, sorted(positions))
        self.assertIn("A lower item cannot override a higher item", text)
        self.assertIn("Preserve the source and report the conflict", text)

    def test_clear_procedure_and_strict_modes_have_safe_boundaries(self):
        text = SKILL.read_text()
        normalized = normalized_text(text)
        required = [
            "**Clear (default):**",
            "Do not apply the strict vocabulary or hard sentence limits",
            "**Procedure:**",
            "Use imperative instructions where appropriate",
            "action-controlling conditions before commands",
            "one action per numbered step",
            "warnings before dangerous actions",
            "required action before the possible consequence",
            "20 words or fewer",
            "**Strict STE:**",
            "only after an explicit request",
            "20-word procedural and 25-word descriptive limits",
            "official Issue 9 dictionary",
            "Classify mixed documents passage by passage",
            "A note inside a procedure is descriptive",
        ]
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)

        self.assertNotIn("Strict STE (default)", normalized)

    def test_protected_content_requires_exact_role_aware_preservation(self):
        normalized = normalized_text(SKILL.read_text()).casefold()
        required = [
            "Unless the user explicitly requests a targeted change",
            "fenced and inline code",
            "identifiers, API names, and schema fields",
            "commands, flags, paths, URLs, and environment variables",
            "product names, UI labels, protocol terms, and repository terminology",
            "quoted errors, logs, diagnostics, and test output",
            "numbers, dates, versions, percentages, units, limits, and ranges",
            "Markdown link destinations, reference IDs, and anchors",
            "machine-readable structure and exact output schemas",
            "value, occurrence count, container, and semantic role",
            "Do not rewrite raw output",
            "Only the explicitly targeted item becomes editable",
        ]
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.casefold(), normalized)

    def test_compact_workflow_routes_to_progressive_references_and_linter(self):
        text = SKILL.read_text()
        normalized = normalized_text(text)
        workflow = [
            "1. Identify the audience, requested mode, and exact output contract.",
            "2. Inventory invariants and build a semantic ledger",
            "3. Classify each passage",
            "4. Rewrite only eligible prose",
            "5. Compare source and draft claim by claim",
            "6. Check protected values by occurrence, container, and role.",
            "7. Optionally run the advisory linter",
        ]
        positions = [normalized.find(step) for step in workflow]
        self.assertNotIn(-1, positions)
        self.assertEqual(positions, sorted(positions))

        reference_rules = [
            "Load `references/semantic-preservation.md` for every source-based rewrite or audit",
            "Load `references/use-cases.md` only when routing, scope, or coding examples are needed",
            "Load `references/checklist.md` for every strict task, requested audit, high-risk procedure, or final verification",
            "Load `references/ste-rules.md` only in strict mode",
        ]
        for rule in reference_rules:
            with self.subTest(rule=rule):
                self.assertIn(rule, normalized)

        paths = [
            "references/semantic-preservation.md",
            "references/use-cases.md",
            "references/checklist.md",
            "references/ste-rules.md",
            "scripts/ste_lint.py",
        ]
        for relative in paths:
            with self.subTest(relative=relative):
                self.assertIn(f"`{relative}`", text)
                self.assertTrue((SKILL.parent / relative).is_file())

        self.assertIn(
            "python3 scripts/ste_lint.py --mode MODE --format json --source SOURCE DRAFT",
            text,
        )
        self.assertIn("Findings are advisory", normalized)
        self.assertIn("`--strict-gate`", text)
        self.assertEqual(len(re.findall(r"\bRule \d", text)), 0)

    def test_scope_excludes_normal_coding_reasoning_and_protected_outputs(self):
        normalized = normalized_text(SKILL.read_text())
        required = [
            "Do not auto-apply this skill to code-review findings, debugging hypotheses, architecture analysis, design tradeoffs, test-result interpretation, or patch summaries",
            "Do not auto-apply it to source code, generated code, raw tool output, logs, quoted diagnostics, JSON, XML, YAML, CSV, schema-constrained output, marketing, brand, or editorial voice",
            "Complete technical reasoning first",
            "An exact `/skill:clear-technical-writing` invocation can override an activation exclusion only when the requested transformation is safe",
            "Invocation alone does not authorize semantic drift",
        ]
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)

    def test_strict_disclaimer_and_package_attribution_are_explicit(self):
        text = SKILL.read_text()
        readme = README.read_text()
        normalized = normalized_text(text)
        size = len(text.encode())

        self.assertGreaterEqual(size, 4_000)
        self.assertLessEqual(size, 5_500)
        self.assertIn(
            "This audit is advisory and cannot certify ASD-STE100 compliance. Final approval rests with the writer using the official standard and dictionary.",
            normalized,
        )
        self.assertIn("ASD-STE100 is a registered trademark of ASD", normalized)
        self.assertIn("not affiliated with ASD, STEMG, or the upstream project", normalized)
        self.assertNotIn("AminBlg/SimpleEnglish", text)
        self.assertNotIn("skills/simple-english/SKILL.md", text)
        self.assertNotIn("59bf6702197a5aadc96d197ea17f290d8d50dcd3", text)
        self.assertIn("AminBlg/SimpleEnglish", readme)
        self.assertIn("59bf6702197a5aadc96d197ea17f290d8d50dcd3", readme)
        self.assertIn("MIT", readme)

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
