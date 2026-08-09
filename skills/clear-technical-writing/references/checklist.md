# Mode-aware verification checklist

Run checks in priority order. A lower-priority style improvement cannot override an
unresolved higher-priority failure.

## Governing decision hierarchy

Use this hierarchy whenever two checks conflict:

1. Technical correctness.
2. Source facts and meaning.
3. Safety information and risk level.
4. User intent and exact output contracts.
5. Certainty, permission, recommendation, and obligation.
6. Repository and product terminology.
7. Clarity and structure.
8. Mode-specific style rules.

The numbered checklist sections define review sequence, not conflict precedence.
Checklist sequence does not let an output contract override safety. Reopen an earlier
status when a later safety check reveals a higher-priority problem.

## 1. Semantic fidelity

Build or reuse the semantic ledger from `references/semantic-preservation.md`. Compare
source and draft claim by claim, not by overall impression.

Confirm all items:

- Verify technical correctness against supplied evidence and authoritative repository
  material.
- Preserve safety information and risk level before checking any output or style rule.
- Actors, actions, objects, states, exclusions, and results are unchanged.
- Numbers, dates, times, versions, percentages, units, limits, ranges, and direction of
  change are unchanged.
- Scope and logic remain attached to the same claim: negation, `all`, `some`, `only`,
  defaults, exceptions, comparisons, conditions, and sequence.
- Evidence and causality retain their source strength. Sequence or correlation did not
  become causation; an unknown cause remains unknown.
- Certainty, capability, possibility, permission, recommendation, and obligation retain
  their distinct force.
- No inferred approval, successful execution, compatibility, root cause, or safety claim
  was added.

Search both source and draft for these candidates. A hit is a review prompt, not an
automatic violation.

- **Quantities:** `(?<![\w.])(?:\d{1,2}:\d{2}(?::\d{2})?|v?\d[\d,]*(?:\.\d+)*(?:-\d[\d,]*(?:\.\d+)*)*%?(?:\s*(?:ms|seconds?|minutes?|hours?|days?|MB|GB|TB))?)`.
  Compare value, unit, range, direction, and occurrence count.
- **Modality:** `\b(must|must not|should|can|may|might|could|will)\b`. Compare semantic
  force and subject.
- **Scope:** `\b(all|some|only|at least|up to|except|unless|default)\b`. Compare the
  population, limit, exception, or condition.
- **Evidence:** `\b(observed|reported|suggests?|confirmed|unknown|no evidence)\b`. Compare
  attribution and confidence.
- **Causality:** `\b(after|following|because|caused?|correlat\w*)\b`. Classify sequence,
  correlation, or confirmed cause.
- **Negation:** `\b(no|not|never|without|does not|must not)\b`. Compare predicate and
  scope.

Reject the draft for added claims, lost qualifiers, contradictions, reversed
relationships, or unsupported implications. If required information is absent, ask a
focused question or label it `unknown`, `not provided`, or `not established`.

When an audit has no source, semantic preservation cannot receive `pass`; report
`needs-review` or state that the task is original authoring with no source claims.

## 2. Protected-span equality

Compare protected content by value, occurrence count, container, and semantic role.
Check fenced and indented code, inline code, commands, flags, paths, URLs, identifiers,
API fields, UI labels, diagnostics, numbers, dates, versions, Markdown links, reference
IDs, and structured data.

From the skill directory, run the advisory comparison when source and draft files exist:

```bash
python3 scripts/ste_lint.py --mode MODE --format json --source SOURCE DRAFT
```

Replace `MODE` with `clear`, `procedure`, or `strict`. Inspect every `protected-span`
finding. The linter compares implemented containers and literal classes; it does not
prove complete semantic or formatting equality.

Also inspect a source-to-draft diff. Confirm that:

- Protected values did not change, disappear, or gain duplicates.
- Code and commands remain in their original container with significant whitespace and
  line breaks intact.
- A copied old value elsewhere does not mask a changed link, command, path, or diagnostic.
- Markdown labels, destinations, anchors, and reference relationships still resolve.
- Any protected change matches an explicit targeted user request.

## 3. Exact output-contract preservation

Identify the output contract before judging prose. Check required format, schema, keys,
field types, ordering, delimiters, placeholders, headings, line count, word count, and
verbatim fragments.

- Parse or validate structured output with the requested parser or schema when possible.
- Compare required keys and values against the exact schema, not a prose summary of it.
- Preserve code fences, frontmatter, templates, CSV columns, and protocol framing.
- Preserve requested prefixes, suffixes, citation forms, and error-message formats.
- Do not rewrite machine-readable output, raw tool output, code, or quoted diagnostics
  as prose.
- Do not add commentary outside a response contract that permits only structured data.

A valid sentence is still a failure when it breaks the requested contract. Record this
section as `not-applicable` only when no exact contract exists.

## 4. Repository terminology

Build a concept-to-term ledger from repository files, supplied product text, and the
source. Check each concept against its established spelling, capitalization, formatting,
and role.

- Preserve identifiers, API names, schema fields, product names, UI labels, protocol
  terms, and other exact technical names.
- Keep distinct concepts distinct. Do not merge terms such as `config`, `settings`, and
  `options` unless the repository defines them as synonyms.
- Use one established name for one concept; do not rotate synonyms for style.
- Treat an apparent terminology conflict as a question or finding. Do not choose a
  preferred term without evidence.
- In strict mode, treat repository and domain terms as technical names before applying
  controlled-vocabulary guidance.

Search for known variants and near-synonyms, but review each hit in context. Matching
words do not prove that two concepts are interchangeable.

## 5. Procedural safety and action ordering

Apply these checks to procedural commands, runbooks, recovery steps, and destructive
operations. Do not move every descriptive `if` or `when` clause.

Confirm this order where the source requires each element:

1. Required preconditions and approvals appear before the controlled action.
2. Put the warning block before the dangerous operation.
3. Put each action-controlling condition before its command.
4. Put the required command before the risk or possible consequence inside the warning.
5. Confirm that each verification step follows the action that it verifies.
6. Preserve each recovery requirement and place recovery information before an
   irreversible action when the source requires it.

Also confirm:

- Use one action per numbered step unless actions must occur at the same time.
- Imperative instructions retain the correct actor, object, parameters, and conditions.
- Descriptive scope statements do not become instructions.
- Commands, flags, identifiers, approvals, snapshots, and verification commands remain
  exact.
- Procedure mode uses a 20-word target for detected instructions. Split only when the
  split preserves logic and safe execution.
- Strict mode applies the Rule 5.1 hard limit after higher-priority checks pass.

A correct command in the wrong sequence is a safety failure.

## 6. Mechanical clarity warnings

Apply mechanical checks only after Sections 1-5 pass.

- **Clear mode:** prefer concise, complete prose and active voice when the actor is known.
  Do not enforce hard sentence or vocabulary limits.
- **Procedure mode:** apply instruction classification, the safe 20-word target, and
  procedure ordering. Descriptive passages keep clear-mode treatment.
- **Strict mode:** add the full strict checks in Section 7.

### Searchable patterns

A search hit is not automatically a violation. Ignore protected content and decide
whether a safe change preserves meaning.

- **Contractions:** `\b(?:\w+n't|(?:I|you|we|they|he|she|it|that|there|here|what|who|where|when|why|how)'(?:ll|re|ve|d|s))\b`.
  Strict: expand without changing tense or force.
- **Perfect constructions:** `\b(has|have|had)\s+\w+`. Strict: inspect for disallowed
  complex tense; do not change event timing.
- **Progressive passive:** `\b(is|are|was|were) being\b`. Strict: inspect voice and agent
  knowledge.
- **`-ing` clause:** `,\s*\w+ing\b`. Strict: inspect verbal use; technical nouns are
  different.
- **Semicolon:** `;`. Strict: split only if scope and logic remain unchanged.
- **Latin abbreviation:** `\b(e\.g\.|i\.e\.|etc\.?)`. Strict: use explicit English or
  name the items.
- **Filler candidate:** `\b(simply|just|easily|seamlessly|robust|powerful)\b`. Clear and
  stricter modes: delete only when it carries no fact.
- **Modal candidate:** `\b(should|would|may|might|could)\b`. Strict: report; never replace
  mechanically.
- **Condition candidate:** `\b(if|when|unless)\b`. Procedure: move only an
  action-controlling condition that trails its command.

Judgment checks:

- Every pronoun has a clear referent.
- Active voice names a known actor when that improves clarity.
- Paragraphs group related facts and preserve evidence relationships.
- Lists reduce structural complexity without changing sequence or scope.
- Removed filler contained no measurement, qualifier, risk, or product meaning.
- Sentence splits preserve negation, conditions, comparisons, and causal limits.

### Advisory linter boundary

The linter provides bounded heuristics:

- Clear mode can compare implemented protected spans when `--source` is supplied.
- Procedure mode adds detected-instruction length and trailing-condition warnings.
- Strict mode adds modal, contraction, Latin-abbreviation, and classified sentence-length
  warnings.

It does not check the official dictionary, all 53 rules, all Markdown syntax, full
semantic equivalence, output-schema validity, or every procedural verb. It also does not
apply Rule 5.4 to strict-mode mixed passages; review those passages manually. The linter
does not implement the `would` modal candidate or the `unless` condition candidate.

Zero linter warnings do not prove semantic correctness or compliance. The
`--strict-gate` option changes the process exit code when warnings exist; it does not
turn advisory findings into certification.

## 7. Strict STE rules when requested

Load `references/ste-rules.md` only after an explicit strict STE request or
compliance-oriented audit. Complete Sections 1-6 first.

Then:

1. Classify each eligible passage as procedural or descriptive.
2. Apply the 20-word procedural and 25-word descriptive limits using Rules 5.1, 6.3, and
   8.4-8.7.
3. Check one instruction per procedural sentence and one topic per descriptive paragraph.
4. Check strict word use, word forms, verb forms, voice, complete grammar, punctuation,
   paragraph structure, and GR-1 through GR-8.
5. Mark Rules 1.1-1.4, 3.1, and 9.2 as dictionary-dependent unless a reviewer used the
   official Issue 9 dictionary.
6. Record every higher-priority conflict instead of forcing a style change.

A strict audit cannot receive full `pass` for dictionary-dependent rules unless a
reviewer used the official Issue 9 dictionary. Mark unverified coverage `needs-review`.

Do not convert recommendations to requirements, possibilities to certainties, or
permissions to capabilities to satisfy strict vocabulary guidance.
Retain the source and report an unresolved conflict when no semantically equivalent
strict rewrite is proven.

Strict review is advisory. It cannot certify ASD-STE100 compliance.

## Mixed-mode handling

Classify each passage separately before applying mode checks.

| Passage | Verification treatment |
|---|---|
| Descriptive prose | Preserve facts and relationships; clear mode has no hard sentence limit. |
| Procedural instruction | Apply procedure ordering and the instruction-specific length policy. |
| A note inside a procedure | A note inside a procedure is descriptive and cannot contain an instruction. |
| Warning or caution | Treat as procedural safety text; preserve risk level and action order. |
| Quoted, code, and structured passages | Preserve exactly unless the user requests a targeted change. |
| Mixed paragraph | Split classification by sentence or block; do not force one rule set onto unrelated passages. |

Strict checks activate only after an explicit strict STE request or compliance-oriented
audit. Clear and procedure reviews do not inherit strict vocabulary, punctuation, or
25-word descriptive limits.

## Delivery gate

Record a status for each priority before delivery:

- Semantic fidelity: `pass`
- Protected-span equality: `pass`
- Output contract: `pass` or `not-applicable`
- Repository terminology: `pass`
- Procedural safety: `pass` or `not-applicable`
- Mechanical clarity: `pass` or advisory findings recorded
- Strict STE: `pass`, `needs-review`, or `not-applicable`

Do not continue to lower-priority style fixes while a higher-priority failure remains
unresolved, unless the user explicitly changes the governing requirement. Acknowledging
a failure does not make it pass. Never describe a draft as successful when semantic,
protected, contract, terminology, or safety status is `fail` or `needs-review`.

## Audit-report format

Use this structure for requested audits:

```text
Mode: clear | procedure | strict
Source: <path, supplied text, or not provided>
Draft: <path or supplied text>
Scope: <passages and exclusions>
Overall status: pass | fail | needs-review

Priority results:
1. Semantic fidelity: <status and evidence>
2. Protected-span equality: <status and evidence>
3. Exact output contract: <status and evidence>
4. Repository terminology: <status and evidence>
5. Procedural safety: <status and evidence>
6. Mechanical clarity: <status and warning count>
7. Strict STE: <status, rule coverage, and unresolved conflicts>

Repeat this block for every finding:
- Status: `pass | fail | needs-review | not-applicable`
- Priority and category: <1-7; semantic | protected | contract | terminology | procedure | style | strict>
- Location: <line, section, or quoted fragment>
- Source evidence: <exact source support>
- Draft text: <offending or reviewed text>
- Semantic or operational risk: <meaning, contract, or execution impact>
- Safe action: <rewrite, retain source, question, or report-only>

Strict coverage:
- Deterministic checks: <performed checks>
- Judgment checks: <reviewed areas>
- Dictionary coverage: <official Issue 9 dictionary used | not verified>
- Linter: <mode, warnings, and advisory status>
```

Do not label output `compliant` or `certified`, even when all implemented checks pass.
For every compliance-oriented audit, include:

> This audit is advisory and cannot certify ASD-STE100 compliance. Final approval rests
> with the writer using the official standard and dictionary.

## Provenance

This checklist reverses and adapts the mechanical-first review in
[`AminBlg/SimpleEnglish`](https://github.com/AminBlg/SimpleEnglish), file
`skills/simple-english/references/checklist.md`, at commit
`59bf6702197a5aadc96d197ea17f290d8d50dcd3`. Local changes make semantic preservation,
protected content, output contracts, terminology, and procedure safety authoritative.
Adapted portions are licensed under the repository MIT `LICENSE`.
