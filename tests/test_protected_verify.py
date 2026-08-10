import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "skills"
    / "clear-technical-writing"
    / "scripts"
    / "protected_verify.py"
)


class ProtectedVerifyTests(unittest.TestCase):
    def run_verify(self, source, draft, env=None):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            source_path = directory / "source.md"
            draft_path = directory / "draft.md"
            source_path.write_text(source)
            draft_path.write_text(draft)
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--source",
                    str(source_path),
                    str(draft_path),
                ],
                capture_output=True,
                text=True,
                timeout=10,
                env=env,
            )
        return result, json.loads(result.stdout)

    def test_rejects_known_protected_content_baselines(self):
        corpus = json.loads(
            (ROOT / "evals" / "fixtures" / "independent-review.json").read_text()
        )
        for fixture in corpus["fixtures"]:
            for baseline in fixture.get("failing_baselines", []):
                if "protected.source-equality" not in baseline.get(
                    "expected_full_scorer_violations", []
                ):
                    continue
                with self.subTest(fixture=fixture["id"], baseline=baseline["id"]):
                    result, report = self.run_verify(
                        fixture["source"],
                        baseline["rewrite"],
                    )
                    self.assertEqual(result.returncode, 1)
                    self.assertFalse(report["ok"])
                    self.assertTrue(report["violations"])

    def test_does_not_claim_to_verify_semantic_roles(self):
        result, report = self.run_verify(
            "Minimum is `low`; maximum is `high`.",
            "Minimum is `high`; maximum is `low`.",
        )

        self.assertEqual(result.returncode, 0)
        self.assertTrue(report["ok"])

    def test_rejects_move_from_heading_to_body(self):
        result, report = self.run_verify(
            "# Release `OPS-6634`\n\nRun cleanup.",
            "# Release\n\nRun cleanup for `OPS-6634`.",
        )

        self.assertEqual(result.returncode, 1)
        self.assertFalse(report["ok"])
        inline = next(
            violation
            for violation in report["violations"]
            if violation["kind"] == "inline-code"
        )
        self.assertEqual(inline["expected"][0]["container"], "heading-1")
        self.assertEqual(inline["actual"][0]["container"], "flow")

    def test_reads_utf8_independent_of_process_locale(self):
        env = os.environ | {"LC_ALL": "C", "PYTHONUTF8": "0"}
        result, report = self.run_verify(
            "Café uses `OPS-6634`.\n",
            "Café uses `OPS-6634`.\n",
            env=env,
        )

        self.assertEqual(result.returncode, 0)
        self.assertTrue(report["ok"])

    def test_accepts_exact_protected_counts_and_containers(self):
        source = (
            "# Release `OPS-6634`\n\n"
            "Run drain-node --ignore-daemonsets for $DEPLOY_ENV at 17:30."
        )
        result, report = self.run_verify(
            source,
            source.replace("Run drain-node", "Execute drain-node"),
        )

        self.assertEqual(result.returncode, 0)
        self.assertTrue(report["ok"])
        self.assertEqual(report["violations"], [])

    def test_ignores_ordered_list_markers_as_structural_numbers(self):
        result, report = self.run_verify(
            "Stop service. Drain node.",
            "1. Stop service.\n2. Drain node.",
        )

        self.assertEqual(result.returncode, 0)
        self.assertTrue(report["ok"])

    def test_rejects_count_and_literal_container_drift(self):
        cases = {
            "inline-to-fence": (
                "Run `kubectl drain node-17 --ignore-daemonsets`.",
                "Run:\n```sh\nkubectl drain node-17 --ignore-daemonsets\n```",
            ),
            "duplicate-inline-identifiers": (
                "Use `OPS-6634` for `export-2027-02-18`.",
                "Use `OPS-6634` for `export-2027-02-18`; record `OPS-6634` again.",
            ),
            "prototype-key-duplicate": (
                "Use `__proto__` once.",
                "Use `__proto__` and `__proto__`.",
            ),
            "link-to-bare-url": (
                "Open [runbook](https://ops.example/runbook?id=17).",
                "Open runbook at https://ops.example/runbook?id=17.",
            ),
            "quoted-diagnostic-edit": (
                "> Error: lease `gpu-17` expired",
                "> Error: lease `gpu-17` was expired",
            ),
            "path-edit": (
                "Copy /srv/releases/v1.7/app.bin.",
                "Copy /srv/releases/v1.8/app.bin.",
            ),
        }
        for name, (source, draft) in cases.items():
            with self.subTest(name=name):
                result, report = self.run_verify(source, draft)
                self.assertEqual(result.returncode, 1)
                self.assertFalse(report["ok"])
                self.assertTrue(report["violations"])

    def test_rejects_changed_cli_flags(self):
        result, report = self.run_verify(
            "Run drain-node --ignore-daemonsets.",
            "Run drain-node --force.",
        )

        self.assertEqual(result.returncode, 1)
        self.assertFalse(report["ok"])
        self.assertEqual(
            [violation["kind"] for violation in report["violations"]],
            ["cli-flag"],
        )

    def test_rejects_changed_environment_variables(self):
        result, report = self.run_verify(
            "Set $RELEASE_ID from ${DEPLOY_ENV}.",
            "Set $RELEASE from ${DEPLOY_ENV}.",
        )

        self.assertEqual(result.returncode, 1)
        self.assertFalse(report["ok"])
        self.assertEqual(
            [violation["kind"] for violation in report["violations"]],
            ["environment-variable"],
        )

    def test_rejects_changed_link_labels(self):
        result, report = self.run_verify(
            "Open [Emergency runbook](https://ops.example/runbook).",
            "Open [Guide](https://ops.example/runbook).",
        )

        self.assertEqual(result.returncode, 1)
        self.assertFalse(report["ok"])
        self.assertEqual(
            [violation["kind"] for violation in report["violations"]],
            ["link-label"],
        )

    def test_rejects_changed_bold_ui_labels(self):
        result, report = self.run_verify(
            "Choose **Witness Matrix**.",
            "Choose **Witness Table**.",
        )

        self.assertEqual(result.returncode, 1)
        self.assertFalse(report["ok"])
        self.assertEqual(
            [violation["kind"] for violation in report["violations"]],
            ["bold-text"],
        )

    def test_rejects_changed_json_keys(self):
        result, report = self.run_verify(
            '{"retry_count": 3, "safe": true}',
            '{"retries": 3, "safe": true}',
        )

        self.assertEqual(result.returncode, 1)
        self.assertFalse(report["ok"])
        self.assertIn(
            "json-key",
            [violation["kind"] for violation in report["violations"]],
        )

    def test_accepts_all_known_safe_fixture_rewrites(self):
        corpus = json.loads(
            (ROOT / "evals" / "fixtures" / "independent-review.json").read_text()
        )
        for fixture in corpus["fixtures"]:
            for rewrite in fixture.get("passing_rewrites", []):
                with self.subTest(fixture=fixture["id"], rewrite=rewrite["id"]):
                    result, report = self.run_verify(
                        fixture["source"],
                        rewrite["rewrite"],
                    )
                    self.assertEqual(result.returncode, 0)
                    self.assertTrue(report["ok"])

    def test_rejects_changed_api_identifiers(self):
        result, report = self.run_verify(
            "Call ApplyPolicy after GPU cleanup.",
            "Call ApplyPolicies after GPU cleanup.",
        )

        self.assertEqual(result.returncode, 1)
        self.assertFalse(report["ok"])
        self.assertEqual(
            [violation["kind"] for violation in report["violations"]],
            ["identifier"],
        )


if __name__ == "__main__":
    unittest.main()
