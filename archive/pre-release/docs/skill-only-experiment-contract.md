# Archived skill-only experiment contract

Historical internal label: `V1`. This label identified design generation, not package release.

> [!NOTE]
> Frozen pre-release contract. Skill-only experiment failed acceptance gates and was never published. Current guarded candidate is specified in [`docs/guarded-verifier-contract.md`](../../../docs/guarded-verifier-contract.md); it does not rewrite this evidence.

Status: approved implementation baseline

Package working name: `pi-ste-writing`

Primary skill name: `clear-technical-writing`

## 1. Purpose

V1 provides a Pi-native skill for human-facing technical prose. It improves clarity without changing technical meaning.

The package adapts useful ASD-STE100 practices for software documentation. It does not make normal Pi coding conversations conform to strict Simplified Technical English (STE).

## 2. Upstream pin and provenance

| Field | Value |
|---|---|
| Project | `AminBlg/SimpleEnglish` |
| Repository | `https://github.com/AminBlg/SimpleEnglish` |
| Reviewed commit | `59bf6702197a5aadc96d197ea17f290d8d50dcd3` (`59bf670`) |
| Upstream skill version | `1.2.0` |
| License | MIT |
| Standard referenced upstream | ASD-STE100 Issue 9 (2025-01-15) |
| Review date | 2026-08-09 |

V1 is a derivative adaptation, not an upstream mirror. Package documentation must identify the repository and reviewed commit. Adapted source files must retain applicable MIT attribution.

ASD-STE100 is a registered trademark of ASD. This package is not affiliated with ASD, STEMG, or the upstream project. It cannot certify text as ASD-STE100 compliant.

## 3. Decision priority

Apply requirements in this order:

1. Preserve technical correctness.
2. Preserve source facts and meaning.
3. Preserve safety information and risk level.
4. Preserve user intent and explicit output contracts.
5. Preserve certainty, permission, recommendation, and obligation.
6. Preserve repository and product terminology.
7. Improve clarity and structure.
8. Apply mode-specific style rules.

A lower-priority rule must not override a higher-priority rule.

Examples:

- Do not change `should` to `must` when the source gives a recommendation.
- Do not change `may fail` to `fails` or `will fail`.
- Do not replace `settings` with `config` when both are distinct product concepts.
- Do not simplify a warning if simplification changes its risk level or trigger condition.

## 4. V1 scope

### 4.1 Included deliverables

V1 includes:

- An explicit Pi package manifest that exposes only skill resources.
- One Pi skill named `clear-technical-writing`.
- A lean `SKILL.md` router.
- References for semantic preservation, strict STE rules, verification, and coding-focused use cases.
- A dependency-free advisory linter where practical.
- Unit and regression tests.
- Deterministic semantic evaluation metrics.
- A reproducible Pi benchmark runner.
- Installation, usage, attribution, and limitation documentation.

### 4.2 Included default targets

The skill can activate automatically for requests that create, rewrite, or audit:

- Documentation and READMEs.
- API guides.
- Setup procedures and runbooks.
- User-facing error messages and CLI help.
- Incident reports and postmortems.
- Release notes and changelogs.
- Translation-ready technical prose.

### 4.3 Excluded default contexts

The skill must not activate automatically for:

- Code review findings.
- Debugging hypotheses.
- Architecture analysis or design tradeoffs.
- Test-result interpretation.
- Patch summaries unless the user asks for a writing pass.
- Raw tool output.
- Logs and quoted diagnostics.
- Structured JSON, XML, YAML, CSV, or schema-constrained output.
- Source code and generated code.
- Marketing, brand, or editorial voice.

Exact user invocation can override these activation exclusions when the requested transformation remains safe.

### 4.4 V1 non-goals

V1 does not include:

- An always-on Pi output style.
- A global `AGENTS.md` rule set.
- Prompt templates that duplicate the skill.
- A persistent `/ste` mode extension.
- Automatic rewriting of assistant messages after generation.
- The copyrighted ASD-STE100 dictionary.
- Certification or claims of full ASD-STE100 compliance.
- Automatic publication to npm, Git, or the Pi package gallery.

Persistent mode remains a separate V2 decision.

## 5. Supported modes

### 5.1 Clear mode

Clear mode is the default.

It must:

- Preserve semantics and established terminology.
- Prefer concise, complete sentences.
- Prefer active voice when the actor is known.
- Remove filler only when no information is lost.
- Separate findings, evidence, actions, and risks when useful.
- Keep uncertainty and obligation words when they carry meaning.

It must not enforce the full STE vocabulary or hard sentence limits.

### 5.2 Procedure mode

Procedure mode applies to instructions, runbooks, recovery steps, and destructive operations.

It must:

- Use imperative instructions where appropriate.
- Put action-controlling conditions before commands.
- Use one action per numbered step unless actions must occur together.
- Put warnings before dangerous actions.
- State the required action before the possible consequence.
- Target 20 words or fewer per instruction when this does not damage meaning.

The condition-first rule applies to procedural commands. It does not apply to every descriptive `if` or `when` clause.

### 5.3 Strict STE mode

Strict mode activates only when the user explicitly requests STE, ASD-STE100, or compliance-oriented auditing.

It must:

- Load the full local STE rule reference and verification checklist.
- Apply 20-word procedural and 25-word descriptive limits.
- Apply strict verb, sentence, terminology, and writing-practice rules where higher-priority requirements permit.
- Preserve domain terms as technical names.
- Report unresolved conflicts instead of changing meaning.
- Include the no-certification disclaimer in compliance-oriented audit output.

## 6. Protected content

Unless the user explicitly requests a targeted change, preserve these items exactly:

- Fenced code and inline code.
- Identifiers, type names, function names, API names, and schema fields.
- Commands, flags, file paths, URLs, and environment variables.
- Product names, UI labels, protocol terms, and established repository terminology.
- Quoted errors, logs, compiler output, and test output.
- Numbers, dates, versions, percentages, units, limits, and ranges.
- Markdown link destinations, reference identifiers, and anchors.
- Machine-readable structure and exact output schemas.

Formatting can change only when the request permits it and the change does not break references or tooling.

## 7. Skill size and progressive disclosure budget

The lean `SKILL.md` must route work instead of reproducing the full rule catalog.

Acceptance limits:

- Target size: 4,000 to 5,500 UTF-8 bytes, including frontmatter.
- Hard maximum: 6,000 UTF-8 bytes.
- Estimated model budget: approximately 1,000 to 1,500 tokens, depending on tokenizer.
- No complete 53-rule table in `SKILL.md`.
- Strict rules, large examples, and detailed checks belong in references.
- The automatic activation description must remain narrow and below Pi's 1,024-character limit.

Byte limits are the deterministic gate. Token figures are planning estimates because tokenizers differ by model.

## 8. Upstream inventory

### 8.1 Material to adapt

| Upstream path or section | V1 destination | Treatment |
|---|---|---|
| `skills/simple-english/SKILL.md` — pragmatic/strict modes | `SKILL.md` and `references/ste-rules.md` | Adapt. Keep explicit modes, but make semantic preservation authoritative. |
| `skills/simple-english/SKILL.md` — procedural/descriptive classification | `SKILL.md` and rule reference | Adapt. Permit mixed documents with separately classified passages. |
| `skills/simple-english/SKILL.md` — rule catalog | `references/ste-rules.md` | Adapt with attribution. Keep real rule numbers and strict-mode scope. |
| `skills/simple-english/SKILL.md` — vocabulary discipline | `references/ste-rules.md` | Restrict to strict mode. Repository terminology wins. |
| `skills/simple-english/SKILL.md` — Untouchables | `SKILL.md` and semantic reference | Expand to APIs, schema fields, UI labels, exact output contracts, and Markdown targets. |
| `skills/simple-english/SKILL.md` — self-check | `references/checklist.md` | Reorder. Semantic and protected-content checks come before style checks. |
| `skills/simple-english/SKILL.md` — limits and disclaimer | `SKILL.md` and README | Retain and expand Pi-specific scope limits. |
| `skills/simple-english/references/checklist.md` | `references/checklist.md` | Adapt. Remove the global every-`if`/`when` assumption. |
| `skills/simple-english/references/use-cases.md` | `references/use-cases.md` | Adapt with coding-agent cases and fact-preserving examples. |
| `evals/pressure-tests.md` | Regression fixtures and scenario design | Adapt the pressure-test method. Add semantic and coding-agent pressure cases. |
| `evals/ste_lint.py` | `scripts/ste_lint.py` | Adapt with attribution. Rewrite classification, protected-span, and exit behavior. |
| `evals/run_pi_bench.py` | V1 Pi benchmark runner | Adapt resumable execution and reporting structure. Add native skill loading and repetitions. |
| `evals/test_run_pi_bench.py` | Benchmark tests | Adapt relevant parser and aggregation tests. |
| `LICENSE` | `LICENSE` | Copy under MIT terms. |

### 8.2 Material to use only as evidence

| Upstream path | Treatment |
|---|---|
| `evals/results/**` | Historical evidence only. Do not present as V1 performance. |
| `examples/before-after.md` | Use as review evidence and fixture inspiration. Do not copy examples that lack visible source-fidelity proof. |
| `README.md` benchmark claims | Cite only when describing upstream. Do not inherit claims for the adapted package. |
| `evals/scenarios.json` | Replace fictional prose-only matrix with coding-agent scenarios. |
| `evals/run_bench.py` | Use judge-method ideas only. Do not carry Claude-specific runner code into V1 unless required. |

### 8.3 Material rejected from V1

| Upstream path or behavior | Reason |
|---|---|
| `output-styles/simple-english.md` | Claude-specific and always-on. Scope is unsafe for normal Pi coding work. |
| `prompts/system-prompt.md` | Duplicates skill instructions and creates persistent prompt cost. |
| `.claude-plugin/**` | Claude plugin metadata has no V1 Pi role. |
| Global modal replacement | Can change certainty, obligation, recommendation, and permission. |
| Global synonym collapse | Can merge distinct repository or product concepts. |
| Global condition-first enforcement | Valid only for action-controlling procedural conditions. |
| Automatic strict sentence limits | Can damage precise coding explanations. Strict limits require explicit strict mode. |
| Full rule catalog in the primary skill file | Violates progressive-disclosure and prompt-budget goals. |

## 9. V1 acceptance evidence

V1 is complete only when all required evidence exists.

### 9.1 Package and Pi discovery

- `package.json` exposes only `./skills` through the `pi` manifest.
- Pi discovers exactly one package skill: `clear-technical-writing`.
- `/skill:clear-technical-writing` accepts task arguments.
- Relative references and linter script paths resolve from the skill directory.
- No prompt template, extension, or output style loads from the package.
- Temporary, global, project-local, disable, and removal flows are documented and smoke-tested.

### 9.2 Activation and mode behavior

A committed activation fixture file must define fixed positive and negative prompts before prompt tuning starts.

Positive fixtures must cover documentation, a procedure, a user-facing error, release notes, and an explicit strict STE audit. Negative fixtures must cover code review, debugging, architecture analysis, raw tool output, and schema-constrained structured output.

Acceptance gates:

- Explicit `/skill:clear-technical-writing` invocation routes to the skill in every test.
- For each model in the preregistered V1 matrix, each automatic-activation fixture runs three times.
- Each positive automatic fixture routes to the skill in at least two of three runs.
- No negative fixture routes to the skill in any run.
- Routing is verified from Pi JSON session events or transcripts, not inferred from prose style.
- Clear-mode fixtures preserve semantic gates and do not apply strict-only vocabulary substitutions.
- Procedure-mode fixtures mechanically verify condition placement, action ordering, and warning placement.
- Strict-mode fixtures mechanically verify the applicable 20-word and 25-word limits and record unresolved semantic conflicts.

These checks prevent an inert or globally active skill from passing V1.

### 9.3 Semantic regression gates

Closed-world fixtures must enumerate required facts, allowed claims, forbidden claims, protected spans, protected terms, and required modality.

Across every native-skill closed-world fixture output in the preregistered V1 matrix:

- Protected-span equality: 100%.
- Required enumerated fact retention: 100%.
- Enumerated forbidden claims: zero.
- Modality, certainty, permission, recommendation, and obligation preservation: 100%.
- Protected repository terminology preservation: 100%.
- Exact output-contract violations: zero.

Open-prose samples also require an attested semantic review. The reviewer must compare each new factual claim with the supplied source. An unsupported or unreviewed claim blocks V1.

Any native-skill semantic failure blocks V1 regardless of readability, linter, or preference scores. Baseline and direct-prompt failures remain authoritative evidence for those outputs and stay visible in reports, but they do not veto package acceptance.

### 9.4 Linter and metric tests

- All linter and deterministic metric tests pass.
- Tests include Markdown, mixed passage types, false-positive cases, and malformed prose that the upstream regex linter missed.
- CLI errors return nonzero.
- Advisory findings do not return nonzero by default.
- Reports never claim certification or compliance.

### 9.5 Benchmark evidence

- `evals/v1-matrix.json` is committed before benchmark prompt tuning begins.
- The matrix fixes scenario IDs, conditions, providers, model IDs, thinking levels, and repetition counts.
- A matrix change requires a versioned amendment with a recorded reason. Existing raw results cannot be silently reused after that change.
- Baseline and adapted conditions use the same task inputs.
- Native Pi skill loading is tested separately from direct prompt injection.
- Every matrix cell has at least three successful samples per condition and model.
- Every completed output is included in aggregation. Invocation failures and exhausted retries remain visible.
- Missing cells or unresolved failures make the matrix incomplete and block a final benchmark claim.
- Results report semantic metrics before style metrics.
- Input tokens, provider-reported reasoning-token metadata, output tokens, cost, duration, failures, and variance are reported when available.
- Unavailable provider metadata is stored as `null` with an availability field. Missing optional metadata does not fail a run.
- Hidden reasoning content is never requested or stored.
- Raw outputs, runner version, Pi version, model identifiers, thinking levels, and package commit are recorded.
- Judge preference cannot override a deterministic or attested semantic failure.

### 9.6 Documentation and legal evidence

- README documents purpose, non-goals, modes, installation, removal, explicit invocation, automatic activation, linter use, and cost tradeoffs.
- MIT license is present.
- README identifies `AminBlg/SimpleEnglish@59bf670` as upstream source.
- An upstream inventory maps every substantially copied or adapted file to its source path and commit.
- Substantially adapted code and rule references include a concise provenance note where the file format permits it.
- Adapted Python files retain applicable MIT attribution in file headers.
- ASD/STEMG non-affiliation and no-certification wording is present.
- Publishing remains outside V1 completion and requires explicit user approval.

## 10. Assumptions and open boundaries

The following assumptions are accepted for V1:

- English is the only authored language.
- Python 3 is available when the optional linter or evaluation suite runs.
- The writing skill itself has no runtime dependency.
- Strict STE vocabulary remains incomplete without the official dictionary.
- Model token counts vary, so byte size is the stable prompt-budget gate.
- Automatic skill activation is probabilistic. Explicit `/skill:clear-technical-writing` invocation is the deterministic path.

Changes to these assumptions require an acceptance-contract update before implementation expands scope.
