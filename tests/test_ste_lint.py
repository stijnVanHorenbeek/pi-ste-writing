import json
import re
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "clear-technical-writing" / "scripts" / "ste_lint.py"
DISCLAIMER = "Advisory only; does not certify ASD-STE100 compliance."
MODAL_MESSAGE = (
    'Review modal "should"; preserve its meaning. '
    "Strict STE may require a different construction."
)


def run_cli(*args, input_text=""):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def run_json(text, mode="strict", *extra_args):
    result = run_cli(
        "--mode",
        mode,
        "--format",
        "json",
        *extra_args,
        "-",
        input_text=text,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"linter failed with {result.returncode}: {result.stderr or result.stdout}"
        )
    return json.loads(result.stdout)


def assert_finding_contract(test_case, finding):
    required = {
        "rule",
        "category",
        "severity",
        "source",
        "line",
        "column",
        "text",
        "message",
    }
    test_case.assertLessEqual(required, set(finding))
    test_case.assertEqual(finding["severity"], "warning")
    test_case.assertTrue(finding["source"])
    test_case.assertGreaterEqual(finding["line"], 1)
    test_case.assertGreaterEqual(finding["column"], 1)
    test_case.assertTrue(finding["text"])
    test_case.assertTrue(finding["message"])


class MarkdownProtectionTest(unittest.TestCase):
    def test_ignores_frontmatter_code_urls_links_and_diagnostics(self):
        text = """---
title: You shouldn't retry if startup fails
reference: https://example.com/should/retry?if=ready
---
# Retry behavior

Use `you shouldn't retry if startup fails`.
Read the [retry guide](https://example.com/shouldn't/retry?if=ready).

```bash
echo "you shouldn't retry if startup fails"
```

> Error: You shouldn't retry if startup fails.

The client should retry.
"""

        report = run_json(text)

        self.assertEqual(report["summary"]["warnings"], 1)
        self.assertEqual(report["findings"][0]["rule"], "modal")
        self.assertEqual(report["findings"][0]["text"], "should")
        self.assertEqual(report["findings"][0]["line"], 16)

    def test_lints_heading_and_link_label_but_not_url_text(self):
        text = """# You should retry

Read [why you may retry](https://example.com/should/may?if=ready).
Source URL: https://example.com/might/could?when=ready
"""

        report = run_json(text)
        modal_text = [
            finding["text"].lower()
            for finding in report["findings"]
            if finding["rule"] == "modal"
        ]

        self.assertEqual(modal_text, ["should", "may"])


class SentenceParsingTest(unittest.TestCase):
    def test_versions_and_abbreviations_do_not_break_sentence_length(self):
        text = (
            "The API v3.8.2 accepts common formats, e.g. JSON and YAML, while the "
            "worker preserves every field, retries failed uploads, and records detailed "
            "results for later incident analysis."
        )

        report = run_json(text)
        rules = [finding["rule"] for finding in report["findings"]]

        self.assertEqual(rules.count("sentence-length"), 1)
        self.assertEqual(rules.count("latin-abbreviation"), 1)

    def test_detects_contractions_but_not_possessive_apostrophes(self):
        text = (
            "It isn't ready. I can't start. It's blocked. You're waiting. We'll retry. "
            "They've stopped. I'd wait. You'd continue. The owner's guide is current."
        )

        report = run_json(text)
        contractions = [
            finding for finding in report["findings"] if finding["rule"] == "contraction"
        ]

        self.assertEqual(
            Counter(finding["text"] for finding in contractions),
            Counter(
                {
                    "isn't": 1,
                    "can't": 1,
                    "It's": 1,
                    "You're": 1,
                    "We'll": 1,
                    "They've": 1,
                    "I'd": 1,
                    "You'd": 1,
                }
            ),
        )
        self.assertNotIn("owner's", {finding["text"] for finding in contractions})


class ModalSafetyTest(unittest.TestCase):
    def test_warns_about_strict_modals_without_replacement_advice(self):
        text = (
            "Operators must retain backups. Administrators can rotate keys. "
            "Operators should test restores. Rotation may interrupt sessions. "
            "Propagation might take ten minutes. Older clients could reconnect."
        )

        report = run_json(text)
        modal_findings = [
            finding for finding in report["findings"] if finding["rule"] == "modal"
        ]

        self.assertEqual(
            Counter(finding["text"].lower() for finding in modal_findings),
            Counter({"should": 1, "may": 1, "might": 1, "could": 1}),
        )
        for finding in modal_findings:
            self.assertEqual(
                finding["message"],
                f'Review modal "{finding["text"]}"; preserve its meaning. '
                "Strict STE may require a different construction.",
            )
            assert_finding_contract(self, finding)


class ProcedureClassificationTest(unittest.TestCase):
    def test_trailing_condition_warning_is_procedure_mode_only(self):
        sentence = "Restart the worker if health checks fail."

        clear_report = run_json(sentence, "clear")
        strict_report = run_json(sentence, "strict")
        procedure_report = run_json(sentence, "procedure")

        for report in (clear_report, strict_report):
            self.assertNotIn(
                "condition-order",
                {finding["rule"] for finding in report["findings"]},
            )
        self.assertEqual(
            [
                finding["rule"]
                for finding in procedure_report["findings"]
                if finding["rule"] == "condition-order"
            ],
            ["condition-order"],
        )

    def test_mixed_prose_warns_only_for_trailing_condition_on_instruction(self):
        text = (
            "The service records an event when the job fails. "
            "Restart the worker if health checks fail. "
            "If health checks fail, restart the worker."
        )

        report = run_json(text, "procedure")
        findings = [
            finding
            for finding in report["findings"]
            if finding["rule"] == "condition-order"
        ]

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["text"], "Restart the worker if health checks fail.")
        self.assertEqual(findings[0]["category"], "procedure")
        assert_finding_contract(self, findings[0])


class ProtectedSpanComparisonTest(unittest.TestCase):
    SOURCE = """Call `ApplyPolicy`.
Read [policy docs](https://docs.example.test/policy?v=3).

```bash
policyctl apply --file /etc/policy.yaml
```

> Error: `invalid field "mode"`
"""

    def run_comparison(self, rewrite):
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "source.md"
            rewrite_path = Path(directory) / "rewrite.md"
            source_path.write_text(self.SOURCE)
            rewrite_path.write_text(rewrite)
            result = run_cli(
                "--mode",
                "clear",
                "--format",
                "json",
                "--source",
                str(source_path),
                str(rewrite_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)

    def test_equal_protected_spans_produce_no_semantic_warning(self):
        report = self.run_comparison(self.SOURCE)

        self.assertNotIn(
            "protected-span",
            {finding["rule"] for finding in report["findings"]},
        )

    def test_changed_protected_containers_report_each_kind(self):
        rewrite = """Call `ApplyPolicies`.
The old URL was https://docs.example.test/policy?v=3.
Read [policy docs](https://docs.example.test/policy?v=4).

```bash
policyctl apply --file /etc/policy.yaml --force
```

> Error: `invalid field "policy_mode"`
"""

        report = self.run_comparison(rewrite)
        findings = [
            finding
            for finding in report["findings"]
            if finding["rule"] == "protected-span"
        ]

        self.assertEqual(
            Counter(finding["protected_kind"] for finding in findings),
            Counter(
                {
                    "inline-code": 1,
                    "fenced-code": 1,
                    "link-destination": 1,
                    "quoted-diagnostic": 1,
                }
            ),
        )
        self.assertTrue(all(finding["category"] == "semantic" for finding in findings))
        for finding in findings:
            assert_finding_contract(self, finding)

    def test_added_duplicate_protected_span_fails_equality(self):
        rewrite = self.SOURCE + "\nCall `ApplyPolicy` again.\n"

        report = self.run_comparison(rewrite)
        protected_kinds = [
            finding["protected_kind"]
            for finding in report["findings"]
            if finding["rule"] == "protected-span"
        ]

        self.assertEqual(protected_kinds, ["inline-code"])


class ExitBehaviorTest(unittest.TestCase):
    def test_default_mode_is_clear(self):
        result = run_cli(
            "--format",
            "json",
            "-",
            input_text="Restart the worker if health checks fail. You should retry.",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["mode"], "clear")
        self.assertNotIn(
            "condition-order",
            {finding["rule"] for finding in report["findings"]},
        )
        self.assertNotIn("modal", {finding["rule"] for finding in report["findings"]})

    def test_advisory_warnings_exit_zero_by_default(self):
        result = run_cli(
            "--mode",
            "strict",
            "--format",
            "json",
            "-",
            input_text="You should retry.",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["summary"]["warnings"], 1)

    def test_strict_gate_exits_one_when_warnings_exist(self):
        result = run_cli(
            "--mode",
            "strict",
            "--format",
            "json",
            "--strict-gate",
            "-",
            input_text="You should retry.",
        )

        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["summary"]["warnings"], 1)

    def test_invocation_error_exits_two_and_uses_stderr(self):
        result = run_cli(
            "--mode",
            "unknown",
            "--format",
            "json",
            "-",
            input_text="Text.",
        )

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("invalid choice", result.stderr)

    def test_missing_input_exits_two_and_uses_stderr(self):
        missing_path = ROOT / "does-not-exist.md"

        result = run_cli(
            "--mode",
            "clear",
            "--format",
            "json",
            str(missing_path),
        )

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("cannot read input", result.stderr)


class OutputContractTest(unittest.TestCase):
    EXPECTED_REPORT = {
        "advisory": True,
        "mode": "strict",
        "findings": [
            {
                "rule": "modal",
                "category": "semantic",
                "severity": "warning",
                "source": "<stdin>",
                "line": 1,
                "column": 5,
                "text": "should",
                "message": MODAL_MESSAGE,
            }
        ],
        "summary": {"warnings": 1},
        "disclaimer": DISCLAIMER,
    }

    def test_json_output_is_stable(self):
        result = run_cli(
            "--mode",
            "strict",
            "--format",
            "json",
            "-",
            input_text="You should retry.\n",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, json.dumps(self.EXPECTED_REPORT, indent=2) + "\n")

    def test_human_output_is_stable(self):
        result = run_cli(
            "--mode",
            "strict",
            "--format",
            "text",
            "-",
            input_text="You should retry.\n",
        )
        expected = (
            "ste-lint: 1 warning (strict mode)\n"
            f"<stdin>:1:5: warning modal/semantic: {MODAL_MESSAGE}\n"
            f"{DISCLAIMER}\n"
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, expected)

    def test_output_never_claims_certification_or_compliance(self):
        for output_format in ("json", "text"):
            with self.subTest(output_format=output_format):
                result = run_cli(
                    "--mode",
                    "strict",
                    "--format",
                    output_format,
                    "-",
                    input_text="The system retries failed jobs.\n",
                )
                output = result.stdout

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(DISCLAIMER, output)
                claims_only = output.replace(DISCLAIMER, "")
                self.assertIsNone(
                    re.search(
                        r"(?is)\bASD-STE100\b.{0,50}\b(compliant|compliance|certif\w*)\b",
                        claims_only,
                    )
                )
                self.assertIsNone(
                    re.search(
                        r"(?is)\b(certif\w*|fully|passes?)\b.{0,50}\bASD-STE100\b",
                        claims_only,
                    )
                )


if __name__ == "__main__":
    unittest.main()
