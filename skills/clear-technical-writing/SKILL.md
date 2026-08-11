---
name: clear-technical-writing
description: >-
  Always auto-use when main task asks to create, draft, write, edit, update, improve,
  rewrite, revise, simplify, clarify, condense, restructure, or audit human-facing
  technical prose while preserving source meaning: incident reports, root-cause analyses,
  correlation findings, documentation, READMEs, APIs, runbooks, error explanations,
  CLI help, releases, or STE audits.
  Never auto-use to rewrite quoted errors or diagnostics. Do not auto-use when main
  task is code review, debugging, architecture, test interpretation, raw tool output,
  logs, schema-constrained output, source or generated code, marketing, or brand/editorial voice.
license: MIT
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

Never weaken a higher priority. Report conflicts when no safe rewrite is proven.

## Modes

- **Clear (default):** Use concise, complete prose and active voice for known actors.
  Remove filler. Do not apply strict vocabulary or sentence limits.
- **Procedure:** Use imperatives where appropriate. Put conditions before commands,
  warnings before dangerous actions, and actions before consequences. Preserve source
  block structure; do not add headings or move inline content to fences. Keep one action
  per numbered step.
- **Strict STE:** Only after an explicit STE or compliance-audit request. Apply 20-word
  procedural and 25-word descriptive limits after higher priorities. Preserve domain
  terms. Vocabulary review requires the official Issue 9 dictionary.

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

1. Identify audience, mode, output contract, protected content, and claims.
2. For repository text files, call `writing_begin` before `edit` or `write`. New files are supported.
3. Classify each passage, then rewrite; sequence does not prove cause.
4. Preserve the source modal when equivalence is uncertain.
5. Keep factual claims factual; keep separate causal thresholds separate.
6. Compare negation, scope, conditions, roles, values, counts, and containers.
7. After a repository edit, call `writing_check`; inspect exact protected deltas and introduced findings in context.
8. Before return, match each source actor and claim to the draft.
9. If fidelity is uncertain, retain the source clause.

`writing_begin` and `writing_check` are advisory. A protected mismatch can be intentional when the
user targeted that value. Without `writing_begin`, do not infer a baseline from Git or current text.
Automatic skill routing is model-dependent; explicit `/skill:clear-technical-writing` is deterministic.

Explicit invocation overrides routing exclusions, not semantic or safety boundaries.

## Progressive references

- Load `references/semantic-preservation.md` for every source rewrite or audit.
- Load `references/use-cases.md` only for routing or coding-focused examples.
- Load `references/checklist.md` only for strict audits or high-risk procedures.
- Load `references/ste-rules.md` only in strict mode.

Users can start a repository-file rewrite with `/ste_doc <path>`. Treat `writing_begin` and
`writing_check` as model-facing workflow tools, not commands users must manage. Analysis runs
in-process through package TypeScript extension; no Python runtime is required.
