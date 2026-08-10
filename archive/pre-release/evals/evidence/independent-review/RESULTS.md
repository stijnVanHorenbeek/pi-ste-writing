# Pi benchmark results

**INCOMPLETE: 159/162 cells successful.**

## Provenance

- Matrix: `v1-independent-review` version 1
- Matrix SHA-256: `6cc06e4d17dd5e5f4bece86e40d4269d029152ddc0e97436a788b6b15381c4d8`
- Package commit: `b7cd7540a05176269bc14315863db4ffc7d97ec1`
- Package dirty: `false`
- Skill SHA-256: `072f9a0178034f55b1b81e9d95b715366759c6b85db9dab0a278e2239459475b`
- Pi version: `0.84.1`
- Runner version: `4`

## Semantic results

**Condition integrity: NOT ACCEPTED.**
Model identity matches: 159/162.
Routing safety passes: 159/162.
Native skill loads: 42/45.
Activation groups passing threshold: 17/18.

**Semantic acceptance: NOT ACCEPTED.**

| Model | Condition | Runs | Gate pass/fail | Procedure pass/fail | Output-contract pass/fail |
|---|---|---:|---:|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | 18 | 7/11 | 0/3 | 18/0 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | 18 | 12/6 | 3/0 | 18/0 |
| `openai-codex/gpt-5.6-sol:high` | direct-prompt | 18 | 6/12 | 1/2 | 18/0 |
| `github-copilot/claude-sonnet-5:low` | baseline | 18 | 7/11 | 0/3 | 18/0 |
| `github-copilot/claude-sonnet-5:low` | native-skill | 18 | 7/11 | 0/3 | 18/0 |
| `github-copilot/claude-sonnet-5:low` | direct-prompt | 15 | 7/8 | 1/2 | 15/0 |
| `github-copilot/gemini-3.6-flash:low` | baseline | 18 | 10/8 | 0/3 | 18/0 |
| `github-copilot/gemini-3.6-flash:low` | native-skill | 18 | 14/4 | 3/0 | 18/0 |
| `github-copilot/gemini-3.6-flash:low` | direct-prompt | 18 | 10/8 | 3/0 | 18/0 |

### Deterministic semantic metrics

| Model | Condition | Metric | Rules | Failed | Pass rate |
|---|---|---|---:|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | `protected_span_equality` | 42 | 0 | 1.0000 |
| `openai-codex/gpt-5.6-sol:high` | baseline | `required_fact_retention` | 18 | 4 | 0.7778 |
| `openai-codex/gpt-5.6-sol:high` | baseline | `forbidden_fact_invention` | 54 | 1 | 0.9815 |
| `openai-codex/gpt-5.6-sol:high` | baseline | `modality_and_certainty_preservation` | 33 | 14 | 0.5758 |
| `openai-codex/gpt-5.6-sol:high` | baseline | `repository_term_preservation` | 3 | 0 | 1.0000 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | `protected_span_equality` | 42 | 0 | 1.0000 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | `required_fact_retention` | 18 | 1 | 0.9444 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | `forbidden_fact_invention` | 54 | 0 | 1.0000 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | `modality_and_certainty_preservation` | 33 | 9 | 0.7273 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | `repository_term_preservation` | 3 | 0 | 1.0000 |
| `openai-codex/gpt-5.6-sol:high` | direct-prompt | `protected_span_equality` | 42 | 6 | 0.8571 |
| `openai-codex/gpt-5.6-sol:high` | direct-prompt | `required_fact_retention` | 18 | 1 | 0.9444 |
| `openai-codex/gpt-5.6-sol:high` | direct-prompt | `forbidden_fact_invention` | 54 | 0 | 1.0000 |
| `openai-codex/gpt-5.6-sol:high` | direct-prompt | `modality_and_certainty_preservation` | 33 | 12 | 0.6364 |
| `openai-codex/gpt-5.6-sol:high` | direct-prompt | `repository_term_preservation` | 3 | 0 | 1.0000 |
| `github-copilot/claude-sonnet-5:low` | baseline | `protected_span_equality` | 42 | 4 | 0.9048 |
| `github-copilot/claude-sonnet-5:low` | baseline | `required_fact_retention` | 18 | 2 | 0.8889 |
| `github-copilot/claude-sonnet-5:low` | baseline | `forbidden_fact_invention` | 54 | 0 | 1.0000 |
| `github-copilot/claude-sonnet-5:low` | baseline | `modality_and_certainty_preservation` | 33 | 11 | 0.6667 |
| `github-copilot/claude-sonnet-5:low` | baseline | `repository_term_preservation` | 3 | 0 | 1.0000 |
| `github-copilot/claude-sonnet-5:low` | native-skill | `protected_span_equality` | 42 | 9 | 0.7857 |
| `github-copilot/claude-sonnet-5:low` | native-skill | `required_fact_retention` | 18 | 5 | 0.7222 |
| `github-copilot/claude-sonnet-5:low` | native-skill | `forbidden_fact_invention` | 54 | 0 | 1.0000 |
| `github-copilot/claude-sonnet-5:low` | native-skill | `modality_and_certainty_preservation` | 33 | 8 | 0.7576 |
| `github-copilot/claude-sonnet-5:low` | native-skill | `repository_term_preservation` | 3 | 0 | 1.0000 |
| `github-copilot/claude-sonnet-5:low` | direct-prompt | `protected_span_equality` | 42 | 8 | 0.8095 |
| `github-copilot/claude-sonnet-5:low` | direct-prompt | `required_fact_retention` | 18 | 4 | 0.7778 |
| `github-copilot/claude-sonnet-5:low` | direct-prompt | `forbidden_fact_invention` | 36 | 0 | 1.0000 |
| `github-copilot/claude-sonnet-5:low` | direct-prompt | `modality_and_certainty_preservation` | 15 | 6 | 0.6000 |
| `github-copilot/claude-sonnet-5:low` | direct-prompt | `repository_term_preservation` | 3 | 0 | 1.0000 |
| `github-copilot/gemini-3.6-flash:low` | baseline | `protected_span_equality` | 42 | 0 | 1.0000 |
| `github-copilot/gemini-3.6-flash:low` | baseline | `required_fact_retention` | 18 | 0 | 1.0000 |
| `github-copilot/gemini-3.6-flash:low` | baseline | `forbidden_fact_invention` | 54 | 0 | 1.0000 |
| `github-copilot/gemini-3.6-flash:low` | baseline | `modality_and_certainty_preservation` | 33 | 9 | 0.7273 |
| `github-copilot/gemini-3.6-flash:low` | baseline | `repository_term_preservation` | 3 | 0 | 1.0000 |
| `github-copilot/gemini-3.6-flash:low` | native-skill | `protected_span_equality` | 42 | 0 | 1.0000 |
| `github-copilot/gemini-3.6-flash:low` | native-skill | `required_fact_retention` | 18 | 1 | 0.9444 |
| `github-copilot/gemini-3.6-flash:low` | native-skill | `forbidden_fact_invention` | 54 | 0 | 1.0000 |
| `github-copilot/gemini-3.6-flash:low` | native-skill | `modality_and_certainty_preservation` | 33 | 7 | 0.7879 |
| `github-copilot/gemini-3.6-flash:low` | native-skill | `repository_term_preservation` | 3 | 0 | 1.0000 |
| `github-copilot/gemini-3.6-flash:low` | direct-prompt | `protected_span_equality` | 42 | 0 | 1.0000 |
| `github-copilot/gemini-3.6-flash:low` | direct-prompt | `required_fact_retention` | 18 | 5 | 0.7222 |
| `github-copilot/gemini-3.6-flash:low` | direct-prompt | `forbidden_fact_invention` | 54 | 0 | 1.0000 |
| `github-copilot/gemini-3.6-flash:low` | direct-prompt | `modality_and_certainty_preservation` | 33 | 11 | 0.6667 |
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
| `github-copilot/claude-sonnet-5:low` | direct-prompt | 15 | 0 |
| `github-copilot/gemini-3.6-flash:low` | baseline | 18 | 0 |
| `github-copilot/gemini-3.6-flash:low` | native-skill | 18 | 0 |
| `github-copilot/gemini-3.6-flash:low` | direct-prompt | 18 | 0 |

## Usage, cost, and duration

Means and population standard deviations use available successful samples only.

| Model | Condition | Input mean±sd | Output mean±sd | Reasoning mean±sd | Cost sum | Duration mean±sd (ms) |
|---|---|---:|---:|---:|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | 285.06±66.75 | 165.44±154.82 | 48.61±92.71 | 0.114995 | 8384.89±4103.02 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | 5237.39±2405.46 | 494.39±264.86 | 256.28±169.99 | 0.744479 | 16868.78±6078.70 |
| `openai-codex/gpt-5.6-sol:high` | direct-prompt | 1167.78±66.68 | 210.83±127.30 | 98.33±113.32 | 0.218950 | 8827.06±2997.55 |
| `github-copilot/claude-sonnet-5:low` | baseline | 441.50±104.18 | 222.50±134.09 | 0±0.00 | 0.055944 | 3657.17±1040.18 |
| `github-copilot/claude-sonnet-5:low` | native-skill | 3.67±1.37 | 327.17±189.22 | 17.44±48.56 | 0.208067 | 6250.89±2976.18 |
| `github-copilot/claude-sonnet-5:low` | direct-prompt | 2±0.00 | 206.93±116.63 | 0±0.00 | 0.103885 | 3286.47±995.86 |
| `github-copilot/gemini-3.6-flash:low` | baseline | 300.94±74.92 | 138.17±87.20 | 0±0.00 | 0.026778 | 7252.39±4016.17 |
| `github-copilot/gemini-3.6-flash:low` | native-skill | 3804.06±2284.86 | 217.89±108.42 | 0±0.00 | 0.132125 | 11989.17±6436.24 |
| `github-copilot/gemini-3.6-flash:low` | direct-prompt | 1257.06±74.93 | 127.39±84.29 | 0±0.00 | 0.051138 | 7873.39±3434.13 |

## Unresolved cells

Completed non-stop outputs retained as failure evidence: 7.

- failed: `github-copilot/claude-sonnet-5:low` direct-prompt orbital-greenhouse-modal-policy repetition 1
- failed: `github-copilot/claude-sonnet-5:low` direct-prompt orbital-greenhouse-modal-policy repetition 2
- failed: `github-copilot/claude-sonnet-5:low` direct-prompt orbital-greenhouse-modal-policy repetition 3

## Reproduce

```bash
python3 evals/run_pi_bench.py \
  --matrix evals/independent-review-matrix.json \
  --results-dir evals/results/independent-review
```

Existing matching successful raw cells are skipped. Failed cells retain attempt history and are retried.

## Limits

- Deterministic fixture checks cover enumerated properties only; open prose still needs attested semantic review.
- Provider reasoning metadata can be unavailable. Missing values remain `null` in raw and aggregate JSON.
- Hidden reasoning content is not stored.
- This benchmark is advisory and does not certify ASD-STE100 compliance.
