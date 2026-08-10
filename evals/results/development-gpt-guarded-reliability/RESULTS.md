# Pi benchmark results

**COMPLETE: 45/45 cells successful.**

## Provenance

- Matrix: `development-gpt-guarded-reliability` version 1
- Matrix SHA-256: `fe5857fb6033d97fb8627a849775e54053dcd17ba5e1295eace63f7749c0b2f1`
- Package commit: `e32b6f18d52935d67e2fcf9dcdc596133e3c499b`
- Package dirty: `false`
- Skill SHA-256: `5f5ac56c60572bec6f68d33601af0533303518759f0149dd9d82b6224c2d7e5a`
- Extension SHA-256: `68fc423974251e228463b3e28d8385e2fdd6f936dbeac3068ceb9e6b5030defa`
- Pi version: `0.84.1`
- Runner version: `12`

## Applicable cell denominators

| Model | Scenario | Condition | Successful/expected |
|---|---|---|---:|
| `openai-codex/gpt-5.6-sol:high` | `phoenix-telemetry-diagnostics` | guarded | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `meridian-device-calibration` | guarded | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `hyperion-refuel-sequence` | guarded | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `nexus-protocol-state` | guarded | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `quartz-sensor-correlation` | guarded | 3/3 |
| `openai-codex/gpt-5.6-sol:low` | `phoenix-telemetry-diagnostics` | guarded | 3/3 |
| `openai-codex/gpt-5.6-sol:low` | `meridian-device-calibration` | guarded | 3/3 |
| `openai-codex/gpt-5.6-sol:low` | `hyperion-refuel-sequence` | guarded | 3/3 |
| `openai-codex/gpt-5.6-sol:low` | `nexus-protocol-state` | guarded | 3/3 |
| `openai-codex/gpt-5.6-sol:low` | `quartz-sensor-correlation` | guarded | 3/3 |
| `openai-codex/gpt-5.4-mini:high` | `phoenix-telemetry-diagnostics` | guarded | 3/3 |
| `openai-codex/gpt-5.4-mini:high` | `meridian-device-calibration` | guarded | 3/3 |
| `openai-codex/gpt-5.4-mini:high` | `hyperion-refuel-sequence` | guarded | 3/3 |
| `openai-codex/gpt-5.4-mini:high` | `nexus-protocol-state` | guarded | 3/3 |
| `openai-codex/gpt-5.4-mini:high` | `quartz-sensor-correlation` | guarded | 3/3 |

## Mechanical verifier integrity

**Guard integrity: ACCEPTED.**
Exact accepted guarded outputs: 45/45.

## Semantic results

**Condition integrity: ACCEPTED.**
Model identity matches: 45/45.
Routing safety passes: 45/45.
Native skill loads: 0/0.
Activation groups passing threshold: 0/0.

**Objective acceptance: ACCEPTED.**
**Applicable procedure acceptance: ACCEPTED.**
**Output-contract acceptance: ACCEPTED.**

| Model | Condition | Runs | Gate pass/fail | Procedure pass/fail | Output-contract pass/fail |
|---|---|---:|---:|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | 0 | 0/0 | 0/0 | 0/0 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | 0 | 0/0 | 0/0 | 0/0 |
| `openai-codex/gpt-5.6-sol:high` | guarded | 15 | 15/0 | 3/0 | 15/0 |
| `openai-codex/gpt-5.6-sol:low` | baseline | 0 | 0/0 | 0/0 | 0/0 |
| `openai-codex/gpt-5.6-sol:low` | native-skill | 0 | 0/0 | 0/0 | 0/0 |
| `openai-codex/gpt-5.6-sol:low` | guarded | 15 | 15/0 | 3/0 | 15/0 |
| `openai-codex/gpt-5.4-mini:high` | baseline | 0 | 0/0 | 0/0 | 0/0 |
| `openai-codex/gpt-5.4-mini:high` | native-skill | 0 | 0/0 | 0/0 | 0/0 |
| `openai-codex/gpt-5.4-mini:high` | guarded | 15 | 15/0 | 3/0 | 15/0 |

## Style results

Style findings are advisory and cannot override semantic failures.

| Model | Condition | Runs | Mechanical warnings |
|---|---|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | 0 | 0 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | 0 | 0 |
| `openai-codex/gpt-5.6-sol:high` | guarded | 15 | 0 |
| `openai-codex/gpt-5.6-sol:low` | baseline | 0 | 0 |
| `openai-codex/gpt-5.6-sol:low` | native-skill | 0 | 0 |
| `openai-codex/gpt-5.6-sol:low` | guarded | 15 | 0 |
| `openai-codex/gpt-5.4-mini:high` | baseline | 0 | 0 |
| `openai-codex/gpt-5.4-mini:high` | native-skill | 0 | 0 |
| `openai-codex/gpt-5.4-mini:high` | guarded | 15 | 0 |

## Usage, cost, and duration

Means and population standard deviations use available successful samples only.

| Model | Condition | Input mean±sd | Output mean±sd | Reasoning mean±sd | Cost sum | Duration mean±sd (ms) |
|---|---|---:|---:|---:|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `openai-codex/gpt-5.6-sol:high` | native-skill | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `openai-codex/gpt-5.6-sol:high` | guarded | 3736.20±584.12 | 434±211.92 | 248.93±160.80 | 0.476795 | 15575±7717.99 |
| `openai-codex/gpt-5.6-sol:low` | baseline | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `openai-codex/gpt-5.6-sol:low` | native-skill | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `openai-codex/gpt-5.6-sol:low` | guarded | 3585.07±36.86 | 219.60±80.63 | 47.47±49.37 | 0.367700 | 9777.53±1730.52 |
| `openai-codex/gpt-5.4-mini:high` | baseline | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `openai-codex/gpt-5.4-mini:high` | native-skill | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `openai-codex/gpt-5.4-mini:high` | guarded | 3618±129.49 | 918.67±746.08 | 739.40±711.26 | 0.103020 | 18606.13±10227.46 |

## Unresolved cells

None.

## Reproduce

```bash
python3 evals/run_pi_bench.py \
  --matrix evals/development-gpt-guarded-reliability-matrix.json \
  --results-dir evals/results/development-gpt-guarded-reliability
```

Existing matching successful raw cells are skipped. Failed cells retain attempt history and are retried.

## Limits

- Deterministic fixture checks cover enumerated properties only; open prose still needs attested semantic review.
- Provider reasoning metadata can be unavailable. Missing values remain `null` in raw and aggregate JSON.
- Hidden reasoning content is not stored.
- This benchmark is advisory and does not certify ASD-STE100 compliance.
