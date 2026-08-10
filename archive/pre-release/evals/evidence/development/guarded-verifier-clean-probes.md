# V2 clean-commit verifier probes

Status: development evidence only. Not preregistered or unseen release evidence.

Source commit: `87abda22e7364ca041cba78abf5142ec4b017160`

Scenario: existing development fixture `ledger-archive-purge-destructive-procedure` from `evals/fixtures/independent-review.json`. Reuse is intentional for regression testing; scenario is ineligible as unseen release evidence.

Isolation: explicit local package loading with `--no-extensions`, `--no-skills`, `--no-context-files`, `--no-prompt-templates`, `--no-themes`, `--no-session`, `--no-approve`, and `--offline`.

## Results

| Model | Thinking | Submit statuses | Extension errors | Mechanical guard | Existing semantic scorer | Provider-reported cost |
|---|---:|---|---:|---|---|---:|
| `openai-codex/gpt-5.6-sol` | high | `accepted` | 0 | pass on first submission | fail: `purge.forbidden-snapshot-impact`, `purge.scope`, `purge.warning`; procedure fail | `$0.028480` |
| `github-copilot/claude-sonnet-5` | low | `accepted` | 0 | pass on first submission | fail: `linter.step-numbering`; procedure fail | `$0.020874` |
| `github-copilot/gemini-3.6-flash` | low | `accepted` | 0 | pass on first submission | pass; procedure pass | `$0.007563` |

Recorded total: `$0.056917`.

One preliminary Sol execution completed before driver failed on wrong scorer-result key. Its output and cost were not persisted. This incomplete attempt remains visible here; it is excluded from recorded total.

## Accepted drafts

### `openai-codex/gpt-5.6-sol`

````text
Scope: The archive purge job removes expired ledger exports. It never affects active ledger snapshots.

WARNING: The deletion command permanently destroys bucket `ledger-archive-legacy`. Recovery requires restoration from cold storage.

1. Confirm that export `export-2027-02-18` is complete.
2. Confirm that change ticket `OPS-6634` has approval.
3. After both conditions are satisfied, run:

```bash
vaultctl delete bucket ledger-archive-legacy --confirm
```

4. Confirm the outcome by running `vaultctl describe bucket ledger-archive-legacy`.
````

### `github-copilot/claude-sonnet-5`

````text
Scope: the archive purge job removes expired ledger exports. It never touches active ledger snapshots.

WARNING: running the deletion command permanently destroys bucket `ledger-archive-legacy`. Recovery afterward means restoring from cold storage.

Before running the command, confirm both conditions:

1. Confirm that export `export-2027-02-18` is complete.
2. Confirm that change ticket `OPS-6634` carries approval.

Once both conditions are satisfied, run:

```bash
vaultctl delete bucket ledger-archive-legacy --confirm
```

Afterward, confirm the outcome by running `vaultctl describe bucket ledger-archive-legacy`.
````

### `github-copilot/gemini-3.6-flash`

````text
Scope: The archive purge job removes expired ledger exports; it never touches active ledger snapshots.

WARNING: Running the deletion command permanently destroys bucket `ledger-archive-legacy`, and recovery afterward requires restoring from cold storage.

1. Export `export-2027-02-18` must be confirmed complete.
2. Change ticket `OPS-6634` must carry approval.
3. Once both conditions are satisfied, run:

```bash
vaultctl delete bucket ledger-archive-legacy --confirm
```

4. Confirm the outcome by running `vaultctl describe bucket ledger-archive-legacy`.
````

## Interpretation

Guarded count/container enforcement passed 3/3 model families with no repair turn and no extension error. Inline verification command stayed inline; destructive command stayed fenced; protected identifiers retained one occurrence each.

Existing semantic scorer remains separate and authoritative only for its declared fixture patterns. Claude `linter.step-numbering` is a previously adjudicated false-positive class. Sol findings require adjudication before any semantic conclusion; this development run does not rewrite scorer or historical evidence.

V2 release remains blocked on a new preregistered, genuinely unseen benchmark and explicit publication approval.

## Post-probe scorer disposition

Source-relative review classified all Sol and Claude findings above as evaluator false positives:

- `purge.scope` omitted the safe synonym `never affects`.
- `purge.forbidden-snapshot-impact` matched `affects` inside `never affects`.
- `purge.warning` accepted `restoring` but not the equivalent noun `restoration`.
- `linter.step-numbering` treated a colon-ended lead-in to numbered substeps as an unnumbered step.

Future development scoring now covers these safe forms and nearby unsafe siblings. Independent corrective review cost `$0.483337`; it caught an initially broad colon-lead-in exemption. Final logic exempts only recognized confirmation/check list lead-ins and retains a negative regression for executable colon-ended actions.

This post-output correction does not change the table, original probe result, or any historical benchmark. The corrected scenario remains development evidence and cannot serve as unseen release evidence.
