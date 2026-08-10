# Pi benchmark results

**INCOMPLETE: 149/153 cells successful.**

## Provenance

- Matrix: `hybrid-release-candidate` version 2
- Matrix SHA-256: `d41409d978ecde0a60026c0702b1080f4372238411051185f3afb4136844e8cb`
- Package commit: `a3fde8294c88970e56606833c28a6aecf44580a6`
- Package dirty: `false`
- Skill SHA-256: `908f5c9aff34a7f34a771e1db0a2e2e421f53ec93b3f8af45926336e48b431fc`
- Extension SHA-256: `a36a7cd3b97555717f81a4016d2add6f627b2a550ce436e3d308ec54c801062c`
- Pi version: `0.84.1`
- Runner version: `7`

## Applicable cell denominators

| Model | Scenario | Condition | Successful/expected |
|---|---|---|---:|
| `openai-codex/gpt-5.6-sol:high` | `lumina-threshold-causality` | baseline | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `lumina-threshold-causality` | native-skill | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `lumina-threshold-causality` | guarded | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `aethel-actor-capability` | baseline | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `aethel-actor-capability` | native-skill | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `aethel-actor-capability` | guarded | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `valerius-factual-assurance` | baseline | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `valerius-factual-assurance` | native-skill | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `valerius-factual-assurance` | guarded | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `ciphera-repository-terms` | baseline | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `ciphera-repository-terms` | native-skill | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `ciphera-repository-terms` | guarded | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `thalassa-destructive-procedure` | baseline | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `thalassa-destructive-procedure` | native-skill | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `thalassa-destructive-procedure` | guarded | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `kestrel-flight-log-structured` | baseline | 3/3 |
| `openai-codex/gpt-5.6-sol:high` | `kestrel-flight-log-structured` | native-skill | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `lumina-threshold-causality` | baseline | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `lumina-threshold-causality` | native-skill | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `lumina-threshold-causality` | guarded | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `aethel-actor-capability` | baseline | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `aethel-actor-capability` | native-skill | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `aethel-actor-capability` | guarded | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `valerius-factual-assurance` | baseline | 0/3 |
| `github-copilot/claude-sonnet-5:low` | `valerius-factual-assurance` | native-skill | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `valerius-factual-assurance` | guarded | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `ciphera-repository-terms` | baseline | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `ciphera-repository-terms` | native-skill | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `ciphera-repository-terms` | guarded | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `thalassa-destructive-procedure` | baseline | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `thalassa-destructive-procedure` | native-skill | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `thalassa-destructive-procedure` | guarded | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `kestrel-flight-log-structured` | baseline | 3/3 |
| `github-copilot/claude-sonnet-5:low` | `kestrel-flight-log-structured` | native-skill | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `lumina-threshold-causality` | baseline | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `lumina-threshold-causality` | native-skill | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `lumina-threshold-causality` | guarded | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `aethel-actor-capability` | baseline | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `aethel-actor-capability` | native-skill | 2/3 |
| `github-copilot/gemini-3.6-flash:medium` | `aethel-actor-capability` | guarded | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `valerius-factual-assurance` | baseline | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `valerius-factual-assurance` | native-skill | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `valerius-factual-assurance` | guarded | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `ciphera-repository-terms` | baseline | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `ciphera-repository-terms` | native-skill | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `ciphera-repository-terms` | guarded | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `thalassa-destructive-procedure` | baseline | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `thalassa-destructive-procedure` | native-skill | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `thalassa-destructive-procedure` | guarded | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `kestrel-flight-log-structured` | baseline | 3/3 |
| `github-copilot/gemini-3.6-flash:medium` | `kestrel-flight-log-structured` | native-skill | 3/3 |

## Mechanical verifier integrity

**Guard integrity: ACCEPTED.**
Exact accepted guarded outputs: 45/45.

## Semantic results

**Condition integrity: NOT ACCEPTED.**
Model identity matches: 149/153.
Routing safety passes: 149/153.
Native skill loads: 44/45.
Activation groups passing threshold: 17/18.

**Objective acceptance: NOT ACCEPTED.**
**Applicable procedure acceptance: NOT ACCEPTED.**
**Output-contract acceptance: NOT ACCEPTED.**

| Model | Condition | Runs | Gate pass/fail | Procedure pass/fail | Output-contract pass/fail |
|---|---|---:|---:|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | 18 | 4/14 | 0/3 | 18/0 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | 18 | 11/7 | 0/3 | 18/0 |
| `openai-codex/gpt-5.6-sol:high` | guarded | 15 | 12/3 | 0/3 | 15/0 |
| `github-copilot/claude-sonnet-5:low` | baseline | 15 | 4/11 | 3/0 | 12/3 |
| `github-copilot/claude-sonnet-5:low` | native-skill | 18 | 9/9 | 1/2 | 15/3 |
| `github-copilot/claude-sonnet-5:low` | guarded | 15 | 12/3 | 3/0 | 15/0 |
| `github-copilot/gemini-3.6-flash:medium` | baseline | 18 | 0/18 | 0/3 | 15/3 |
| `github-copilot/gemini-3.6-flash:medium` | native-skill | 17 | 9/8 | 0/3 | 14/3 |
| `github-copilot/gemini-3.6-flash:medium` | guarded | 15 | 12/3 | 2/1 | 15/0 |

## Style results

Style findings are advisory and cannot override semantic failures.

| Model | Condition | Runs | Mechanical warnings |
|---|---|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | 18 | 0 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | 18 | 0 |
| `openai-codex/gpt-5.6-sol:high` | guarded | 15 | 0 |
| `github-copilot/claude-sonnet-5:low` | baseline | 15 | 0 |
| `github-copilot/claude-sonnet-5:low` | native-skill | 18 | 0 |
| `github-copilot/claude-sonnet-5:low` | guarded | 15 | 0 |
| `github-copilot/gemini-3.6-flash:medium` | baseline | 18 | 0 |
| `github-copilot/gemini-3.6-flash:medium` | native-skill | 17 | 0 |
| `github-copilot/gemini-3.6-flash:medium` | guarded | 15 | 0 |

## Usage, cost, and duration

Means and population standard deviations use available successful samples only.

| Model | Condition | Input mean±sd | Output mean±sd | Reasoning mean±sd | Cost sum | Duration mean±sd (ms) |
|---|---|---:|---:|---:|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | 206.39±32.07 | 127.61±59.12 | 15.78±18.16 | 0.087485 | 8846.44±2370.43 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | 5807.72±2671.00 | 456.83±289.50 | 218.50±199.10 | 0.769385 | 18014.17±7864.83 |
| `openai-codex/gpt-5.6-sol:high` | guarded | 4204.53±1211.15 | 460.93±130.31 | 235.20±105.76 | 0.526600 | 15291.20±4238.67 |
| `github-copilot/claude-sonnet-5:low` | baseline | 313.33±60.24 | 179.33±83.77 | 0±0.00 | 0.036300 | 3519.40±848.71 |
| `github-copilot/claude-sonnet-5:low` | native-skill | 5±1.53 | 370.28±164.52 | 10.44±13.45 | 0.320060 | 8435.89±3405.92 |
| `github-copilot/claude-sonnet-5:low` | guarded | 2±0.00 | 305.20±21.94 | 2.80±7.22 | 0.287760 | 4080.20±431.90 |
| `github-copilot/gemini-3.6-flash:medium` | baseline | 217.11±33.67 | 137.44±61.37 | 0±0.00 | 0.024417 | 5319.72±1507.23 |
| `github-copilot/gemini-3.6-flash:medium` | native-skill | 5248.76±2381.55 | 239.12±106.24 | 0±0.00 | 0.164331 | 11297.76±4964.32 |
| `github-copilot/gemini-3.6-flash:medium` | guarded | 3847.47±14.53 | 191.73±17.74 | 0±0.00 | 0.108138 | 13189.33±4236.50 |

## Unresolved cells

Completed non-stop outputs retained as failure evidence: 5.

- failed: `github-copilot/gemini-3.6-flash:medium` native-skill aethel-actor-capability repetition 1
- failed: `github-copilot/claude-sonnet-5:low` baseline valerius-factual-assurance repetition 1
- failed: `github-copilot/claude-sonnet-5:low` baseline valerius-factual-assurance repetition 2
- failed: `github-copilot/claude-sonnet-5:low` baseline valerius-factual-assurance repetition 3

## Reproduce

```bash
python3 evals/run_pi_bench.py \
  --matrix evals/hybrid-release-candidate-matrix.json \
  --results-dir evals/results/hybrid-release-candidate
```

Existing matching successful raw cells are skipped. Failed cells retain attempt history and are retried.

## Limits

- Deterministic fixture checks cover enumerated properties only; open prose still needs attested semantic review.
- Provider reasoning metadata can be unavailable. Missing values remain `null` in raw and aggregate JSON.
- Hidden reasoning content is not stored.
- This benchmark is advisory and does not certify ASD-STE100 compliance.
