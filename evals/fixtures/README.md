# Semantic-preservation fixtures

`semantic-preservation.json` is closed-world source data for deterministic semantic checks and Pi benchmarks.

## Contract

Each fixture contains:

- `mode`: requested writing mode.
- `tags`: required risk coverage.
- `task`: model instruction.
- `source`: only source text supplied for rewriting.
- `allowed_claims`: human-readable claim inventory for semantic review.
- `forbidden_claims`: known semantic contradictions with deterministic detection patterns.
- `invariants`: machine-readable facts, modalities, terminology, protected spans, causal limits, and procedure ordering.
- `passing_rewrites`: noncanonical paraphrases that must pass every rule.
- `failing_baselines`: known-bad rewrites with exact expected rule failures.

No fixture defines one preferred rewrite. Positive rewrites guard against overfitting checks to original wording.

## Check types

Checks within one invariant are conjunctive.

| Type | Pass condition |
|---|---|
| `contains` | Exact value occurs. If `count` is present, occurrence count must match. |
| `regex` | Python regular expression matches. |
| `precedes_regex` | First `before_pattern` match exists before first `after_pattern` match. |
| `inline_code` | Exact value occurs inside inline-code delimiters. |
| `fenced_code` | Exact value is complete content of a fenced code block. |
| `markdown_link` | Exact label and destination occur in one Markdown link. |
| `bold_text` | Exact value occurs inside Markdown bold delimiters. |

Container-aware checks prevent a changed command or URL from passing because the original text appears elsewhere.

## Review boundary

Deterministic patterns prove only enumerated properties. They cannot reject every paraphrased contradiction or unsupported implication.

- `allowed_claims` bounds attested semantic review.
- `forbidden_claims` records known contradictions and regression probes.
- A new factual claim still requires source comparison even when all deterministic checks pass.
- Protected-container checks are deterministic and must pass exactly.

## Adding a fixture

1. Add or update a failing contract test in `tests/test_semantic_fixtures.py`.
2. Run focused test and confirm expected failure.
3. Add smallest fixture data that passes.
4. Confirm source and at least one alternate rewrite satisfy every rule.
5. Add known-bad baseline and list exact failures.
6. Run full fixture test suite.

Run tests:

```bash
python3 -m unittest -v tests.test_semantic_fixtures
```
