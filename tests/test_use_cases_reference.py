import re
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = (
    ROOT
    / "skills"
    / "clear-technical-writing"
    / "references"
    / "use-cases.md"
)
NUMERIC_TOKEN_PATTERN = re.compile(
    r"(?<![\w.])(?:\d{1,2}:\d{2}(?::\d{2})?|"
    r"v?\d[\d,]*(?:\.\d+)*(?:-\d[\d,]*(?:\.\d+)*)*%?"
    r"(?:\s*(?:ms|seconds?|minutes?|hours?|days?|MB|GB|TB))?)",
    re.IGNORECASE,
)
REQUIRED_HEADINGS = [
    "## READMEs and API guides",
    "## Setup procedures and runbooks",
    "## User-facing CLI errors",
    "## Incident reports and postmortems",
    "## Release notes and changelogs",
    "## Patch and test summaries",
    "## Destructive operations and security warnings",
    "## Translation preparation",
    "## Scope boundaries",
]
EXAMPLE_CONTRACTS = {
    "## READMEs and API guides": {
        "values": [
            "Acme SDK",
            "Python 3.12",
            "Linux",
            "Windows",
            "`acme.Client`",
            "`/v1/jobs`",
            "`timeout_ms`",
            "5000",
        ],
        "claims": [
            "does not support Windows",
            "`timeout_ms` is optional",
            "The default is 5000",
        ],
    },
    "## Setup procedures and runbooks": {
        "values": [
            "`acme-cli==3.8.2`",
            "`CHG-913`",
            "`acme check`",
            "`acme migrate --database orders`",
            "15 minutes",
        ],
        "claims": [
            "You must obtain approval",
            "If `acme check` succeeds",
            "can take up to 15 minutes",
            "Do not run two migrations at the same time",
        ],
    },
    "## User-facing CLI errors": {
        "values": [
            "`db-prod`",
            "12:30 UTC",
            "`app`",
            "`DB_PASSWORD`",
            "`acmectl connect db-prod`",
        ],
        "claims": [
            "The cause remains unknown",
            "may have expired",
            "If the password expired",
        ],
    },
    "## Incident reports and postmortems": {
        "values": [
            "14:02",
            "14:31 UTC",
            "12%",
            "14:00 UTC",
            "73%",
        ],
        "claims": [
            "timing correlation only",
            "The root cause remains unknown",
            "contributed to 73% of the failed requests",
            "No evidence shows data loss",
        ],
    },
    "## Release notes and changelogs": {
        "values": [
            "`v3.8.2`",
            "`retry_count`",
            "from 3 to 5",
            "`/v1/jobs`",
            "2027-01-15",
            "`/v2/jobs`",
        ],
        "claims": [
            "for new profiles only",
            "Existing profiles are unchanged",
            "remains available until 2027-01-15",
            "Users should migrate",
        ],
    },
    "## Patch and test summaries": {
        "values": [
            "`ParseConfig`",
            "`timeout`",
            "`go test ./...`",
            "87 tests",
        ],
        "claims": [
            "The patch changes `ParseConfig` to reject duplicate `timeout` keys",
            "CLI output is unchanged",
            "The race detector was not run",
            "The reviewer should inspect compatibility",
        ],
    },
    "## Destructive operations and security warnings": {
        "values": [
            "`CHG-4821`",
            "`snap-2026-07-14`",
            "`kubectl delete namespace payments`",
            "`kubectl get namespace payments`",
            "`token-id-7F3`",
            "`PAYMENTS_API_KEY`",
        ],
        "claims": [
            "must be approved before deletion",
            "Snapshot `snap-2026-07-14` must be complete before deletion",
            "Deletion is permanent",
            "Recovery requires `snap-2026-07-14`",
            "must be revoked before deployment",
            "Deleting the log does not revoke the token",
            "After revocation, rotate `PAYMENTS_API_KEY`",
        ],
    },
    "## Translation preparation": {
        "values": [
            "`Settings`",
            "`retry_delay`",
            "5 seconds",
            "30 seconds",
            "`%d`",
        ],
        "claims": [
            "The default retry delay is 5 seconds",
            "A timeout may occur after 30 seconds",
            "Translators must not translate `retry_delay`",
            "The translation output must keep `%d` exactly",
        ],
    },
}
APPROVED_EXAMPLES = {
    "## READMEs and API guides": (
        "The Acme SDK supports Python 3.12 on Linux. It does not support Windows. "
        "`acme.Client` sends requests to `/v1/jobs`. `timeout_ms` is optional. "
        "Its default is 5000.",
        "Acme SDK supports Python 3.12 on Linux. It does not support Windows. The "
        "`acme.Client` sends requests to `/v1/jobs`. The `timeout_ms` is optional. "
        "The default is 5000.",
    ),
    "## Setup procedures and runbooks": (
        "1. Install `acme-cli==3.8.2`.\n"
        "2. You must obtain approval for `CHG-913` before the migration.\n"
        "3. If `acme check` succeeds, run `acme migrate --database orders`.\n\n"
        "The migration can take up to 15 minutes. Do not run two migrations at "
        "the same time.",
        "1. Install `acme-cli==3.8.2`.\n"
        "2. You must obtain approval for `CHG-913` before the migration.\n\n"
        "WARNING: Do not run two migrations at the same time. The migration can "
        "take up to 15 minutes.\n\n"
        "3. If `acme check` succeeds, run `acme migrate --database orders`.",
    ),
    "## User-facing CLI errors": (
        "Connection to `db-prod` failed at 12:30 UTC. The cause is unknown. The "
        "password for user `app` may have expired. If the password expired, set "
        "`DB_PASSWORD`. Then run `acmectl connect db-prod` again.",
        "Connection to `db-prod` failed at 12:30 UTC. The cause remains unknown. "
        "The password for user `app` may have expired.\n\n"
        "If the password expired:\n"
        "- Set `DB_PASSWORD`.\n"
        "- Run `acmectl connect db-prod` again.",
    ),
    "## Incident reports and postmortems": (
        "Between 14:02 and 14:31 UTC, 12% of requests failed. The deployment "
        "started at 14:00 UTC. The evidence shows timing correlation only, and "
        "the root cause is unknown. Cache misses contributed to 73% of the failed "
        "requests. No evidence shows data loss.",
        "Between 14:02 and 14:31 UTC, 12% of requests failed. The deployment "
        "started at 14:00 UTC, but the evidence shows timing correlation only. "
        "The root cause remains unknown. Cache misses contributed to 73% of the "
        "failed requests. No evidence shows data loss.",
    ),
    "## Release notes and changelogs": (
        "Version `v3.8.2` changes the default `retry_count` from 3 to 5 for new "
        "profiles only. Existing profiles are unchanged. The `/v1/jobs` endpoint "
        "is deprecated but remains available until 2027-01-15. Users should "
        "migrate to `/v2/jobs` before that date.",
        "- In `v3.8.2`, the default `retry_count` changes from 3 to 5 for new "
        "profiles only. Existing profiles are unchanged.\n"
        "- The `/v1/jobs` endpoint is deprecated but remains available until "
        "2027-01-15. Users should migrate to `/v2/jobs` before that date.",
    ),
    "## Patch and test summaries": (
        "The patch changes `ParseConfig` to reject duplicate `timeout` keys. CLI "
        "output is unchanged. `go test ./...` passed 87 tests. The race detector "
        "was not run. The reviewer should inspect compatibility with users that "
        "depend on duplicate keys.",
        "- The patch changes `ParseConfig` to reject duplicate `timeout` keys.\n"
        "- CLI output is unchanged.\n"
        "- `go test ./...` passed 87 tests. The race detector was not run.\n"
        "- The reviewer should inspect compatibility with users that depend on "
        "duplicate keys.",
    ),
    "## Destructive operations and security warnings": (
        "1. Change request `CHG-4821` must be approved before deletion.\n"
        "2. Run `kubectl delete namespace payments`.\n"
        "3. Then check status with `kubectl get namespace payments`.\n\n"
        "Snapshot `snap-2026-07-14` must be complete before deletion. Deletion "
        "is permanent. Recovery requires `snap-2026-07-14`.\n\n"
        "Token `token-id-7F3` was exposed in a log. It must be revoked before "
        "deployment. Deleting the log does not revoke the token.\n\n"
        "1. Revoke the token before deployment.\n"
        "2. After revocation, rotate `PAYMENTS_API_KEY`.",
        "WARNING: Snapshot `snap-2026-07-14` must be complete before deletion. "
        "Deletion is permanent. Recovery requires `snap-2026-07-14`.\n\n"
        "1. Change request `CHG-4821` must be approved before deletion.\n"
        "2. Run `kubectl delete namespace payments`.\n"
        "3. Check status with `kubectl get namespace payments`.\n\n"
        "SECURITY WARNING: Token `token-id-7F3` was exposed in a log and must be "
        "revoked before deployment. Deleting the log does not revoke the token.\n\n"
        "1. Revoke the token before deployment.\n"
        "2. After revocation, rotate `PAYMENTS_API_KEY`.",
    ),
    "## Translation preparation": (
        "The `Settings` screen shows `retry_delay`. The default retry delay is 5 "
        "seconds. A timeout may occur after 30 seconds. Translators must not "
        "translate `retry_delay`. The translation output must keep `%d` exactly.",
        "The `Settings` screen shows `retry_delay`. The default retry delay is 5 "
        "seconds. A timeout may occur after 30 seconds. Translators must not "
        "translate `retry_delay`. The translation output must keep `%d` exactly.",
    ),
}


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


def replace_in_rewrite(text, heading, old, new):
    section_start = text.index(heading)
    section_end = text.find("\n## ", section_start + len(heading))
    if section_end == -1:
        section_end = len(text)
    section = text[section_start:section_end]
    rewrite = fenced_example(section, "Safe rewrite")
    if old not in rewrite:
        raise AssertionError(f"missing mutation target: {old}")
    changed = rewrite.replace(old, new, 1)
    rewrite_start = section.index(rewrite)
    updated_section = (
        section[:rewrite_start]
        + changed
        + section[rewrite_start + len(rewrite) :]
    )
    return text[:section_start] + updated_section + text[section_end:]


def assert_example_contracts(testcase, text):
    for heading, contract in EXAMPLE_CONTRACTS.items():
        section = section_for(text, heading)
        source = fenced_example(section, "Source text")
        rewrite = fenced_example(section, "Safe rewrite")
        testcase.assertEqual((source, rewrite), APPROVED_EXAMPLES[heading])

        for value in contract["values"]:
            testcase.assertGreater(source.count(value), 0)
            testcase.assertEqual(source.count(value), rewrite.count(value))
        for claim in contract["claims"]:
            testcase.assertIn(claim, rewrite)


class UseCasesReferenceTest(unittest.TestCase):
    def test_required_coding_use_cases_exist_in_order(self):
        text = REFERENCE.read_text()
        positions = [text.find(heading) for heading in REQUIRED_HEADINGS]

        self.assertNotIn(-1, positions)
        self.assertEqual(positions, sorted(positions))

    def test_each_example_declares_mode_source_rewrite_and_preservation_check(self):
        text = REFERENCE.read_text()
        self.assertEqual(text.count("**Source text**"), len(EXAMPLE_CONTRACTS))
        self.assertEqual(text.count("**Safe rewrite**"), len(EXAMPLE_CONTRACTS))
        self.assertNotIn("**Unsafe rewrite**", text)

        for heading in REQUIRED_HEADINGS[:-1]:
            section = section_for(text, heading)
            with self.subTest(heading=heading):
                self.assertIn("**Mode:**", section)
                self.assertIn("**Source text**", section)
                self.assertIn("**Safe rewrite**", section)
                self.assertIn("**Preservation check:**", section)
                source = fenced_example(section, "Source text")
                rewrite = fenced_example(section, "Safe rewrite")
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

    def test_rewrites_preserve_enumerated_values_facts_and_qualifications(self):
        assert_example_contracts(self, REFERENCE.read_text())

    def test_contracts_reject_semantic_mutations_and_invented_success(self):
        text = REFERENCE.read_text()
        mutations = [
            (
                "## READMEs and API guides",
                "supports Python 3.12",
                "does not support Python 3.12",
            ),
            (
                "## Setup procedures and runbooks",
                "Install `acme-cli==3.8.2`",
                "Do not install `acme-cli==3.8.2`",
            ),
            (
                "## User-facing CLI errors",
                "Connection to `db-prod` failed",
                "Connection to `db-prod` succeeded",
            ),
            (
                "## Incident reports and postmortems",
                "12% of requests failed",
                "12% of requests succeeded",
            ),
            (
                "## Release notes and changelogs",
                "endpoint is deprecated",
                "endpoint is supported",
            ),
            (
                "## Patch and test summaries",
                "passed 87 tests",
                "failed 87 tests",
            ),
            (
                "## Destructive operations and security warnings",
                "was exposed in a log",
                "was not exposed in a log",
            ),
            (
                "## Translation preparation",
                "screen shows `retry_delay`",
                "screen does not show `retry_delay`",
            ),
            (
                "## Patch and test summaries",
                "The race detector was not run.",
                "The race detector was not run. All tests succeeded.",
            ),
        ]
        for heading, old, new in mutations:
            with self.subTest(heading=heading, mutation=new):
                mutated = replace_in_rewrite(text, heading, old, new)
                with self.assertRaises(AssertionError):
                    assert_example_contracts(self, mutated)

    def test_procedure_rewrites_preserve_required_action_order(self):
        text = REFERENCE.read_text()
        ordered_phrases = {
            "## Setup procedures and runbooks": [
                "1. Install `acme-cli==3.8.2`",
                "2. You must obtain approval",
                "WARNING: Do not run two migrations",
                "3. If `acme check` succeeds",
                "run `acme migrate --database orders`",
            ],
            "## User-facing CLI errors": [
                "If the password expired",
                "- Set `DB_PASSWORD`",
                "- Run `acmectl connect db-prod` again",
            ],
            "## Destructive operations and security warnings": [
                "WARNING: Snapshot `snap-2026-07-14` must be complete",
                "1. Change request `CHG-4821` must be approved",
                "2. Run `kubectl delete namespace payments`",
                "3. Check status with `kubectl get namespace payments`",
                "SECURITY WARNING:",
                "1. Revoke the token before deployment",
                "2. After revocation, rotate `PAYMENTS_API_KEY`",
            ],
        }
        for heading, phrases in ordered_phrases.items():
            rewrite = fenced_example(section_for(text, heading), "Safe rewrite")
            positions = [rewrite.find(phrase) for phrase in phrases]
            with self.subTest(heading=heading):
                self.assertNotIn(-1, positions)
                self.assertEqual(positions, sorted(positions))

    def test_scope_boundaries_match_pi_activation_contract(self):
        text = REFERENCE.read_text()
        section = section_for(text, "## Scope boundaries")
        rows = {}
        for line in section.splitlines():
            if not line.startswith("|") or line.startswith("|---"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if cells[0] == "Context":
                continue
            rows[cells[0]] = cells[1]

        expected_routes = {
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
        }
        self.assertEqual(rows, expected_routes)

        required = [
            "Use automatic activation only",
            "Explicit Pi invocation can override an activation exclusion",
            "/skill:clear-technical-writing",
            "complete technical reasoning first",
            "Strict STE mode activates only after an explicit request",
            "Exact invocation does not by itself permit",
            "explicitly requests a targeted safe change",
            "derived text is not raw output",
        ]
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, section)

        self.assertNotIn("strict by default", text.casefold())

    def test_provenance_and_certification_boundary_are_explicit(self):
        text = REFERENCE.read_text()
        required = [
            "cannot certify ASD-STE100 compliance",
            "## Provenance",
            "skills/simple-english/references/use-cases.md",
            "59bf6702197a5aadc96d197ea17f290d8d50dcd3",
        ]
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

        self.assertEqual(text.count("```") % 2, 0)
        positive_claims = [
            r"\bis ASD-STE100 compliant\b",
            r"\bis ASD-STE100 certified\b",
            r"\bcertifies ASD-STE100 compliance\b",
            r"\bproves ASD-STE100 compliance\b",
        ]
        for pattern in positive_claims:
            with self.subTest(pattern=pattern):
                self.assertIsNone(re.search(pattern, text, re.IGNORECASE))

    def test_rewrites_do_not_add_known_unsupported_claims(self):
        text = REFERENCE.read_text()
        forbidden = {
            "## User-facing CLI errors": ["password caused", "will connect"],
            "## Incident reports and postmortems": [
                "deployment caused",
                "All failed requests",
            ],
            "## Patch and test summaries": [
                "All tests passed",
                "race detector passed",
                "backward compatible",
            ],
            "## Destructive operations and security warnings": [
                "snapshot was created",
                "confirm that snapshot",
                "token was revoked",
            ],
        }
        for heading, claims in forbidden.items():
            rewrite = fenced_example(section_for(text, heading), "Safe rewrite")
            for claim in claims:
                with self.subTest(heading=heading, claim=claim):
                    self.assertNotIn(claim.casefold(), rewrite.casefold())


if __name__ == "__main__":
    unittest.main()
