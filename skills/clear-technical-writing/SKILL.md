---
name: clear-technical-writing
description: >-
  Always auto-use to rewrite or condense incident reports, root-cause analyses,
  correlation findings, documentation, READMEs, APIs, runbooks, error explanations,
  CLI help, releases/changelogs, or STE audits. Never auto-use to rewrite quoted
  errors or diagnostics. Do not auto-use when main task is code review, debugging,
  architecture, test interpretation, patch summaries without writing request, raw
  tool output, logs, schema-constrained output, source or generated code, or
  marketing/brand/editorial voice.
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

Map source occurrences one-to-one by container and semantic role. Do not repeat them in headings,
summaries, prerequisites, or steps. Never move inline code to a fence or fenced code
inline. Do not add formatting or rewrite raw output. Only targets are editable.

## Workflow

1. Identify audience, mode, and exact output contract.
2. Inventory protected content and claims.
3. Classify each passage.
4. Rewrite without inventing facts, causes, approval, success, or safety; sequence does not prove cause.
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
