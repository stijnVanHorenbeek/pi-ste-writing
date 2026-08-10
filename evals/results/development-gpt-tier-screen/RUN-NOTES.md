# GPT tier development screen notes

## Scope

Development-only guarded comparison on three previously used schema-v3 regression scenarios. This evidence is directional, not held-out, reliability, release, or blind semantic-review evidence. It did not use or modify the paused final held-out candidate.

Frozen source commit: `875e29b8fecf9e7df015c0a154cb55b8eaca5e7f`.

## Result

All 18 cells completed successfully:

- Objective protected contract: 18/18.
- Applicable procedure contract: 6/6.
- Gated output contract: 18/18.
- Correlated guard integrity: 18/18.
- Exact accepted guarded artifact: 18/18.
- Provider-level attempts: one for every cell.
- Guard submissions: one accepted submission for every cell; no rejected or unchanged drafts.
- Mechanical style warnings: zero.

| Configuration | Cells | Cost sum | Mean duration (ms) | Mean reasoning tokens |
|---|---:|---:|---:|---:|
| `gpt-5.6-sol:high` | 3/3 | 0.096020 | 16266.67 | 264.00 |
| `gpt-5.6-sol:medium` | 3/3 | 0.091305 | 13412.00 | 216.00 |
| `gpt-5.6-sol:low` | 3/3 | 0.081465 | 12173.67 | 101.00 |
| `gpt-5.5:high` | 3/3 | 0.103295 | 16554.67 | 344.67 |
| `gpt-5.4:high` | 3/3 | 0.063878 | 19338.00 | 622.67 |
| `gpt-5.4-mini:high` | 3/3 | 0.015538 | 12821.33 | 358.00 |

Against the `gpt-5.6-sol:high` control, `gpt-5.6-sol:low` used 15.2% less reported cost and completed 25.2% faster on mean. `gpt-5.4-mini:high` used 83.8% less reported cost and completed 21.2% faster on mean. `gpt-5.4:high` cost less but was 18.9% slower and generated substantially more output and reasoning tokens.

## Interpretation limits

Each configuration has only three observations and one observation per scenario. Perfect deterministic results therefore show compatibility with these known cases, not comparative reliability or open semantic equivalence. No blind judge ran. A reliability follow-up should preregister repeated known development cases before drawing a default-model recommendation.
