# Pi benchmark results

**COMPLETE: 18/18 cells successful.**

## Provenance

- Matrix: `development-hardening-reliability` version 1
- Matrix SHA-256: `288710e5ebac9b992408464bc7c2fc998f08adda8ebf4aad58479be74b9400bc`
- Package commit: `0c369f25053a4890ade4a8e8d236b845472e5170`
- Package dirty: `false`
- Skill SHA-256: `5f5ac56c60572bec6f68d33601af0533303518759f0149dd9d82b6224c2d7e5a`
- Extension SHA-256: `68fc423974251e228463b3e28d8385e2fdd6f936dbeac3068ceb9e6b5030defa`
- Pi version: `0.84.1`
- Runner version: `11`

## Applicable cell denominators

| Model | Scenario | Condition | Successful/expected |
|---|---|---|---:|
| `openai-codex/gpt-5.6-sol:high` | `hyperion-refuel-sequence` | guarded | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `nexus-protocol-state` | native-skill | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `hyperion-refuel-sequence` | guarded | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `nexus-protocol-state` | native-skill | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `hyperion-refuel-sequence` | guarded | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `nexus-protocol-state` | native-skill | 3/3 |

## Mechanical verifier integrity

**Guard integrity: ACCEPTED.**
Exact accepted guarded outputs: 9/9.

## Semantic results

**Condition integrity: ACCEPTED.**
Model identity matches: 18/18.
Routing safety passes: 18/18.
Native skill loads: 8/9.
Activation groups passing threshold: 0/0.

**Objective acceptance: ACCEPTED.**
**Applicable procedure acceptance: ACCEPTED.**
**Output-contract acceptance: ACCEPTED.**

| Model | Condition | Runs | Gate pass/fail | Procedure pass/fail | Output-contract pass/fail |
|---|---|---:|---:|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | 0 | 0/0 | 0/0 | 0/0 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | 3 | 3/0 | 0/0 | 3/0 |
| `openai-codex/gpt-5.6-sol:high` | guarded | 3 | 3/0 | 3/0 | 3/0 |
| `github-copilot/claude-sonnet-5:low` | baseline | 0 | 0/0 | 0/0 | 0/0 |
| `github-copilot/claude-sonnet-5:low` | native-skill | 3 | 3/0 | 0/0 | 3/0 |
| `github-copilot/claude-sonnet-5:low` | guarded | 3 | 3/0 | 3/0 | 3/0 |
| `github-copilot/gemini-3.6-flash:medium` | baseline | 0 | 0/0 | 0/0 | 0/0 |
| `github-copilot/gemini-3.6-flash:medium` | native-skill | 3 | 3/0 | 0/0 | 3/0 |
| `github-copilot/gemini-3.6-flash:medium` | guarded | 3 | 3/0 | 3/0 | 3/0 |

## Style results

Style findings are advisory and cannot override semantic failures.

| Model | Condition | Runs | Mechanical warnings |
|---|---|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | 0 | 0 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | 3 | 0 |
| `openai-codex/gpt-5.6-sol:high` | guarded | 3 | 0 |
| `github-copilot/claude-sonnet-5:low` | baseline | 0 | 0 |
| `github-copilot/claude-sonnet-5:low` | native-skill | 3 | 0 |
| `github-copilot/claude-sonnet-5:low` | guarded | 3 | 0 |
| `github-copilot/gemini-3.6-flash:medium` | baseline | 0 | 0 |
| `github-copilot/gemini-3.6-flash:medium` | native-skill | 3 | 0 |
| `github-copilot/gemini-3.6-flash:medium` | guarded | 3 | 0 |

## Usage, cost, and duration

Means and population standard deviations use available successful samples only.

| Model | Condition | Input mean±sd | Output mean±sd | Reasoning mean±sd | Cost sum | Duration mean±sd (ms) |
|---|---|---:|---:|---:|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `openai-codex/gpt-5.6-sol:high` | native-skill | 6274±3.74 | 486±42.20 | 193.67±45.84 | 0.137850 | 19728.33±1075.28 |
| `openai-codex/gpt-5.6-sol:high` | guarded | 3628±4.55 | 689.67±59.17 | 441±56.68 | 0.116490 | 17744.67±1254.76 |
| `github-copilot/claude-sonnet-5:low` | baseline | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `github-copilot/claude-sonnet-5:low` | native-skill | 4±1.63 | 424±100.04 | 33.33±6.60 | 0.042772 | 7263.33±2530.37 |
| `github-copilot/claude-sonnet-5:low` | guarded | 4±1.63 | 868.33±396.42 | 95±73.82 | 0.083168 | 10961±4500.14 |
| `github-copilot/gemini-3.6-flash:medium` | baseline | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `github-copilot/gemini-3.6-flash:medium` | native-skill | 6609±1.41 | 311±2.45 | 0±0.00 | 0.036738 | 15399.67±273.08 |
| `github-copilot/gemini-3.6-flash:medium` | guarded | 3869±3.74 | 225.67±1.89 | 0±0.00 | 0.022488 | 27139.33±7488.51 |

## Unresolved cells

Completed non-stop outputs retained as failure evidence: 1.

None.

## Reproduce

```bash
python3 evals/run_pi_bench.py \
  --matrix evals/development-hardening-reliability-matrix.json \
  --results-dir evals/results/development-hardening-reliability
```

Existing matching successful raw cells are skipped. Failed cells retain attempt history and are retried.

## Limits

- Deterministic fixture checks cover enumerated properties only; open prose still needs attested semantic review.
- Provider reasoning metadata can be unavailable. Missing values remain `null` in raw and aggregate JSON.
- Hidden reasoning content is not stored.
- This benchmark is advisory and does not certify ASD-STE100 compliance.
