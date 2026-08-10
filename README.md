# pi-ste-writing

Semantics-first technical-writing skill for [Pi](https://pi.dev). It rewrites or audits human-facing technical prose while keeping technical correctness, source facts, safety, modality, terminology, and exact values ahead of style.

> [!WARNING]
> `0.0.1` is an experimental prerelease. Use guarded mode when protected-content enforcement matters, and review high-risk output against its source. This package does not prove semantic equivalence or certify ASD-STE100 compliance.

## What it provides

Package provides:

- Progressively loaded `clear-technical-writing` skill.
- Opt-in `/clear-write` Pi extension for guarded rewrites.
- **Clear:** concise technical prose without strict STE vocabulary or sentence limits.
- **Procedure:** actionable instructions with conditions and warnings in safe order.
- **Strict STE:** explicit STE-oriented review after semantic checks pass.
- Advisory Python linter for writing checks.
- Deterministic Python verifier for protected occurrence counts and containers.

Package does not load prompt template, theme, output style, global instruction, or persistent writing mode. Extension stays idle until `/clear-write` invocation.

## Install

Pi packages can execute arbitrary code. This package extension creates temporary files and runs package-owned Python verifier. Review package source before installation. Python 3 is required for guarded rewrites.

### npm installation

Install pinned experimental version for all Pi projects:

```bash
pi install npm:pi-ste-writing@0.0.1
```

### Git installation

Install from GitHub:

```bash
pi install git:github.com/stijnVanHorenbeek/pi-ste-writing@v0.0.1
```

Pin any tag or commit for reproducibility:

```bash
pi install git:github.com/stijnVanHorenbeek/pi-ste-writing@<tag-or-commit>
```

Inspect installed packages:

```bash
pi list
```

### Project-local installation

From the project root, install the pinned version into `.pi/settings.json`:

```bash
pi install git:github.com/stijnVanHorenbeek/pi-ste-writing@v0.0.1 -l
```

Review and trust project-local files before loading them. Pi installs missing project packages after project trust is granted. If Pi reports that project is untrusted, review files first, then approve that command explicitly:

```bash
pi install git:github.com/stijnVanHorenbeek/pi-ste-writing@v0.0.1 -l --approve
```

### Temporary use

Load the pinned package for one Pi run without changing settings:

```bash
pi -e git:github.com/stijnVanHorenbeek/pi-ste-writing@v0.0.1
```

For local development, replace Git source with package checkout path:

```bash
pi install /absolute/path/to/pi-ste-writing
```

## Use

### Automatic activation

Pi always sees the short skill name and description. The model loads full `SKILL.md` only when the request matches. Automatic activation targets requests to create, rewrite, or audit:

- Documentation and READMEs.
- API guides.
- Setup procedures and runbooks.
- User-facing errors and CLI help.
- Incident reports and postmortems.
- Release notes and changelogs.
- Translation-ready technical prose.

Automatic activation is model-dependent. Use explicit command when activation must be deterministic.

### Explicit activation

In interactive Pi:

```text
/skill:clear-technical-writing Rewrite this API guide for clarity. Preserve commands, identifiers, links, values, and requirement levels.
```

Arguments after command become skill task. Explicit invocation can request writing work in normally excluded contexts, but cannot authorize semantic drift, unsafe action ordering, or unrequested protected-content changes.

### Guarded rewrite

Use the verifier when protected occurrence counts and containers must be gated:

```text
/clear-write --mode procedure
Before maintenance, run `kubectl drain node-17 --ignore-daemonsets`.
Record ticket `OPS-6634` once.
```

Modes: `clear`, `procedure`, and `strict`; default is `clear`. Source can follow mode on same line. With no source argument in interactive Pi, command opens editor.

The extension owns the source snapshot. The model submits the job ID and draft to the terminating `submit_clear_rewrite` tool. The verifier rejects protected-content drift and permits up to three submissions. An invalid draft is never accepted output.

Guard checks recognized literal occurrence counts and structural Markdown containers for code, links, bold text, quoted diagnostics, URLs, numeric values, paths, flags, environment variables, JSON keys, and recognized identifiers. Ordered-list markers are structural, not protected numeric facts. Guard does not verify semantic role or relationship between preserved values.

Guard acceptance is not proof of full semantic equivalence. It cannot mechanically verify every fact, modality, causal statement, unknown-root-cause statement, procedure ordering, or domain term. Review high-risk output against source.

TUI, JSON, and RPC expose accepted draft as tool result. Print mode emits accepted draft as final assistant text. Provider streaming can show unverified deltas before finalized direct output is blocked; only accepted artifact carries verifier result.

### Clear mode

Clear mode is default:

```text
Rewrite this release note for clarity. Preserve every fact, qualifier, number, and degree of certainty.

Source:
The deployment may reduce latency, but tests have not confirmed the effect.
```

Clear mode does not enforce full STE vocabulary or hard sentence limits.

### Procedure mode

Ask for procedure or runbook rewrite:

```text
Rewrite this setup procedure. Put warnings before dangerous commands, action-controlling conditions before commands, and verification after each action. Preserve commands exactly.

Source:
...
```

Procedure mode prefers one action per numbered step. It targets 20 words or fewer only when shorter text preserves meaning and safe order.

Standalone destructive-operation or security-warning text does not auto-activate. Invoke skill explicitly for that work.

### Strict STE mode

Strict mode requires explicit STE, ASD-STE100, or compliance-audit request:

```text
/skill:clear-technical-writing Audit this maintenance procedure in strict STE mode. Preserve technical meaning and report unresolved conflicts.
```

Strict mode loads local rule map and checklist. Complete vocabulary review still requires official ASD-STE100 Issue 9 dictionary, which package does not include. Compliance-oriented audits must include no-certification disclaimer.

## Semantic-preservation contract

Skill applies this priority order:

1. Technical correctness.
2. Source facts and meaning.
3. Safety and risk level.
4. User intent and exact output contract.
5. Certainty, permission, recommendation, and obligation.
6. Repository and product terminology.
7. Clarity and structure.
8. Mode-specific style.

Unless user requests targeted change, skill preserves code, identifiers, commands, flags, paths, URLs, environment variables, product terms, quoted output, numbers, dates, versions, units, ranges, link destinations, reference IDs, anchors, and machine-readable schemas. Protected values retain occurrence count, container, and semantic role.

These safeguards reduce known failure modes; they do not prove arbitrary prose equivalence. Review high-risk or open-ended model output against source. Deterministic fixtures cover declared properties only. Guarded path adds mechanical enforcement for recognized protected occurrences; it does not weaken or replace this semantic contract.

## Default exclusions

Skill does not auto-activate for:

- Code review findings or debugging hypotheses.
- Architecture analysis or design tradeoffs.
- Test-result interpretation or patch summaries without writing-pass request.
- Raw tool output, logs, or quoted diagnostics.
- JSON, XML, YAML, CSV, or schema-constrained output.
- Source or generated code.
- Marketing, brand, or editorial voice.

Complete technical reasoning first. Apply skill only to requested human-facing prose.

## Protected-content verifier

Guarded extension runs verifier automatically. Direct CLI use:

```bash
python3 skills/clear-technical-writing/scripts/protected_verify.py \
  --source source.md \
  draft.md
```

Exit 0 means recognized protected occurrence counts and containers match. Exit 1 means mismatch. Other failures indicate verifier infrastructure error. JSON report is written to stdout. Verifier imports bundled `ste_lint.py`; no third-party Python package is required.

Mechanical success does not prove arbitrary semantic equivalence or ASD-STE100 compliance.

## Advisory linter

Python 3 linter has no third-party dependencies. Run from repository checkout:

```bash
python3 skills/clear-technical-writing/scripts/ste_lint.py \
  --mode clear \
  --source source.md \
  draft.md
```

Modes: `clear`, `procedure`, `strict`. Output formats: `text` and `json`.

```bash
python3 skills/clear-technical-writing/scripts/ste_lint.py \
  --mode procedure \
  --format json \
  --source source.md \
  draft.md
```

Findings are advisory and normally exit 0. Use `--strict-gate` only when any finding must produce exit 1:

```bash
python3 skills/clear-technical-writing/scripts/ste_lint.py \
  --mode strict \
  --strict-gate \
  draft.md
```

Zero warnings do not prove semantic correctness or ASD-STE100 compliance.

## Context and cost

Progressive loading limits normal prompt cost:

1. Short skill description is available at Pi startup.
2. `SKILL.md` loads only after activation.
3. Semantic reference loads for source-based rewrites and audits.
4. Use-case, checklist, and strict-rule references load only when needed.

Activated work consumes additional input tokens. Strict audits and high-risk procedures load the most context. Explicit skill invocation improves routing reliability with the same loaded-context cost. Guarded invocation loads the skill and semantic-preservation guidance. Repairs can add model turns and cost. The local linter and verifier make no provider calls.

## Disable, remove, and update

Disable all discovered skills for one run:

```bash
pi --no-skills
```

`--no-skills` disables discovery; explicit `--skill <path>` still loads named path.

Use `pi config` to disable installed skill globally. Use project-local view for project overrides:

```bash
pi config
pi config -l
```

Disabling `clear-technical-writing` stops automatic and explicit skill use but does not disable `/clear-write`. Package filters can disable resources independently. Example keeps skill and disables extension:

```json
{
  "packages": [
    {
      "source": "git:github.com/stijnVanHorenbeek/pi-ste-writing",
      "extensions": []
    }
  ]
}
```

Remove an npm installation:

```bash
pi remove npm:pi-ste-writing
```

Remove a Git installation:

```bash
pi remove git:github.com/stijnVanHorenbeek/pi-ste-writing
```

Remove a project-local Git installation:

```bash
pi remove git:github.com/stijnVanHorenbeek/pi-ste-writing -l
```

For an untrusted project, append `--approve` only after reviewing project-local files.

Update an unpinned package:

```bash
pi update --extensions
```

Pinned npm versions and Git refs do not move during update. Install the new version or ref explicitly.

## Troubleshooting

### Skill command is missing

- Run `pi list` and confirm package source.
- Confirm skill commands are enabled in Pi settings (`enableSkillCommands`).
- Check startup warnings for duplicate skill name; Pi keeps first discovered skill.
- For project install, confirm project is trusted and command runs inside project scope.

### Automatic activation did not occur

Automatic routing is probabilistic. Use:

```text
/skill:clear-technical-writing <task>
```

### Skill activates in unwanted work

- Start Pi with `--no-skills` for one run.
- Disable skill with `pi config` or `pi config -l`.
- Remove package from correct global or project scope.

### Guarded rewrite fails

- Confirm Python 3 is available as `python3`.
- Check extension is enabled in package filters.
- Keep source in same `/clear-write` invocation; guarded jobs are one-shot and not restored across reload/session changes.
- Treat blocked or verifier-error result as no accepted rewrite.

### Linter command fails

- Confirm Python 3 is available.
- Run command from repository checkout or resolve script relative to installed skill directory.
- Pass `-` or omit path to read draft from standard input.
- Remember `--source` expects source file path, not inline text.

## Evaluation summary

Before `0.0.1`, full development repository validation passed 266 Python tests, eight Node tests, Python compilation, package dry run, and diff checks. Benchmark machinery and raw evidence were then removed from release tree and retained in ignored local archive; tracked history through commit `a4c6758` preserves prior evidence.

Latest broader guarded probe used five known prose scenarios, three repetitions, and three OpenAI configurations:

| Configuration | Cells | Accepted on first verifier submission | Reported cost | Mean latency |
|---|---:|---:|---:|---:|
| `gpt-5.6-sol:high` | 15/15 | 14/15 | $0.476795 | 15.58 s |
| `gpt-5.6-sol:low` | 15/15 | 15/15 | $0.367700 | 9.78 s |
| `gpt-5.4-mini:high` | 15/15 | 14/15 | $0.103020 | 18.61 s |

Across all 45 cells, objective protected contracts, output contracts, correlated guard integrity, model identity, and routing safety passed 45/45. Procedure contracts passed 9/9. Every call succeeded on its first provider-level attempt. Two drafts required one bounded verifier repair; neither repeated unchanged rejected text.

Limits: the scenarios were known development regressions, not held-out evidence. Historical release candidates remain failed. Planned final held-out generation and blind semantic judging did not complete after non-candidate author and reviewer capacity became unavailable. These results support experimental guarded-path use only. They do not establish arbitrary semantic equivalence, population reliability, or certification.

## Package layout

```text
extensions/                      Opt-in guarded-rewrite Pi extension
skills/clear-technical-writing/  Pi skill, references, linter, and verifier
tests/                           product-focused deterministic regressions
docs/                            Guarded-verifier contract
```

See [`docs/guarded-verifier-contract.md`](docs/guarded-verifier-contract.md). Historical benchmark material is omitted from release tree.

## Upstream, trademark, and limits

Project adapts [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) at commit [`59bf670`](https://github.com/AminBlg/SimpleEnglish/commit/59bf6702197a5aadc96d197ea17f290d8d50dcd3), licensed under MIT License.

ASD-STE100 is a registered trademark of ASD. Project is not affiliated with ASD, STEMG, or AminBlg. None of those organizations endorses it. Package does not include official ASD-STE100 dictionary and cannot certify ASD-STE100 compliance.

## License

MIT. See [`LICENSE`](LICENSE).
