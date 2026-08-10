# Semantic preservation

Use this reference in every mode. Semantic fidelity overrides clarity, brevity,
vocabulary, sentence length, and other style guidance.

## Decision priority

Resolve conflicts in this order:

1. Technical correctness.
2. Source facts and meaning.
3. Safety information and risk level.
4. User intent and exact output contracts.
5. Certainty, permission, recommendation, and obligation.
6. Repository and product terminology.
7. Clarity and structure.
8. Mode-specific style rules.

A lower item cannot override a higher item. If strict STE guidance conflicts with a
higher priority, preserve meaning and report the unresolved style conflict.

## Build a semantic ledger before rewriting

Record each source claim and its role. Do not rely on remembering the general message.

| Preserve | Include in the ledger |
|---|---|
| Facts | Actors, actions, objects, states, results, and exclusions |
| Quantities | Numbers, dates, times, versions, percentages, units, limits, ranges, and directions of change |
| Scope | `all`, `some`, `only`, `at least`, `up to`, defaults, exceptions, and affected populations |
| Logic | Negation, comparisons, conditions, dependencies, sequence, and necessary versus sufficient conditions |
| Causality | Observed sequence, correlation, contributing factors, confirmed causes, ruled-out causes, and unknown causes |
| Evidence | Observation, inference, estimate, report, confirmation, and source attribution |
| Modality | Requirement, prohibition, recommendation, permission, capability, possibility, and uncertainty |
| Procedure | Preconditions, approvals, warnings, commands, expected results, verification, and recovery steps |
| Terms | Repository-defined concepts, product names, API names, UI labels, protocol terms, and domain terminology |

Unless the user requests a targeted factual change, every ledger item must remain
unchanged in value, scope, relationship, and semantic force.

Retain relationships, not only words. Keeping `5`, `15`, and `minutes` is insufficient
if a rewrite reverses a change from 5 minutes to 15 minutes.

## Preserve semantic force

Do not normalize modal verbs mechanically. Interpret each use in context, then retain its force.

| Source force | Typical signals | Unsafe change |
|---|---|---|
| Obligation | `must`, `required` | Weaken to recommendation or permission |
| Prohibition | `must not`, `prohibited` | Weaken to caution |
| Recommendation | `should`, `recommended` | Strengthen to obligation |
| Permission | `may`, `allowed` | Change to capability or requirement |
| Capability | `can`, `supports` | Change to permission or obligation |
| Possibility | `may`, `possible` | Make certain or impossible |
| Uncertainty | `might` | Strengthen to an unqualified possibility or certainty |
| Conditional possibility | `could` with a stated condition | Remove the condition or make the outcome certain |
| Certainty | `will`, `confirmed`, direct factual statement | Add uncertainty without evidence |
| Unknown | `unknown`, `not established`, `no evidence` | Invent an answer or imply certainty |

`May`, `might`, and `could` are not automatic synonyms. Their function depends on
context, but a rewrite must retain any difference in permission, uncertainty, or
conditionality. When that difference cannot be proved from context, preserve the source
modal instead of collapsing it into another term.

Preserve qualifiers such as `approximately`, `likely`, `possibly`, `currently`, and
`by default` when they constrain a claim. Do not add qualifiers that weaken a confirmed
requirement or fact.

## Preserve evidence and causality

Match the source's evidence level:

- `B happened after A` states sequence, not cause.
- `A correlates with B` does not mean `A caused B`.
- `Evidence suggests A` is weaker than `Evidence confirms A`.
- A confirmed cause for 73% of failures does not explain all failures.
- A ruled-out cause remains ruled out.
- An unknown cause remains unknown.

Do not fill causal gaps with plausible technical explanations. Plausibility is not source evidence.

## Preserve terminology

Repository and product terminology wins over synonym preferences and controlled-vocabulary guidance.

- Keep identifiers and exact technical names unchanged.
- Keep distinct concepts distinct. Do not merge `config`, `settings`, and `options`
  unless the source defines them as synonyms.
- Use one established term for one concept when the repository already does so.
- Do not rename an API, schema field, UI label, command, flag, or protocol term to improve prose.
- If terminology is inconsistent or undefined, report the conflict or ask which term is
  authoritative. Do not choose silently.

A technical name can remain outside an approved strict-STE vocabulary. Treat it as a
domain term and explain it in surrounding prose when useful.

## Protected content and boundaries

Unless the user explicitly requests a targeted change, preserve these items exactly:

- Fenced code, indented code, and inline code.
- Commands, flags, paths, URLs, anchors, environment variables, and version strings.
- Identifiers, type names, function names, API names, schema fields, and reference IDs.
- Product names, UI labels, protocol terms, and established repository terms.
- Quoted errors, logs, compiler diagnostics, test output, and terminal output.
- Numbers, dates, times, percentages, units, limits, and ranges.
- Complete Markdown links, including labels, destinations, containers, and occurrence counts.
- Machine-readable structure and exact output schemas.
- JSON, YAML, XML, CSV, frontmatter, templates, and schema-constrained output.

Exact preservation includes value, occurrence count, container, and semantic role. A
command copied into prose does not compensate for changing its fenced block. An old URL
added elsewhere does not compensate for changing a link destination.

If the source has an inline command, keep each occurrence inline. Do not fence it. Do not
repeat it in a heading, summary, prerequisite list, or procedure step.

Preserve delimiters, whitespace, line breaks, ordering, and formatting when tools or
output contracts can depend on them. Reformat only when the request permits it and
references, parsers, copy-paste behavior, and meaning remain intact.

Do not rewrite raw tool output. Separate commentary from output instead.

## Missing, ambiguous, or conflicting information

Never invent missing information.

- Ask a focused question when the missing value affects correctness, safety, scope, or the requested deliverable.
- If work can continue without the value, label it `unknown`, `not provided`, or `not established`, as appropriate.
- Preserve placeholders when an exact output contract requires them.
- Distinguish source conflicts from missing facts. State both conflicting values and request an authority.
- Do not infer approval, successful execution, root cause, compatibility, or safety from silence.

When the user explicitly requests a factual or protected-value change, treat that item
as editable. Recheck dependent claims and update them only when the request requires it.
Ask before proceeding if the change creates a contradiction or unsafe procedure.

## Final claim-by-claim check

Before returning a rewrite:

1. Match each assigned actor to the same responsibility in the draft.
2. Preserve the source modal verb when equivalent force is not certain.
3. Keep each factual assertion factual; do not turn it into an instruction.
4. Keep each causal threshold separate, including confirmed cause, unconfirmed cause,
   and possible contribution that evidence does not exclude.
5. Compare every source proposition with the final draft.
6. If exact force cannot be proved, retain the source clause.

## Safe rewrite workflow

1. Identify requested mode, audience, and output contract.
2. Inventory protected content as value, count, container, and role.
3. Build the semantic ledger.
4. Classify each passage as descriptive, procedural, quoted, code, or structured data.
5. Rewrite only eligible prose.
6. Compare the inventory one-to-one; reject any protected occurrence that was added, removed, duplicated, or moved.
7. Check for added claims, lost qualifiers, changed relationships, and new implications.
8. Report unresolved conflicts or unknowns instead of hiding them with fluent prose.

Semantic comparison is claim-based. Token equality alone cannot prove preservation,
and readable prose cannot excuse semantic drift.

## Coding-agent examples

### Recommendation versus requirement

Source:

> Operators should test restoration monthly. They must retain backups for 30 days.

Unsafe:

> Operators must test restoration monthly and retain backups for 30 days.

The rewrite turns a recommendation into a requirement.

Safe:

> Operators must retain backups for 30 days. Monthly restoration testing is recommended.

### Correlation versus causation

Source:

> Latency increased during the deployment. The timing shows correlation only. The root cause is unknown.

Unsafe:

> The deployment caused the latency increase.

Safe:

> Latency increased during the deployment, but no causal link is established. The root cause remains unknown.

### Repository terminology

Source:

> `config` stores file-backed values. `settings` stores UI preferences.

Unsafe:

> Configuration stores file and UI values.

Safe:

> `config` stores file-backed values, and `settings` stores UI preferences.

### Protected command

Source:

```bash
acmectl config set retry_count 3 --file /etc/acme/app.yaml
```

Unsafe:

```bash
acmectl settings set retries 4 --file /etc/acme/settings.yaml
```

Safe: keep the command unchanged and improve only the surrounding explanation.

### Destructive procedure

Source facts: confirm that snapshot `snap-2026-07-14` is complete before continuing;
deletion is permanent; recovery requires that snapshot; change request `CHG-4821` must
be approved;
run `kubectl delete namespace payments`; then check status with
`kubectl get namespace payments`.

Unsafe:

1. Run `kubectl delete namespace payments`.
2. Request approval for `CHG-4821`.
3. Create a snapshot if recovery is necessary.

Safe:

1. Confirm that snapshot `snap-2026-07-14` is complete.
2. Put the permanent-deletion and recovery warning before the command.
3. After change request `CHG-4821` is approved, run
   `kubectl delete namespace payments`.
4. Check the status with `kubectl get namespace payments`.

### Missing information

Source:

> The remaining failures have no confirmed cause.

Unsafe:

> Database contention caused the remaining failures.

Safe:

> The cause of the remaining failures is unknown.

## Reporting conflicts

When meaning blocks a requested style rule, report:

- Protected source wording or claim.
- Conflicting style rule.
- Semantic risk of applying it.
- Safe retained wording or focused question.

This package, its linter, model output, and review process cannot certify ASD-STE100
compliance. For every compliance-oriented audit, include this disclaimer:

> This audit is advisory and cannot certify ASD-STE100 compliance. Final approval rests
> with the writer using the official standard and dictionary.

Do not claim that linter success proves semantic correctness. Deterministic checks cover
enumerated properties only; open prose requires source comparison and human or attested
semantic review.
