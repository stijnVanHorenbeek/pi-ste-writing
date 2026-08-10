import json
import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXTENSION = ROOT / "extensions" / "clear-writing-guard.ts"


class ProtectedContentNodeTests(unittest.TestCase):
    def test_node_verifier_suite(self):
        result = subprocess.run(
            ["node", "--test", str(ROOT / "tests" / "guard-session.test.ts")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class PackageManifestTests(unittest.TestCase):
    def test_package_exposes_extension_and_runtime_files(self):
        manifest = json.loads((ROOT / "package.json").read_text())
        self.assertEqual(manifest["version"], "0.1.0-rc.1")
        self.assertEqual(
            manifest["pi"]["extensions"],
            ["./extensions/clear-writing-guard.ts"],
        )
        self.assertIn("extensions", manifest["files"])
        self.assertIn("docs", manifest["files"])
        self.assertEqual(
            manifest["peerDependencies"],
            {
                "@earendil-works/pi-coding-agent": "*",
                "typebox": "*",
            },
        )


    def test_package_dry_run_includes_guard_without_bundled_dependencies(self):
        result = subprocess.run(
            ["npm", "pack", "--dry-run", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        package = next(iter(payload.values())) if isinstance(payload, dict) else payload[0]
        paths = {entry["path"] for entry in package["files"]}
        self.assertIn("extensions/clear-writing-guard.ts", paths)
        self.assertIn(
            "skills/clear-technical-writing/scripts/protected_verify.py",
            paths,
        )
        self.assertIn("docs/guarded-verifier-contract.md", paths)
        self.assertNotIn("docs/v2-verifier-contract.md", paths)
        self.assertEqual(package.get("bundled", []), [])


class ExtensionDiscoveryTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("pi"), "pi is required for extension discovery")
    def test_pi_discovers_opt_in_clear_write_command(self):
        process = subprocess.Popen(
            [
                "pi",
                "--mode",
                "rpc",
                "--no-session",
                "--no-skills",
                "-e",
                str(EXTENSION),
            ],
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            stdout, stderr = process.communicate(
                json.dumps({"id": "commands", "type": "get_commands"}) + "\n",
                timeout=20,
            )
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            self.fail(f"Pi RPC command timed out.\nstdout:\n{stdout}\nstderr:\n{stderr}")

        records = [json.loads(line) for line in stdout.splitlines() if line.strip()]
        response = next(
            record
            for record in records
            if record.get("type") == "response" and record.get("id") == "commands"
        )
        self.assertTrue(response["success"], response)
        names = [command["name"] for command in response["data"]["commands"]]
        self.assertIn("clear-write", names)
        self.assertEqual(stderr, "")

    @unittest.skipUnless(shutil.which("pi"), "pi is required for extension discovery")
    def test_invalid_guard_mode_fails_before_model_call(self):
        process = subprocess.Popen(
            [
                "pi",
                "--mode",
                "rpc",
                "--no-session",
                "--no-skills",
                "-e",
                str(EXTENSION),
            ],
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate(
            json.dumps(
                {
                    "id": "invalid",
                    "type": "prompt",
                    "message": "/clear-write --mode unsafe source",
                }
            )
            + "\n",
            timeout=20,
        )
        records = [json.loads(line) for line in stdout.splitlines() if line.strip()]
        response = next(
            record
            for record in records
            if record.get("type") == "response" and record.get("id") == "invalid"
        )
        notifications = [
            record
            for record in records
            if record.get("type") == "extension_ui_request"
            and record.get("method") == "notify"
        ]
        self.assertTrue(response["success"], response)
        self.assertEqual(len(notifications), 1)
        self.assertIn("Unknown mode: unsafe", notifications[0]["message"])
        self.assertFalse(any(record.get("type") == "agent_start" for record in records))
        self.assertEqual(stderr, "")


if __name__ == "__main__":
    unittest.main()
