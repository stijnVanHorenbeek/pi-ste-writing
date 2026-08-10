# Pi benchmark results

**COMPLETE: 18/18 cells successful.**

## Provenance

- Matrix: `development-gpt-tier-screen` version 1
- Matrix SHA-256: `be2775288fe846efadc3063a9399180bc8ba9d63f9de739bc1b55b87c596eef5`
- Package commit: `875e29b8fecf9e7df015c0a154cb55b8eaca5e7f`
- Package dirty: `false`
- Skill SHA-256: `5f5ac56c60572bec6f68d33601af0533303518759f0149dd9d82b6224c2d7e5a`
- Extension SHA-256: `68fc423974251e228463b3e28d8385e2fdd6f936dbeac3068ceb9e6b5030defa`
- Pi version: `0.84.1`
- Runner version: `12`

## Applicable cell denominators

| Model | Scenario | Condition | Successful/expected |
|---|---|---|---:|
| `openai-codex/gpt-5.6-sol:high` | `phoenix-telemetry-diagnostics` | guarded | 1/1 |
| `openai-codex/gpt-5.6-sol:high` | `hyperion-refuel-sequence` | guarded | 1/1 |
| `openai-codex/gpt-5.6-sol:high` | `nexus-protocol-state` | guarded | 1/1 |
| `openai-codex/gpt-5.6-sol:medium` | `phoenix-telemetry-diagnostics` | guarded | 1/1 |
| `openai-codex/gpt-5.6-sol:medium` | `hyperion-refuel-sequence` | guarded | 1/1 |
| `openai-codex/gpt-5.6-sol:medium` | `nexus-protocol-state` | guarded | 1/1 |
| `openai-codex/gpt-5.6-sol:low` | `phoenix-telemetry-diagnostics` | guarded | 1/1 |
| `openai-codex/gpt-5.6-sol:low` | `hyperion-refuel-sequence` | guarded | 1/1 |
| `openai-codex/gpt-5.6-sol:low` | `nexus-protocol-state` | guarded | 1/1 |
| `openai-codex/gpt-5.5:high` | `phoenix-telemetry-diagnostics` | guarded | 1/1 |
| `openai-codex/gpt-5.5:high` | `hyperion-refuel-sequence` | guarded | 1/1 |
| `openai-codex/gpt-5.5:high` | `nexus-protocol-state` | guarded | 1/1 |
| `openai-codex/gpt-5.4:high` | `phoenix-telemetry-diagnostics` | guarded | 1/1 |
| `openai-codex/gpt-5.4:high` | `hyperion-refuel-sequence` | guarded | 1/1 |
| `openai-codex/gpt-5.4:high` | `nexus-protocol-state` | guarded | 1/1 |
| `openai-codex/gpt-5.4-mini:high` | `phoenix-telemetry-diagnostics` | guarded | 1/1 |
| `openai-codex/gpt-5.4-mini:high` | `hyperion-refuel-sequence` | guarded | 1/1 |
| `openai-codex/gpt-5.4-mini:high` | `nexus-protocol-state` | guarded | 1/1 |

## Mechanical verifier integrity

**Guard integrity: ACCEPTED.**
Exact accepted guarded outputs: 18/18.

## Semantic results

**Condition integrity: ACCEPTED.**
Model identity matches: 18/18.
Routing safety passes: 18/18.
Native skill loads: 0/0.
Activation groups passing threshold: 0/0.

**Objective acceptance: ACCEPTED.**
**Applicable procedure acceptance: ACCEPTED.**
**Output-contract acceptance: ACCEPTED.**

| Model | Condition | Runs | Gate pass/fail | Procedure pass/fail | Output-contract pass/fail |
|---|---|---:|---:|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | 0 | 0/0 | 0/0 | 0/0 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | 0 | 0/0 | 0/0 | 0/0 |
| `openai-codex/gpt-5.6-sol:high` | guarded | 3 | 3/0 | 1/0 | 3/0 |
| `openai-codex/gpt-5.6-sol:medium` | baseline | 0 | 0/0 | 0/0 | 0/0 |
| `openai-codex/gpt-5.6-sol:medium` | native-skill | 0 | 0/0 | 0/0 | 0/0 |
| `openai-codex/gpt-5.6-sol:medium` | guarded | 3 | 3/0 | 1/0 | 3/0 |
| `openai-codex/gpt-5.6-sol:low` | baseline | 0 | 0/0 | 0/0 | 0/0 |
| `openai-codex/gpt-5.6-sol:low` | native-skill | 0 | 0/0 | 0/0 | 0/0 |
| `openai-codex/gpt-5.6-sol:low` | guarded | 3 | 3/0 | 1/0 | 3/0 |
| `openai-codex/gpt-5.5:high` | baseline | 0 | 0/0 | 0/0 | 0/0 |
| `openai-codex/gpt-5.5:high` | native-skill | 0 | 0/0 | 0/0 | 0/0 |
| `openai-codex/gpt-5.5:high` | guarded | 3 | 3/0 | 1/0 | 3/0 |
| `openai-codex/gpt-5.4:high` | baseline | 0 | 0/0 | 0/0 | 0/0 |
| `openai-codex/gpt-5.4:high` | native-skill | 0 | 0/0 | 0/0 | 0/0 |
| `openai-codex/gpt-5.4:high` | guarded | 3 | 3/0 | 1/0 | 3/0 |
| `openai-codex/gpt-5.4-mini:high` | baseline | 0 | 0/0 | 0/0 | 0/0 |
| `openai-codex/gpt-5.4-mini:high` | native-skill | 0 | 0/0 | 0/0 | 0/0 |
| `openai-codex/gpt-5.4-mini:high` | guarded | 3 | 3/0 | 1/0 | 3/0 |

## Style results

Style findings are advisory and cannot override semantic failures.

| Model | Condition | Runs | Mechanical warnings |
|---|---|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | 0 | 0 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | 0 | 0 |
| `openai-codex/gpt-5.6-sol:high` | guarded | 3 | 0 |
| `openai-codex/gpt-5.6-sol:medium` | baseline | 0 | 0 |
| `openai-codex/gpt-5.6-sol:medium` | native-skill | 0 | 0 |
| `openai-codex/gpt-5.6-sol:medium` | guarded | 3 | 0 |
| `openai-codex/gpt-5.6-sol:low` | baseline | 0 | 0 |
| `openai-codex/gpt-5.6-sol:low` | native-skill | 0 | 0 |
| `openai-codex/gpt-5.6-sol:low` | guarded | 3 | 0 |
| `openai-codex/gpt-5.5:high` | baseline | 0 | 0 |
| `openai-codex/gpt-5.5:high` | native-skill | 0 | 0 |
| `openai-codex/gpt-5.5:high` | guarded | 3 | 0 |
| `openai-codex/gpt-5.4:high` | baseline | 0 | 0 |
| `openai-codex/gpt-5.4:high` | native-skill | 0 | 0 |
| `openai-codex/gpt-5.4:high` | guarded | 3 | 0 |
| `openai-codex/gpt-5.4-mini:high` | baseline | 0 | 0 |
| `openai-codex/gpt-5.4-mini:high` | native-skill | 0 | 0 |
| `openai-codex/gpt-5.4-mini:high` | guarded | 3 | 0 |

## Usage, cost, and duration

Means and population standard deviations use available successful samples only.

| Model | Condition | Input mean±sd | Output mean±sd | Reasoning mean±sd | Cost sum | Duration mean±sd (ms) |
|---|---|---:|---:|---:|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `openai-codex/gpt-5.6-sol:high` | native-skill | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `openai-codex/gpt-5.6-sol:high` | guarded | 3609.33±21.45 | 465.33±242.17 | 264±214.34 | 0.096020 | 16266.67±8050.90 |
| `openai-codex/gpt-5.6-sol:medium` | baseline | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `openai-codex/gpt-5.6-sol:medium` | native-skill | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `openai-codex/gpt-5.6-sol:medium` | guarded | 3603±28.99 | 414±130.74 | 216±87.18 | 0.091305 | 13412±2929.07 |
| `openai-codex/gpt-5.6-sol:low` | baseline | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `openai-codex/gpt-5.6-sol:low` | native-skill | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `openai-codex/gpt-5.6-sol:low` | guarded | 3613±29.71 | 303±169.08 | 101±132.37 | 0.081465 | 12173.67±2546.30 |
| `openai-codex/gpt-5.5:high` | baseline | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `openai-codex/gpt-5.5:high` | native-skill | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `openai-codex/gpt-5.5:high` | guarded | 3610.33±24.28 | 546±519.36 | 344.67±487.43 | 0.103295 | 16554.67±7731.86 |
| `openai-codex/gpt-5.4:high` | baseline | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `openai-codex/gpt-5.4:high` | native-skill | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `openai-codex/gpt-5.4:high` | guarded | 3605±28.39 | 818.67±306.32 | 622.67±269.60 | 0.063878 | 19338±5467.43 |
| `openai-codex/gpt-5.4-mini:high` | baseline | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `openai-codex/gpt-5.4-mini:high` | native-skill | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `openai-codex/gpt-5.4-mini:high` | guarded | 3603.67±26.13 | 550.33±160.53 | 358±127.80 | 0.015538 | 12821.33±1634.91 |

## Unresolved cells

None.

## Reproduce

```bash
python3 evals/run_pi_bench.py \
  --matrix evals/development-gpt-tier-screen-matrix.json \
  --results-dir evals/results/development-gpt-tier-screen
```

Existing matching successful raw cells are skipped. Failed cells retain attempt history and are retried.

## Limits

- Deterministic fixture checks cover enumerated properties only; open prose still needs attested semantic review.
- Provider reasoning metadata can be unavailable. Missing values remain `null` in raw and aggregate JSON.
- Hidden reasoning content is not stored.
- This benchmark is advisory and does not certify ASD-STE100 compliance.
