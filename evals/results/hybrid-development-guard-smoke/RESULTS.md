# Pi benchmark results

**COMPLETE: 3/3 cells successful.**

## Provenance

- Matrix: `development-guard-smoke` version 2
- Matrix SHA-256: `57708f855a0e019032b904bcbfda89de379091363d285474a1fd4c7045e01920`
- Package commit: `a3fde8294c88970e56606833c28a6aecf44580a6`
- Package dirty: `false`
- Skill SHA-256: `908f5c9aff34a7f34a771e1db0a2e2e421f53ec93b3f8af45926336e48b431fc`
- Extension SHA-256: `a36a7cd3b97555717f81a4016d2add6f627b2a550ce436e3d308ec54c801062c`
- Pi version: `0.84.1`
- Runner version: `7`

## Applicable cell denominators

| Model | Scenario | Condition | Successful/expected |
|---|---|---|---:|
| `openai-codex/gpt-5.6-sol:high` | `release-facts-and-causes` | guarded | 1/1 |
| `github-copilot/claude-sonnet-5:low` | `release-facts-and-causes` | guarded | 1/1 |
| `github-copilot/gemini-3.6-flash:medium` | `release-facts-and-causes` | guarded | 1/1 |

## Mechanical verifier integrity

**Guard integrity: ACCEPTED.**
Exact accepted guarded outputs: 3/3.

## Semantic results

**Condition integrity: ACCEPTED.**
Model identity matches: 3/3.
Routing safety passes: 3/3.
Native skill loads: 0/0.
Activation groups passing threshold: 0/0.

**Semantic acceptance: ACCEPTED.**
**Applicable procedure acceptance: ACCEPTED.**
**Output-contract acceptance: ACCEPTED.**

| Model | Condition | Runs | Gate pass/fail | Procedure pass/fail | Output-contract pass/fail |
|---|---|---:|---:|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | 0 | 0/0 | 0/0 | 0/0 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | 0 | 0/0 | 0/0 | 0/0 |
| `openai-codex/gpt-5.6-sol:high` | guarded | 1 | 1/0 | 0/0 | 1/0 |
| `github-copilot/claude-sonnet-5:low` | baseline | 0 | 0/0 | 0/0 | 0/0 |
| `github-copilot/claude-sonnet-5:low` | native-skill | 0 | 0/0 | 0/0 | 0/0 |
| `github-copilot/claude-sonnet-5:low` | guarded | 1 | 1/0 | 0/0 | 1/0 |
| `github-copilot/gemini-3.6-flash:medium` | baseline | 0 | 0/0 | 0/0 | 0/0 |
| `github-copilot/gemini-3.6-flash:medium` | native-skill | 0 | 0/0 | 0/0 | 0/0 |
| `github-copilot/gemini-3.6-flash:medium` | guarded | 1 | 1/0 | 0/0 | 1/0 |

### Deterministic semantic metrics

| Model | Condition | Metric | Rules | Failed | Pass rate |
|---|---|---|---:|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | `protected_span_equality` | 0 | 0 | n/a |
| `openai-codex/gpt-5.6-sol:high` | baseline | `required_fact_retention` | 0 | 0 | n/a |
| `openai-codex/gpt-5.6-sol:high` | baseline | `forbidden_fact_invention` | 0 | 0 | n/a |
| `openai-codex/gpt-5.6-sol:high` | baseline | `modality_and_certainty_preservation` | 0 | 0 | n/a |
| `openai-codex/gpt-5.6-sol:high` | baseline | `repository_term_preservation` | 0 | 0 | n/a |
| `openai-codex/gpt-5.6-sol:high` | native-skill | `protected_span_equality` | 0 | 0 | n/a |
| `openai-codex/gpt-5.6-sol:high` | native-skill | `required_fact_retention` | 0 | 0 | n/a |
| `openai-codex/gpt-5.6-sol:high` | native-skill | `forbidden_fact_invention` | 0 | 0 | n/a |
| `openai-codex/gpt-5.6-sol:high` | native-skill | `modality_and_certainty_preservation` | 0 | 0 | n/a |
| `openai-codex/gpt-5.6-sol:high` | native-skill | `repository_term_preservation` | 0 | 0 | n/a |
| `openai-codex/gpt-5.6-sol:high` | guarded | `protected_span_equality` | 0 | 0 | n/a |
| `openai-codex/gpt-5.6-sol:high` | guarded | `required_fact_retention` | 3 | 0 | 1.0000 |
| `openai-codex/gpt-5.6-sol:high` | guarded | `forbidden_fact_invention` | 3 | 0 | 1.0000 |
| `openai-codex/gpt-5.6-sol:high` | guarded | `modality_and_certainty_preservation` | 3 | 0 | 1.0000 |
| `openai-codex/gpt-5.6-sol:high` | guarded | `repository_term_preservation` | 0 | 0 | n/a |
| `github-copilot/claude-sonnet-5:low` | baseline | `protected_span_equality` | 0 | 0 | n/a |
| `github-copilot/claude-sonnet-5:low` | baseline | `required_fact_retention` | 0 | 0 | n/a |
| `github-copilot/claude-sonnet-5:low` | baseline | `forbidden_fact_invention` | 0 | 0 | n/a |
| `github-copilot/claude-sonnet-5:low` | baseline | `modality_and_certainty_preservation` | 0 | 0 | n/a |
| `github-copilot/claude-sonnet-5:low` | baseline | `repository_term_preservation` | 0 | 0 | n/a |
| `github-copilot/claude-sonnet-5:low` | native-skill | `protected_span_equality` | 0 | 0 | n/a |
| `github-copilot/claude-sonnet-5:low` | native-skill | `required_fact_retention` | 0 | 0 | n/a |
| `github-copilot/claude-sonnet-5:low` | native-skill | `forbidden_fact_invention` | 0 | 0 | n/a |
| `github-copilot/claude-sonnet-5:low` | native-skill | `modality_and_certainty_preservation` | 0 | 0 | n/a |
| `github-copilot/claude-sonnet-5:low` | native-skill | `repository_term_preservation` | 0 | 0 | n/a |
| `github-copilot/claude-sonnet-5:low` | guarded | `protected_span_equality` | 0 | 0 | n/a |
| `github-copilot/claude-sonnet-5:low` | guarded | `required_fact_retention` | 3 | 0 | 1.0000 |
| `github-copilot/claude-sonnet-5:low` | guarded | `forbidden_fact_invention` | 3 | 0 | 1.0000 |
| `github-copilot/claude-sonnet-5:low` | guarded | `modality_and_certainty_preservation` | 3 | 0 | 1.0000 |
| `github-copilot/claude-sonnet-5:low` | guarded | `repository_term_preservation` | 0 | 0 | n/a |
| `github-copilot/gemini-3.6-flash:medium` | baseline | `protected_span_equality` | 0 | 0 | n/a |
| `github-copilot/gemini-3.6-flash:medium` | baseline | `required_fact_retention` | 0 | 0 | n/a |
| `github-copilot/gemini-3.6-flash:medium` | baseline | `forbidden_fact_invention` | 0 | 0 | n/a |
| `github-copilot/gemini-3.6-flash:medium` | baseline | `modality_and_certainty_preservation` | 0 | 0 | n/a |
| `github-copilot/gemini-3.6-flash:medium` | baseline | `repository_term_preservation` | 0 | 0 | n/a |
| `github-copilot/gemini-3.6-flash:medium` | native-skill | `protected_span_equality` | 0 | 0 | n/a |
| `github-copilot/gemini-3.6-flash:medium` | native-skill | `required_fact_retention` | 0 | 0 | n/a |
| `github-copilot/gemini-3.6-flash:medium` | native-skill | `forbidden_fact_invention` | 0 | 0 | n/a |
| `github-copilot/gemini-3.6-flash:medium` | native-skill | `modality_and_certainty_preservation` | 0 | 0 | n/a |
| `github-copilot/gemini-3.6-flash:medium` | native-skill | `repository_term_preservation` | 0 | 0 | n/a |
| `github-copilot/gemini-3.6-flash:medium` | guarded | `protected_span_equality` | 0 | 0 | n/a |
| `github-copilot/gemini-3.6-flash:medium` | guarded | `required_fact_retention` | 3 | 0 | 1.0000 |
| `github-copilot/gemini-3.6-flash:medium` | guarded | `forbidden_fact_invention` | 3 | 0 | 1.0000 |
| `github-copilot/gemini-3.6-flash:medium` | guarded | `modality_and_certainty_preservation` | 3 | 0 | 1.0000 |
| `github-copilot/gemini-3.6-flash:medium` | guarded | `repository_term_preservation` | 0 | 0 | n/a |

## Style results

Style findings are advisory and cannot override semantic failures.

| Model | Condition | Runs | Mechanical warnings |
|---|---|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | 0 | 0 |
| `openai-codex/gpt-5.6-sol:high` | native-skill | 0 | 0 |
| `openai-codex/gpt-5.6-sol:high` | guarded | 1 | 0 |
| `github-copilot/claude-sonnet-5:low` | baseline | 0 | 0 |
| `github-copilot/claude-sonnet-5:low` | native-skill | 0 | 0 |
| `github-copilot/claude-sonnet-5:low` | guarded | 1 | 0 |
| `github-copilot/gemini-3.6-flash:medium` | baseline | 0 | 0 |
| `github-copilot/gemini-3.6-flash:medium` | native-skill | 0 | 0 |
| `github-copilot/gemini-3.6-flash:medium` | guarded | 1 | 0 |

## Usage, cost, and duration

Means and population standard deviations use available successful samples only.

| Model | Condition | Input mean±sd | Output mean±sd | Reasoning mean±sd | Cost sum | Duration mean±sd (ms) |
|---|---|---:|---:|---:|---:|---:|
| `openai-codex/gpt-5.6-sol:high` | baseline | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `openai-codex/gpt-5.6-sol:high` | native-skill | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `openai-codex/gpt-5.6-sol:high` | guarded | 3565±0.00 | 261±0.00 | 119±0.00 | 0.025655 | 10701±0.00 |
| `github-copilot/claude-sonnet-5:low` | baseline | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `github-copilot/claude-sonnet-5:low` | native-skill | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `github-copilot/claude-sonnet-5:low` | guarded | 2±0.00 | 238±0.00 | 0±0.00 | 0.018367 | 3487±0.00 |
| `github-copilot/gemini-3.6-flash:medium` | baseline | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `github-copilot/gemini-3.6-flash:medium` | native-skill | n/a±n/a | n/a±n/a | n/a±n/a | n/a | n/a±n/a |
| `github-copilot/gemini-3.6-flash:medium` | guarded | 3830±0.00 | 165±0.00 | 0±0.00 | 0.006982 | 10623±0.00 |

## Unresolved cells

None.

## Reproduce

```bash
python3 evals/run_pi_bench.py \
  --matrix evals/development-guard-smoke-matrix.json \
  --results-dir evals/results/hybrid-development-guard-smoke
```

Existing matching successful raw cells are skipped. Failed cells retain attempt history and are retried.

## Limits

- Deterministic fixture checks cover enumerated properties only; open prose still needs attested semantic review.
- Provider reasoning metadata can be unavailable. Missing values remain `null` in raw and aggregate JSON.
- Hidden reasoning content is not stored.
- This benchmark is advisory and does not certify ASD-STE100 compliance.
