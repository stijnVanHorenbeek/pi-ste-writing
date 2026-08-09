---
name: clear-technical-writing
description: >-
  Write, rewrite, or audit semantic-safe technical prose. Use for
  documentation and READMEs, API guides, setup procedures and runbooks,
  user-facing error messages and CLI help, incident reports and postmortems,
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

## Priority

1. Technical correctness.
2. Source facts and meaning.
3. Safety information and risk level.
4. User intent and exact output contracts.
5. Certainty, permission, recommendation, and obligation.
6. Repository and product terminology.
7. Clarity and structure.
8. Mode-specific style rules.

A lower item cannot override a higher item. Preserve the source and report the conflict
if no safe rewrite is proven.

## Modes

- **Clear (default):** Use concise, complete prose; use active voice for known actors.
  Remove fact-free filler. Do not apply the strict vocabulary or hard
  sentence limits.
- **Procedure:** Use for instructions, runbooks, recovery, and destructive actions. Use
  imperative instructions where appropriate. Put action-controlling conditions before
  commands, warnings before dangerous actions, and the required action before the
  possible consequence. Use one action per numbered step unless actions
  must occur together. Target 20 words or fewer when meaning and safe order remain intact.
- **Strict STE:** Activate only after an explicit request for STE, ASD-STE100, or an
  STE-compliance audit. Apply the 20-word procedural and 25-word descriptive limits after
  higher priorities pass. Preserve domain terms; report conflicts. Full vocabulary
  verification requires the official Issue 9 dictionary.

Classify mixed documents passage by passage. A note inside a procedure is descriptive
and cannot contain an instruction.

## Protected content

Unless the user explicitly requests a targeted change, preserve these exactly:

- Fenced and inline code.
- Identifiers, API names, and schema fields.
- Commands, flags, paths, URLs, and environment variables.
- Product names, UI labels, protocol terms, and repository terminology.
- Quoted errors, logs, diagnostics, and test output.
- Numbers, dates, versions, percentages, units, limits, and ranges.
- Markdown link destinations, reference IDs, and anchors.
- Machine-readable structure and exact output schemas.

Preserve protected value, occurrence count, container, and semantic role. Do not
rewrite raw output; separate commentary. Only the explicitly targeted
item becomes editable.

## Workflow

1. Identify the audience, requested mode, and exact output contract.
2. Inventory invariants and build a semantic ledger.
3. Classify each passage.
4. Rewrite only eligible prose. Never invent facts, causes, approvals, success, or safety.
5. Compare source and draft claim by claim, including negation, qualifiers, conditions,
   relationships, and modal force.
6. Check protected values by occurrence, container, and role.
7. Optionally run the advisory linter; inspect findings in context.

## References

- Load `references/semantic-preservation.md` for every source-based rewrite or audit.
- Load `references/use-cases.md` only when routing, scope, or coding examples are needed.
- Load `references/checklist.md` for every strict task, requested audit, high-risk procedure, or final verification.
- Load `references/ste-rules.md` only in strict mode.

Optional `scripts/ste_lint.py` command:

```bash
python3 scripts/ste_lint.py --mode MODE --format json --source SOURCE DRAFT
```

`MODE`: `clear`, `procedure`, or `strict`. Omit `--source SOURCE` without a source.
Findings are advisory, not proof. Use `--strict-gate` for nonzero-on-findings.

## Scope

Do not auto-apply this skill to code-review findings, debugging hypotheses, architecture
analysis, design tradeoffs, test-result interpretation, or patch summaries unless the
user requests a writing pass. Complete technical reasoning first; then edit only the
requested prose.

Do not auto-apply it to source code, generated code, raw tool output, logs, quoted
diagnostics, JSON, XML, YAML, CSV, schema-constrained output, marketing, brand, or
editorial voice.

An exact `/skill:clear-technical-writing` invocation can override an activation exclusion
only when the requested transformation is safe. Invocation alone does not authorize
semantic drift, unsafe ordering, or unrequested protected changes.

## Strict limit

STE-compliance audits must include:

> This audit is advisory and cannot certify ASD-STE100 compliance. Final approval rests
> with the writer using the official standard and dictionary.

ASD-STE100 is a registered trademark of ASD. This package is not affiliated with ASD,
STEMG, or the upstream project.
