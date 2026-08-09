---
name: clear-technical-writing
description: >-
  Write, rewrite, or audit semantic-safe technical prose. Use for
  documentation and READMEs, API guides, setup procedures and runbooks,
  user-facing error messages and CLI help, incident findings and postmortems,
  release notes and changelogs, translation-ready prose, or explicit STE,
  ASD-STE100, or STE-compliance audits.
  Do not auto-use for code review, debugging, architecture analysis or design tradeoffs,
  test-result interpretation, patch summaries without a writing-pass request, raw tool
  output, logs, and quoted diagnostics, JSON, XML, YAML, CSV, or schema-constrained
  output, source or generated code, marketing, brand, or editorial voice.
license: MIT
compatibility: Pi; Python 3 optional for linter.
---

# Clear writing

## Priorities

Apply in order:

1. Technical correctness.
2. Source facts and meaning.
3. Safety and risk level.
4. User intent and exact output contract.
5. Certainty, permission, recommendation, and obligation.
6. Repository and product terminology.
7. Clarity and structure.
8. Mode-specific style.

Never improve a lower priority by weakening a higher one. Report a conflict when no safe
rewrite is proven.

## Modes

- **Clear (default):** Use concise, complete prose and active voice for known actors.
  Remove fact-free filler. Do not apply strict vocabulary or sentence limits.
- **Procedure:** Use imperative instructions where appropriate. Put action-controlling
  conditions before commands, warnings before dangerous actions, and required actions
  before possible consequences. Keep one action per numbered step unless actions must
  occur together. Target 20 words or fewer only when meaning and safe order remain intact.
- **Strict STE:** Use only after an explicit STE, ASD-STE100, or compliance-audit request.
  Apply 20-word procedural and 25-word descriptive limits only after higher priorities
  pass. Preserve domain terms. Full vocabulary review requires the official Issue 9
  dictionary.

Classify mixed documents by passage. Notes in procedures are descriptive, not
instructions.

## Protected content

Preserve these unless the user targets them:

- Fenced and inline code.
- Identifiers, API names, and schema fields.
- Commands, flags, paths, URLs, and environment variables.
- Product names, UI labels, protocols, and repository terms.
- Quoted errors, logs, diagnostics, and tests.
- Numbers, dates, versions, percentages, units, limits, and ranges.
- Modals: `must`, `should`, `can`, `may`, `might`, and `could`.
- Markdown link destinations, reference IDs, and anchors.
- Machine-readable structures and schemas.

Keep count, container, and semantic role. Never add formatting or rewrite raw output.
Only targeted items become editable.

## Workflow

1. Identify audience, mode, and exact output contract.
2. Inventory protected content and claims.
3. Classify each passage.
4. Rewrite eligible prose without inventing facts, causes, approval, success, or safety.
5. Compare source and draft for negation, qualifiers, conditions, relationships, modal
   force, protected values, containers, and roles.
6. Run the advisory linter only when useful; inspect findings in context.

An explicit `/skill:clear-technical-writing` invocation can override routing exclusions,
but never authorizes semantic drift, unsafe ordering, or unrequested protected changes.

## Progressive references

- Load `references/semantic-preservation.md` for every source rewrite or audit.
- Load `references/use-cases.md` only for routing or coding-focused examples.
- Load `references/checklist.md` only for strict audits or high-risk procedures.
- Load `references/ste-rules.md` only in strict mode.

Linter:

```bash
python3 scripts/ste_lint.py --mode MODE --format json --source SOURCE DRAFT
```

`MODE` is `clear`, `procedure`, or `strict`. Omit `--source SOURCE` when no source exists.
Findings are advisory. Use `--strict-gate` only when warnings must produce a nonzero exit.
