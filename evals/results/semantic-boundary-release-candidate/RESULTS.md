# Pi benchmark results

**INCOMPLETE: 151/153 cells successful.**

## Provenance

- Matrix: `semantic-boundary-release-candidate` version 1
- Matrix SHA-256: `98d36a80267e64f6bd271dd1ca805d53344f00fb24044068896da128c88fdcb7`
- Package commit: `bbffefd4b8e843e7057195ccc4e39df418b3fe79`
- Package dirty: `false`
- Skill SHA-256: `908f5c9aff34a7f34a771e1db0a2e2e421f53ec93b3f8af45926336e48b431fc`
- Extension SHA-256: `a36a7cd3b97555717f81a4016d2add6f627b2a550ce436e3d308ec54c801062c`
- Pi version: `0.84.1`
- Runner version: `9`

## Applicable cell denominators

| Model | Scenario | Condition | Successful/expected |
|---|---|---|---:|
| `openai-codex/gpt-5.6-sol:high` | `phoenix-telemetry-diagnostics` | baseline | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `phoenix-telemetry-diagnostics` | native-skill | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `phoenix-telemetry-diagnostics` | guarded | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `meridian-device-calibration` | baseline | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `meridian-device-calibration` | native-skill | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `meridian-device-calibration` | guarded | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `hyperion-refuel-sequence` | baseline | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `hyperion-refuel-sequence` | native-skill | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `hyperion-refuel-sequence` | guarded | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `nexus-protocol-state` | baseline | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `nexus-protocol-state` | native-skill | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `nexus-protocol-state` | guarded | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `quartz-sensor-correlation` | baseline | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `quartz-sensor-correlation` | native-skill | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `quartz-sensor-correlation` | guarded | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `atlas-inventory-structured` | baseline | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `atlas-inventory-structured` | native-skill | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `phoenix-telemetry-diagnostics` | baseline | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `phoenix-telemetry-diagnostics` | native-skill | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `phoenix-telemetry-diagnostics` | guarded | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `meridian-device-calibration` | baseline | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `meridian-device-calibration` | native-skill | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `meridian-device-calibration` | guarded | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `hyperion-refuel-sequence` | baseline | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `hyperion-refuel-sequence` | native-skill | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `hyperion-refuel-sequence` | guarded | 2/3 |
| `github-copilot/claude-sonnet-5:low` | `nexus-protocol-state` | baseline | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `nexus-protocol-state` | native-skill | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `nexus-protocol-state` | guarded | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `quartz-sensor-correlation` | baseline | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `quartz-sensor-correlation` | native-skill | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `quartz-sensor-correlation` | guarded | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `atlas-inventory-structured` | baseline | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `atlas-inventory-structured` | native-skill | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `phoenix-telemetry-diagnostics` | baseline | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `phoenix-telemetry-diagnostics` | native-skill | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `phoenix-telemetry-diagnostics` | guarded | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `meridian-device-calibration` | baseline | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `meridian-device-calibration` | native-skill | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `meridian-device-calibration` | guarded | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `hyperion-refuel-sequence` | baseline | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `hyperion-refuel-sequence` | native-skill | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `hyperion-refuel-sequence` | guarded | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `nexus-protocol-state` | baseline | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `nexus-protocol-state` | native-skill | 2/3 |
| `github-copilot/gemini-3.6-flash:medium` | `nexus-protocol-state` | guarded | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `quartz-sensor-correlation` | baseline | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `quartz-sensor-correlation` | native-skill | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `quartz-sensor-correlation` | guarded | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `atlas-inventory-structured` | baseline | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `atlas-inventory-structured` | native-skill | 3/3 |

## Mechanical verifier integrity

**Guard integrity: NOT ACCEPTED.**
Exact accepted guarded outputs: 44/45.

## Semantic results

**Condition integrity: NOT ACCEPTED.**
Model identity matches: 151/153.
Routing safety passes: 151/153.
Native skill loads: 44/45.
Activation groups passing threshold: 17/18.

**Objective acceptance: NOT ACCEPTED.**
**Applicable procedure acceptance: NOT ACCEPTED.**
**Output-contract acceptance: NOT ACCEPTED.**

| Model | Condition | Runs | Gate pass/fail | Procedure pass/fail | Output-contract pass/fail |
|---|---|---:|---:|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | 18 | 17/1 | 2/1 | 18/0 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | 18 | 18/0 | 3/0 | 18/0 |
| `openai-codex/gpt-5.6-sol:high` | guarded | 15 | 15/0 | 3/0 | 15/0 |
| `github-copilot/claude-sonnet-5:low` | baseline | 18 | 16/2 | 3/0 | 15/3 |
| `github-copilot/claude-sonnet-5:low` | native-skill | 18 | 18/0 | 3/0 | 15/3 |
| `github-copilot/claude-sonnet-5:low` | guarded | 14 | 14/0 | 2/0 | 14/0 |
| `github-copilot/gemini-3.6-flash:medium` | baseline | 18 | 18/0 | 3/0 | 15/3 |
| `github-copilot/gemini-3.6-flash:medium` | native-skill | 17 | 17/0 | 3/0 | 14/3 |
| `github-copilot/gemini-3.6-flash:medium` | guarded | 15 | 15/0 | 3/0 | 15/0 |

## Style results

Style findings are advisory and cannot override semantic failures.

| Model | Condition | Runs | Mechanical warnings |
|---|---|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | 18 | 0 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | 18 | 0 |
| `openai-codex/gpt-5.6-sol:high` | guarded | 15 | 0 |
| `github-copilot/claude-sonnet-5:low` | baseline | 18 | 0 |
| `github-copilot/claude-sonnet-5:low` | native-skill | 18 | 0 |
| `github-copilot/claude-sonnet-5:low` | guarded | 14 | 0 |
| `github-copilot/gemini-3.6-flash:medium` | baseline | 18 | 0 |
| `github-copilot/gemini-3.6-flash:medium` | native-skill | 17 | 0 |
| `github-copilot/gemini-3.6-flash:medium` | guarded | 15 | 0 |

## Usage, cost, and duration

Means and population standard deviations use available successful samples only.

| Model | Condition | Input mean±sd | Output mean±sd | Reasoning mean±sd | Cost sum | Duration mean±sd (ms) |
|---|---|---:|---:|---:|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | 201.83±37.59 | 236.44±270.83 | 127.78±272.30 | 0.145845 | 11180.78±7767.08 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | 6593.06±3350.32 | 547.39±401.45 | 295.61±298.41 | 0.888965 | 20464.72±9612.16 |
| `openai-codex/gpt-5.6-sol:high` | guarded | 3586.07±34.87 | 349±133.36 | 176.60±103.38 | 0.426005 | 13841.53±4343.97 |
| `github-copilot/claude-sonnet-5:low` | baseline | 317.83±62.83 | 180.50±93.62 | 0±0.00 | 0.043932 | 3618.94±862.91 |
| `github-copilot/claude-sonnet-5:low` | native-skill | 4.89±1.52 | 453.83±274.56 | 78.56±160.37 | 0.353996 | 9195.06±3612.10 |
| `github-copilot/claude-sonnet-5:low` | guarded | 2.29±0.70 | 336.57±92.47 | 0±0.00 | 0.277326 | 4842.57±1147.16 |
| `github-copilot/gemini-3.6-flash:medium` | baseline | 207.83±34.16 | 119.06±71.05 | 0±0.00 | 0.021684 | 6942.78±2705.11 |
| `github-copilot/gemini-3.6-flash:medium` | native-skill | 5275.18±3296.58 | 223.18±97.83 | 0±0.00 | 0.163573 | 13398±6721.94 |
| `github-copilot/gemini-3.6-flash:medium` | guarded | 3830.67±33.92 | 175.80±38.39 | 0±0.00 | 0.105968 | 14281.47±8138.90 |

## Unresolved cells

Completed non-stop outputs retained as failure evidence: 3.

- failed: `github-copilot/claude-sonnet-5:low` guarded hyperion-refuel-sequence repetition 2
- failed: `github-copilot/gemini-3.6-flash:medium` native-skill nexus-protocol-state repetition 3

## Reproduce

```bash
python3 evals/run_pi_bench.py \
  --matrix evals/semantic-boundary-release-candidate-matrix.json \
  --results-dir evals/results/semantic-boundary-release-candidate
```

Existing matching successful raw cells are skipped. Failed cells retain attempt history and are retried.

## Limits

- Deterministic fixture checks cover enumerated properties only; open prose still needs attested semantic review.
- Provider reasoning metadata can be unavailable. Missing values remain `null` in raw and aggregate JSON.
- Hidden reasoning content is not stored.
- This benchmark is advisory and does not certify ASD-STE100 compliance.
