# Pi benchmark results

**COMPLETE: 162/162 cells successful.**

## Provenance

- Matrix: `v1` version 6
- Matrix SHA-256: `79d5bf8714f725b1c25694689027efbfb7e75e01daacaf0f62e6323b276be5dd`
- Package commit: `61700956572775e85a0d79def70eff40505bf858`
- Package dirty: `false`
- Skill SHA-256: `072f9a0178034f55b1b81e9d95b715366759c6b85db9dab0a278e2239459475b`
- Pi version: `0.84.1`
- Runner version: `3`

## Semantic results

**Condition integrity: NOT ACCEPTED.**
Model identity matches: 162/162.
Routing safety passes: 162/162.
Native skill loads: 42/45.
Activation groups passing threshold: 17/18.

**Semantic acceptance: NOT ACCEPTED.**

| Model | Condition | Runs | Gate pass/fail | Procedure pass/fail | Output-contract pass/fail |
|---|---|---:|---:|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | 18 | 12/6 | 0/3 | 18/0 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | 18 | 17/1 | 3/0 | 18/0 |
| `openai-codex/gpt-5.6-sol:high` | direct-prompt | 18 | 15/3 | 3/0 | 18/0 |
| `github-copilot/claude-sonnet-5:low` | baseline | 18 | 16/2 | 1/2 | 18/0 |
| `github-copilot/claude-sonnet-5:low` | native-skill | 18 | 15/3 | 1/2 | 18/0 |
| `github-copilot/claude-sonnet-5:low` | direct-prompt | 18 | 17/1 | 2/1 | 18/0 |
| `github-copilot/gemini-3.6-flash:low` | baseline | 18 | 8/10 | 0/3 | 18/0 |
| `github-copilot/gemini-3.6-flash:low` | native-skill | 18 | 17/1 | 3/0 | 18/0 |
| `github-copilot/gemini-3.6-flash:low` | direct-prompt | 18 | 17/1 | 3/0 | 18/0 |

### Deterministic semantic metrics

| Model | Condition | Metric | Rules | Failed | Pass rate |
|---|---|---|---:|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | `protected_span_equality` | 45 | 0 | 1.0000 |
| `openai-codex/gpt-5.6-sol:high` | baseline | `required_fact_retention` | 18 | 0 | 1.0000 |
| `openai-codex/gpt-5.6-sol:high` | baseline | `forbidden_fact_invention` | 51 | 2 | 0.9608 |
| `openai-codex/gpt-5.6-sol:high` | baseline | `modality_and_certainty_preservation` | 33 | 10 | 0.6970 |
| `openai-codex/gpt-5.6-sol:high` | baseline | `repository_term_preservation` | 3 | 0 | 1.0000 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | `protected_span_equality` | 45 | 0 | 1.0000 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | `required_fact_retention` | 18 | 0 | 1.0000 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | `forbidden_fact_invention` | 51 | 0 | 1.0000 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | `modality_and_certainty_preservation` | 33 | 1 | 0.9697 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | `repository_term_preservation` | 3 | 0 | 1.0000 |
| `openai-codex/gpt-5.6-sol:high` | direct-prompt | `protected_span_equality` | 45 | 0 | 1.0000 |
| `openai-codex/gpt-5.6-sol:high` | direct-prompt | `required_fact_retention` | 18 | 0 | 1.0000 |
| `openai-codex/gpt-5.6-sol:high` | direct-prompt | `forbidden_fact_invention` | 51 | 0 | 1.0000 |
| `openai-codex/gpt-5.6-sol:high` | direct-prompt | `modality_and_certainty_preservation` | 33 | 3 | 0.9091 |
| `openai-codex/gpt-5.6-sol:high` | direct-prompt | `repository_term_preservation` | 3 | 0 | 1.0000 |
| `github-copilot/claude-sonnet-5:low` | baseline | `protected_span_equality` | 45 | 0 | 1.0000 |
| `github-copilot/claude-sonnet-5:low` | baseline | `required_fact_retention` | 18 | 0 | 1.0000 |
| `github-copilot/claude-sonnet-5:low` | baseline | `forbidden_fact_invention` | 51 | 0 | 1.0000 |
| `github-copilot/claude-sonnet-5:low` | baseline | `modality_and_certainty_preservation` | 33 | 0 | 1.0000 |
| `github-copilot/claude-sonnet-5:low` | baseline | `repository_term_preservation` | 3 | 0 | 1.0000 |
| `github-copilot/claude-sonnet-5:low` | native-skill | `protected_span_equality` | 45 | 2 | 0.9556 |
| `github-copilot/claude-sonnet-5:low` | native-skill | `required_fact_retention` | 18 | 1 | 0.9444 |
| `github-copilot/claude-sonnet-5:low` | native-skill | `forbidden_fact_invention` | 51 | 0 | 1.0000 |
| `github-copilot/claude-sonnet-5:low` | native-skill | `modality_and_certainty_preservation` | 33 | 0 | 1.0000 |
| `github-copilot/claude-sonnet-5:low` | native-skill | `repository_term_preservation` | 3 | 0 | 1.0000 |
| `github-copilot/claude-sonnet-5:low` | direct-prompt | `protected_span_equality` | 45 | 1 | 0.9778 |
| `github-copilot/claude-sonnet-5:low` | direct-prompt | `required_fact_retention` | 18 | 0 | 1.0000 |
| `github-copilot/claude-sonnet-5:low` | direct-prompt | `forbidden_fact_invention` | 51 | 0 | 1.0000 |
| `github-copilot/claude-sonnet-5:low` | direct-prompt | `modality_and_certainty_preservation` | 33 | 0 | 1.0000 |
| `github-copilot/claude-sonnet-5:low` | direct-prompt | `repository_term_preservation` | 3 | 0 | 1.0000 |
| `github-copilot/gemini-3.6-flash:low` | baseline | `protected_span_equality` | 45 | 4 | 0.9111 |
| `github-copilot/gemini-3.6-flash:low` | baseline | `required_fact_retention` | 18 | 1 | 0.9444 |
| `github-copilot/gemini-3.6-flash:low` | baseline | `forbidden_fact_invention` | 51 | 0 | 1.0000 |
| `github-copilot/gemini-3.6-flash:low` | baseline | `modality_and_certainty_preservation` | 33 | 17 | 0.4848 |
| `github-copilot/gemini-3.6-flash:low` | baseline | `repository_term_preservation` | 3 | 0 | 1.0000 |
| `github-copilot/gemini-3.6-flash:low` | native-skill | `protected_span_equality` | 45 | 0 | 1.0000 |
| `github-copilot/gemini-3.6-flash:low` | native-skill | `required_fact_retention` | 18 | 0 | 1.0000 |
| `github-copilot/gemini-3.6-flash:low` | native-skill | `forbidden_fact_invention` | 51 | 0 | 1.0000 |
| `github-copilot/gemini-3.6-flash:low` | native-skill | `modality_and_certainty_preservation` | 33 | 0 | 1.0000 |
| `github-copilot/gemini-3.6-flash:low` | native-skill | `repository_term_preservation` | 3 | 1 | 0.6667 |
| `github-copilot/gemini-3.6-flash:low` | direct-prompt | `protected_span_equality` | 45 | 0 | 1.0000 |
| `github-copilot/gemini-3.6-flash:low` | direct-prompt | `required_fact_retention` | 18 | 1 | 0.9444 |
| `github-copilot/gemini-3.6-flash:low` | direct-prompt | `forbidden_fact_invention` | 51 | 1 | 0.9804 |
| `github-copilot/gemini-3.6-flash:low` | direct-prompt | `modality_and_certainty_preservation` | 33 | 1 | 0.9697 |
| `github-copilot/gemini-3.6-flash:low` | direct-prompt | `repository_term_preservation` | 3 | 0 | 1.0000 |

## Style results

Style findings are advisory and cannot override semantic failures.

| Model | Condition | Runs | Mechanical warnings |
|---|---|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | 18 | 0 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | 18 | 0 |
| `openai-codex/gpt-5.6-sol:high` | direct-prompt | 18 | 0 |
| `github-copilot/claude-sonnet-5:low` | baseline | 18 | 0 |
| `github-copilot/claude-sonnet-5:low` | native-skill | 18 | 0 |
| `github-copilot/claude-sonnet-5:low` | direct-prompt | 18 | 0 |
| `github-copilot/gemini-3.6-flash:low` | baseline | 18 | 0 |
| `github-copilot/gemini-3.6-flash:low` | native-skill | 18 | 0 |
| `github-copilot/gemini-3.6-flash:low` | direct-prompt | 18 | 0 |

## Usage, cost, and duration

Means and population standard deviations use available successful samples only.

| Model | Condition | Input mean±sd | Output mean±sd | Reasoning mean±sd | Cost sum | Duration mean±sd (ms) |
|---|---|---:|---:|---:|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | 207.50±40.27 | 188±126.72 | 96.72±107.18 | 0.120195 | 10776.83±7046.35 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | 5968.94±2830.79 | 509.67±328.79 | 288.33±257.13 | 0.813961 | 20966±11776.19 |
| `openai-codex/gpt-5.6-sol:high` | direct-prompt | 1090.56±40.10 | 154.44±114.49 | 67.67±93.68 | 0.181550 | 7745.61±2559.55 |
| `github-copilot/claude-sonnet-5:low` | baseline | 319.28±68.28 | 155.33±122.31 | 0±0.00 | 0.039454 | 3341.72±1762.86 |
| `github-copilot/claude-sonnet-5:low` | native-skill | 4.22±1.75 | 304.33±195.32 | 10.61±15.77 | 0.278359 | 6946.83±4459.90 |
| `github-copilot/claude-sonnet-5:low` | direct-prompt | 2±0.00 | 146.61±93.05 | 12.33±50.85 | 0.107454 | 2999.39±801.96 |
| `github-copilot/gemini-3.6-flash:low` | baseline | 220.67±47.38 | 99.89±65.75 | 0±0.00 | 0.019443 | 8058.33±5664.91 |
| `github-copilot/gemini-3.6-flash:low` | native-skill | 5556.61±3092.57 | 210.61±98.72 | 0±0.00 | 0.179062 | 11527.28±4972.07 |
| `github-copilot/gemini-3.6-flash:low` | direct-prompt | 1176.67±47.35 | 92.50±57.80 | 0±0.00 | 0.044257 | 6906.50±2796.87 |

## Unresolved cells

Completed non-stop outputs retained as failure evidence: 1.

None.

## Reproduce

```bash
python3 evals/run_pi_bench.py \
  --matrix evals/v1-matrix.json \
  --results-dir evals/results/v6
```

Existing matching successful raw cells are skipped. Failed cells retain attempt history and are retried.

## Limits

- Deterministic fixture checks cover enumerated properties only; open prose still needs attested semantic review.
- Provider reasoning metadata can be unavailable. Missing values remain `null` in raw and aggregate JSON.
- Hidden reasoning content is not stored.
- This benchmark is advisory and does not certify ASD-STE100 compliance.
