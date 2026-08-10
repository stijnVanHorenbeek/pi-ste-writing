# Post-adjudication development notes

Status: **routing improved; semantic release gate still fails**

These diagnostics use the failed independent-review scenarios as development evidence. They do not retroactively amend the preregistered result and are not new release evidence.

## Blinded adjudication

Eighteen native-skill deterministic failures where the skill loaded received blinded cross-provider review. Two package-contract disputes received separate arbitration.

- Genuine release-blocking failures: 6.
- Evaluator false positives: 12.
- Ambiguous: 0.

Genuine classes: two inline-to-fenced command moves, three protected occurrence-count changes, and one omitted unknown-root-cause fact. See `independent-review/adjudication/summary.json`.

## Routing probes

First frontmatter revision failed:

- Claude incident-correlation positive: 1/3 loads; threshold failed.
- Claude root-cause positive: 2/3 loads; passed.
- Claude quoted-diagnostic negative: 0/3 loads; passed.
- Gemini quoted-diagnostic negative: 3/3 loads; failed.

Second revision made incident rewriting the first explicit trigger and separated error explanations from quoted diagnostics:

- Claude incident-correlation positive: 3/3 loads.
- Claude root-cause positive: 3/3 loads.
- Claude quoted-diagnostic negative: 0/3 loads.
- Gemini quoted-diagnostic negative: 0/3 loads.

All four routing groups passed their declared thresholds at commit `13a49ee`.

## Semantic development probes

At commit `13a49ee`:

- Vesper protected-count scenario: 3/3 semantic passes.
- Broker correlation/unknown-cause scenario: 0/3 deterministic passes before adjudicated safe paraphrases were added; activation passed 2/3.
- Ledger destructive procedure: 1/3 semantic passes. Two failures moved an inline verification command to a fenced block.

After scorer corrections, all three safe broker outputs pass while the arbitrated omitted-root-cause output remains a failure.

An explicit inline-command example in the progressively loaded semantic reference did not affect Claude because all three probes read only `SKILL.md`; ledger procedure result remained 0/3 at `dfe9be3`.

A final hot-path instruction in `SKILL.md` improved ledger procedure output to 1/3 at `fd1dd8c`. Remaining failures included a duplicated protected bucket identifier in a heading and warning/procedure formatting drift. This still fails the required 3/3 semantic threshold.

## Stop decision

Prompt tuning stopped. Repeated explicit instructions did not make Claude reliably preserve protected occurrence count and inline/fenced containers in procedure rewrites. More tuning against the same scenario would overfit and cannot provide unseen release evidence.

Package should remain experimental or require downstream deterministic validation for protected-content rewrites. It does not meet the current V1 release contract.

## Additional cost

Provider-reported cost for blinded adjudication, arbitration, fix reviews, and targeted probes was approximately `$2.816319`, within the selected `$2–$3` balanced-review budget. Provider metadata is not a billing record.
