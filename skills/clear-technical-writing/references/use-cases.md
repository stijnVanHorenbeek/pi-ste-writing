# Coding-focused use cases

Use these examples only for human-facing technical prose. Before rewriting, build the
semantic ledger from `semantic-preservation.md`. Preserve protected values by occurrence
count, container, and semantic role. Use `checklist.md` before delivery.

Each safe rewrite below uses only the supplied source facts. It preserves uncertainty,
recommendations, requirements, negation, scope, technical names, and exact values. Do
not use an example as evidence for a fact in another task.

## READMEs and API guides

**Mode:** Clear. Use procedure mode only for instructional passages. Preserve API names,
field names, compatibility limits, defaults, and unsupported platforms.

**Source text**

```text
The Acme SDK supports Python 3.12 on Linux. It does not support Windows. `acme.Client` sends requests to `/v1/jobs`. `timeout_ms` is optional. Its default is 5000.
```

**Safe rewrite**

```text
Acme SDK supports Python 3.12 on Linux. It does not support Windows. The `acme.Client` sends requests to `/v1/jobs`. The `timeout_ms` is optional. The default is 5000.
```

**Preservation check:** Support did not expand to Windows. API and field names remain
exact. Optional status and default value remain attached to `timeout_ms`.

For README installation blocks, keep commands unchanged and edit only surrounding prose.
For API guides, keep request fields, response fields, endpoint paths, status codes, and
version boundaries distinct.

## Setup procedures and runbooks

**Mode:** Procedure. Put approvals, warnings, and action-controlling conditions before
the command that they control. Use one action per numbered step unless actions must
occur together.

**Source text**

```text
1. Install `acme-cli==3.8.2`.
2. You must obtain approval for `CHG-913` before the migration.
3. If `acme check` succeeds, run `acme migrate --database orders`.

The migration can take up to 15 minutes. Do not run two migrations at the same time.
```

**Safe rewrite**

```text
1. Install `acme-cli==3.8.2`.
2. You must obtain approval for `CHG-913` before the migration.

WARNING: Do not run two migrations at the same time. The migration can take up to 15 minutes.

3. If `acme check` succeeds, run `acme migrate --database orders`.
```

**Preservation check:** Approval remains mandatory. The successful check remains the
condition for migration. The duration remains an upper bound, not an estimate or
guarantee. The concurrency prohibition appears before the migration command.

Do not invent package sources, privilege requirements, rollback steps, expected output,
or successful verification. If a required operational fact is absent, ask or label it
unknown.

## User-facing CLI errors

**Mode:** Clear for status and known cause; procedure for remediation. Do not rewrite raw
quoted diagnostics. Rewrite only user-facing copy that the task identifies as editable.

**Source text**

```text
Connection to `db-prod` failed at 12:30 UTC. The cause is unknown. The password for user `app` may have expired. If the password expired, set `DB_PASSWORD`. Then run `acmectl connect db-prod` again.
```

**Safe rewrite**

```text
Connection to `db-prod` failed at 12:30 UTC. The cause remains unknown. The password for user `app` may have expired.

If the password expired:
- Set `DB_PASSWORD`.
- Run `acmectl connect db-prod` again.
```

**Preservation check:** Password expiry remains a possibility, not the confirmed cause.
The rewrite does not promise that retrying will connect. User, environment variable,
target, command, and time remain exact.

State a cause only when the source establishes it. Do not convert an error code, log
sequence, or plausible debugging hypothesis into a confirmed explanation.

## Incident reports and postmortems

**Mode:** Clear. Keep observations, timeline facts, contributing factors, ruled-out
causes, and unknown causes separate.

**Source text**

```text
Between 14:02 and 14:31 UTC, 12% of requests failed. The deployment started at 14:00 UTC. The evidence shows timing correlation only, and the root cause is unknown. Cache misses contributed to 73% of the failed requests. No evidence shows data loss.
```

**Safe rewrite**

```text
Between 14:02 and 14:31 UTC, 12% of requests failed. The deployment started at 14:00 UTC, but the evidence shows timing correlation only. The root cause remains unknown. Cache misses contributed to 73% of the failed requests. No evidence shows data loss.
```

**Preservation check:** Timing did not become causation. The known contributing factor
still covers 73%, not all failures. Unknown cause and no-evidence statement retain their
different meanings.

Prefer dated events and attributed evidence over vague chronology. Do not infer impact,
recovery, ownership, or root cause from missing data.

## Release notes and changelogs

**Mode:** Clear. Use one entry per change when useful. Preserve compatibility scope,
deprecation dates, migration recommendations, and changed defaults.

**Source text**

```text
Version `v3.8.2` changes the default `retry_count` from 3 to 5 for new profiles only. Existing profiles are unchanged. The `/v1/jobs` endpoint is deprecated but remains available until 2027-01-15. Users should migrate to `/v2/jobs` before that date.
```

**Safe rewrite**

```text
- In `v3.8.2`, the default `retry_count` changes from 3 to 5 for new profiles only. Existing profiles are unchanged.
- The `/v1/jobs` endpoint is deprecated but remains available until 2027-01-15. Users should migrate to `/v2/jobs` before that date.
```

**Preservation check:** New-profile scope did not expand to existing profiles. Deprecated
did not become removed. The migration remains a recommendation with a stated date, not
an immediate requirement.

Do not label a change breaking, compatible, fixed, or secure unless source evidence
supports that label.

## Patch and test summaries

**Mode:** Clear after explicit writing request. Patch summaries and test-result
interpretation are excluded from automatic activation. Exact invocation can request a
writing pass after technical analysis is complete.

**Source text**

```text
The patch changes `ParseConfig` to reject duplicate `timeout` keys. CLI output is unchanged. `go test ./...` passed 87 tests. The race detector was not run. The reviewer should inspect compatibility with users that depend on duplicate keys.
```

**Safe rewrite**

```text
- The patch changes `ParseConfig` to reject duplicate `timeout` keys.
- CLI output is unchanged.
- `go test ./...` passed 87 tests. The race detector was not run.
- The reviewer should inspect compatibility with users that depend on duplicate keys.
```

**Preservation check:** The rewrite reports only the observed test command and count. It
does not claim full-suite, race, compatibility, or review success. The compatibility
check remains a recommendation.

Do not alter code-review severity, debugging confidence, test interpretation, or patch
scope to satisfy prose rules. First establish technical findings; then rewrite only the
requested human-facing summary.

## Destructive operations and security warnings

**Mode:** Procedure. Safety information and risk level override brevity and output-style
preferences. Put warnings, mandatory approval, and recovery prerequisites before a
destructive command.

**Source text**

```text
1. Change request `CHG-4821` must be approved before deletion.
2. Run `kubectl delete namespace payments`.
3. Then check status with `kubectl get namespace payments`.

Snapshot `snap-2026-07-14` must be complete before deletion. Deletion is permanent. Recovery requires `snap-2026-07-14`.

Token `token-id-7F3` was exposed in a log. It must be revoked before deployment. Deleting the log does not revoke the token.

1. Revoke the token before deployment.
2. After revocation, rotate `PAYMENTS_API_KEY`.
```

**Safe rewrite**

```text
WARNING: Snapshot `snap-2026-07-14` must be complete before deletion. Deletion is permanent. Recovery requires `snap-2026-07-14`.

1. Change request `CHG-4821` must be approved before deletion.
2. Run `kubectl delete namespace payments`.
3. Check status with `kubectl get namespace payments`.

SECURITY WARNING: Token `token-id-7F3` was exposed in a log and must be revoked before deployment. Deleting the log does not revoke the token.

1. Revoke the token before deployment.
2. After revocation, rotate `PAYMENTS_API_KEY`.
```

**Preservation check:** Approval and snapshot completion remain mandatory before
deletion. Permanent loss, recovery dependency, deletion command, and verification
command remain exact and ordered. Exposure is not described as exploitation. Revocation
is not reported as complete. Log deletion does not become remediation.

Never invent approval, backup completion, revocation, rotation, recovery, validation, or
successful execution. Ask before continuing when missing safety information affects an
irreversible action.

## Translation preparation

**Mode:** Clear by default; strict only after explicit request. Improve complete grammar
and stable terminology without replacing protected UI labels, fields, or placeholders.

**Source text**

```text
The `Settings` screen shows `retry_delay`. The default retry delay is 5 seconds. A timeout may occur after 30 seconds. Translators must not translate `retry_delay`. The translation output must keep `%d` exactly.
```

**Safe rewrite**

```text
The `Settings` screen shows `retry_delay`. The default retry delay is 5 seconds. A timeout may occur after 30 seconds. Translators must not translate `retry_delay`. The translation output must keep `%d` exactly.
```

**Preservation check:** UI label, field occurrences, values, placeholder, possibility,
and both translation requirements remain unchanged. An unchanged source is the safe
result when rewriting cannot improve clarity without semantic or formatting risk.

Do not promise lower translation cost or error rates without task-specific evidence.
Strict vocabulary verification remains incomplete without the official Issue 9
dictionary.

## Scope boundaries

Use automatic activation only for requests to create, rewrite, or audit human-facing
technical prose in included targets.

| Context | Default routing | Safe handling |
|---|---|---|
| Documentation or README | Activate | Select clear or procedure mode by passage. |
| API guide | Activate | Use clear mode except for instructional passages. |
| Setup procedure or runbook | Activate | Use procedure mode and preserve operational order. |
| Destructive operation or security warning | Do not auto-activate | Use procedure mode when part of an included setup procedure or runbook; otherwise require exact invocation. |
| User-facing error message or CLI help | Activate | Preserve raw diagnostics; rewrite only editable copy. |
| Incident report, postmortem, release note, changelog | Activate | Preserve evidence, causality, scope, dates, and modality. |
| Translation-ready technical prose | Activate | Use clear mode unless strict review is explicit. |
| Code review finding | Do not auto-activate | Preserve severity and technical judgment; use exact invocation for a later writing pass. |
| Debugging hypothesis | Do not auto-activate | Preserve uncertainty; investigate before rewriting conclusions. |
| Architecture analysis or design tradeoff | Do not auto-activate | Preserve alternatives, constraints, and tradeoffs; do not simplify away nuance. |
| Test-result interpretation | Do not auto-activate | Establish what ran and what passed before editing a report. |
| Patch or test summary | Do not auto-activate | Activate only when the user asks for a writing pass. |
| Raw tool output, log, or quoted diagnostic | Do not auto-activate | Keep raw content exact. A targeted transformation produces derived text; derived text is not raw output. |
| JSON, XML, YAML, CSV, or schema-constrained output | Do not auto-activate | Honor the exact output contract. Change only explicitly targeted fields or structure when the request permits. |
| Source code or generated code | Do not auto-activate | Apply language and repository rules; this writing skill does not govern code edits. |
| Marketing, editorial, or brand writing | Do not auto-activate | Preserve intended voice; this skill is not a persuasion or brand-style tool. |

Explicit Pi invocation can override an activation exclusion when the transformation is
safe:

```text
/skill:clear-technical-writing Rewrite this patch summary in clear mode. Preserve finding severity, uncertainty, commands, test counts, and untested areas.
```

Exact invocation does not by itself permit semantic drift, unsafe reordering, changes
to protected content, or violation of a machine-readable output contract. Preserve
protected content unless the user explicitly requests a targeted safe change. Keep raw
or machine-readable content exact when the deliverable must retain that role.

For reviews, debugging, and architecture work, complete technical reasoning first. Apply
the skill only to the requested prose deliverable.

Strict STE mode activates only after an explicit request for STE, ASD-STE100, or a
compliance-oriented audit.

This package provides writing guidance, not certification. It cannot certify ASD-STE100 compliance.

## Provenance

This reference adapts the use-case organization in
[`AminBlg/SimpleEnglish`](https://github.com/AminBlg/SimpleEnglish), file
`skills/simple-english/references/use-cases.md`, at commit
`59bf6702197a5aadc96d197ea17f290d8d50dcd3`. Coding-agent cases, semantic ledgers,
activation boundaries, safe examples, and Pi invocation guidance are local adaptations.
Adapted portions are licensed under the repository MIT `LICENSE`.
