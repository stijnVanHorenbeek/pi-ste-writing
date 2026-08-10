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

## Schema-v3 semantic boundary

`hybrid-regressions.json` contains seen development scenarios only. It does not replace or rescore frozen release evidence.

Schema v3 narrows objective checks to declared protected literals:

- `required_literals` requires each unique inline-code, fenced-code, Markdown-link, or bold value at least once in its original container.
- `ordered_literals` checks order only between declared immutable literals, such as exact commands and machine-return tokens.
- Repetition count, ordinary numbers, dates, units, identifiers outside protected containers, sentence wording, actor roles, modality, causality, warnings, and safety gates require source-relative semantic review.
- Exact external serialization stays in scenario-level output contracts.

Supporting rationale from official ASD-STE100 Issue 9:

- PDF page 47, printed page 1-1-3: approved alternatives can require a different sentence construction; meaning must remain unchanged.
- PDF page 57, Rule 1.11, printed page 1-1-13: use one consistent technical noun for one item. Rule does not require source occurrence-count equality.
- PDF pages 115–116, Rule 9.1, printed pages 1-9-1–1-9-2: use a different sentence construction when word-for-word replacement is insufficient, while preserving meaning.
- PDF page 122, Rule 9.4, printed page 1-9-8: distinct STE sentences can communicate same instruction; consistent wording is selected for repeated work steps.

These rules support meaning-relative review instead of exact prose matching. They do not define this benchmark architecture, prove semantic equivalence, or certify ASD-STE100 compliance. Official PDF and dictionary remain outside repository.

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

## Deterministic scoring

Score one candidate against one fixture:

```bash
python3 evals/score_fixtures.py FIXTURE_ID CANDIDATE --format json
```

Use `-` or omit `CANDIDATE` to read from standard input. Text output is the default.
JSON output is stable input for the benchmark runner.

The scorer reports each measurement separately:

| Measurement | Executable source | Gate behavior |
|---|---|---|
| Protected-span equality | `protected_span` invariants plus nonnumeric linter source equality by count and container | Semantic gate |
| Required fact retention | `fact` invariants | Semantic gate |
| Forbidden fact invention | All `forbidden_claims` patterns | Semantic gate |
| Modality and certainty preservation | `modality` and `causality` invariants | Semantic gate |
| Repository-term preservation | `repository_term` invariants | Semantic gate |
| Procedure structure | `procedure` invariants plus mechanical condition-order and step-numbering findings | Semantic gate |
| Mechanical style warnings | Linter findings in the `style` category | Advisory only |

Schema-v1 semantic and procedure failures exit 1. Style warnings remain advisory and exit 0 when all semantic and procedure gates pass. Schema-v2/v3 objective-contract failures exit 1; open semantic review is separate and does not appear in scorer output. Invocation and input errors exit 2. No combined semantic-and-style score exists.

Nonnumeric linter source-comparison findings are protected-span failures, including
added or removed protected values outside `protected_span` invariants. Numeric values
remain gated by their declared fact, modality, or procedure invariants. Generic numeric
token comparison is not a semantic gate because safe formatting can add list ordinals
or repeat units without changing a declared value.

The scorer measures enumerated rules only. `allowed_claims` still requires attested
source review. Exact output contracts remain scenario-level benchmark gates; this scorer
does not infer schemas that fixtures do not declare. A passing report does not prove full
semantic equivalence or certify ASD-STE100 compliance.

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
