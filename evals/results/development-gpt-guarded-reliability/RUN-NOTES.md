# GPT guarded reliability probe notes

## Scope

Development-only guarded comparison on all five previously used schema-v3 semantic-boundary prose scenarios, with three repetitions per model-scenario group. This evidence is known-case regression evidence, not held-out, release, or blind semantic-review evidence. It did not use or modify the paused final held-out candidate.

Frozen source commit: `e32b6f18d52935d67e2fcf9dcdc596133e3c499b`.

## Result

All 45 cells completed successfully:

- Objective protected contract: 45/45.
- Applicable procedure contract: 9/9.
- Gated output contract: 45/45.
- Correlated guard integrity: 45/45.
- Exact accepted guarded artifact: 45/45.
- Provider-level attempts: one for every cell.
- Guard submissions: 43 cells accepted their first submission; two cells produced a corrected second submission that was accepted.
- Unchanged rejected drafts: zero.
- Mechanical style warnings: zero.

| Configuration | Cells | First guard submission | Cost sum | Mean duration (ms) | Mean output tokens | Mean reasoning tokens |
|---|---:|---:|---:|---:|---:|---:|
| `gpt-5.6-sol:high` | 15/15 | 14/15 | 0.476795 | 15575.00 | 434.00 | 248.93 |
| `gpt-5.6-sol:low` | 15/15 | 15/15 | 0.367700 | 9777.53 | 219.60 | 47.47 |
| `gpt-5.4-mini:high` | 15/15 | 14/15 | 0.103020 | 18606.13 | 918.67 | 739.40 |

Against `gpt-5.6-sol:high`, `gpt-5.6-sol:low` used 22.9% less provider-reported cost, completed 37.2% faster on mean, emitted 49.4% fewer output tokens, and used 80.9% fewer reported reasoning tokens. `gpt-5.4-mini:high` used 78.4% less provider-reported cost, but completed 19.5% slower, emitted 111.7% more output tokens, and used 197.0% more reported reasoning tokens.

## Interpretation limits

The probe has 15 observations per configuration across known scenarios. Perfect deterministic results support guarded-path compatibility and repeatability on this regression set. They do not establish open semantic equivalence or justify changing the frozen prospective release cohort. No blind judge ran. Provider cost fields are metadata, not billing records.
