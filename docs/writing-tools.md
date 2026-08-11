# Writing tool contract

Package version: `0.1.0`

## User command

`/ste_doc <path>` starts one repository-file rewrite with bundled clear-writing and semantic-preservation guidance.

Command:

- Requires one path; whole argument is treated as path.
- Accepts an outer single- or double-quoted path.
- Rejects empty, multiline, NUL-containing, or overly long paths.
- Keeps ambient repository and third-party tools active.
- Activates model-facing writing tools.
- Sends one task asking Pi to read, baseline, edit, check, and repair target file only.

Command does not read, edit, or validate target itself. Pi performs repository work through normal tools.

## `writing_begin`

Purpose: capture baseline after Pi reads file and before first `edit` or `write`.

Input:

```json
{
  "path": "README.md",
  "mode": "clear"
}
```

`mode` is `clear`, `procedure`, or `strict`.

Existing-file snapshot stores canonical path, display path, mode, UTF-8 source, byte SHA-256, and random snapshot ID. New-file snapshot records that target did not exist. Files must be valid UTF-8 and no larger than 2 MiB.

Visible model result contains readiness and next step. Full source and hash stay in tool-result details for branch/session restoration. Saved or exported sessions can therefore contain source text.

## `writing_check`

Purpose: compare current file with baseline and return repair information to model.

Input:

```json
{
  "path": "README.md"
}
```

Visible statuses:

- `clean`: file changed without detected protected drift or introduced findings.
- `unchanged`: bytes equal baseline.
- `needs-review`: protected drift or introduced findings exist.
- `no-snapshot`: no baseline for canonical path.
- `missing-file`: existing target cannot be read because it is absent.
- `invalid-utf8`: current file is not valid UTF-8.
- `analysis-error`: file or analysis work exceeds bound.

Visible `needs-review` result contains:

- Protected kind.
- Removed source values and added current values.
- Occurrence count, container, line, and column.
- At most 20 distinct protected changes across report, balanced between removed and added values when both exist.
- Counts of additional hidden removed and added groups when result is truncated.
- At most 20 introduced writing findings.
- Count of current findings that also existed in baseline.
- Repair and rerun instruction.

Protected values longer than 160 characters are truncated. Tool-result details retain hashes and same bounded summary, not full verifier inventories.

Findings are baseline-aware. Comparison uses finding rule, offending text, message, and protected kind while ignoring location shifts. Duplicate findings use occurrence counts. Existing warnings do not occupy visible introduced-finding budget.

New files have no source comparison; all detected findings are introduced.

## Protected comparison

Verifier compares exact value and occurrence count within these containers:

- `flow`
- `blockquote`
- `heading-1` through `heading-6`

Implemented kinds:

- Inline code.
- Fenced and indented code.
- Link destinations and labels.
- Quoted diagnostics.
- Bare URLs.
- Numeric tokens.
- Paths.
- CLI flags.
- Environment variables.
- Bold labels.
- JSON keys.
- Recognized identifiers.
- Modal phrases, including negated forms. Internal whitespace is canonicalized; capitalization remains exact.

Ordered-list markers are not protected numeric facts. CRLF and LF compare equally inside code.

## Lifecycle

Tools activate after exact package skill read, exact package skill invocation, or `/ste_doc`. Activation is additive.

Snapshots live in writing tool-result details. Session start and tree navigation reconstruct snapshots from current branch. Branches without skill activation or snapshots do not keep writing tools active.

## Limits

Analysis is synchronous and bounded to 2 MiB per input and 100,000 matches per regex class. Path and analysis failures are explicit.

Mechanical equality does not prove semantic equivalence. Verifier does not establish actor-role preservation, causality, factual completeness, safe procedure order, arbitrary terminology equality, or complete Markdown equivalence. Model must compare source claims, user-requested targets, and repository context.
