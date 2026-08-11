# pi-ste-writing

Technical-writing support for [Pi](https://pi.dev). Package helps Pi rewrite repository documentation while preserving commands, values, links, identifiers, requirement levels, and technical meaning.

Pi package gallery lists [`pi-ste-writing`](https://pi.dev/packages/pi-ste-writing). Installed skill name is `clear-technical-writing`.

> [!WARNING]
> Pi packages run with full user permissions. Model-facing `writing_begin` stores source text in session tool-result details so checks survive session restore and branching. Saved sessions and trusted extensions or RPC consumers can access that text. Do not use it on secrets. Checks are advisory and do not prove semantic equivalence or certify ASD-STE100 compliance.

Package is experimental pre-1.0 software.

## Use

Rewrite one repository document:

```text
/ste_doc README.md
```

Paths with spaces can be quoted:

```text
/ste_doc "docs/installation guide.md"
```

`/ste_doc` starts a normal Pi task. Pi keeps `read`, `edit`, `write`, `bash`, and third-party tools available, injects a compact preservation checklist, edits only target file, and checks its changes before returning. Generated task stays hidden in chat transcript and does not embed full skill or reference files.

No other package-specific command is required.

## Automatic use

Skill can also load automatically when request asks Pi to create, write, edit, improve, rewrite, or audit technical prose such as:

- READMEs and documentation.
- API and CLI help.
- Runbooks and procedures.
- Incident reports and root-cause analyses.
- Error explanations and release notes.
- Explicit STE audits.

Automatic routing is model-dependent. `/ste_doc <path>` gives deterministic file-rewrite entry point. Pi's standard `/skill:clear-technical-writing` command remains available for custom prompts.

## Model workflow

When writing workflow activates, extension adds two model-facing tools. Users do not need to call them.

1. Pi reads target and repository guidance.
2. `writing_begin` captures baseline before first mutation.
3. Pi edits with normal repository tools.
4. `writing_check` compares current file with baseline.
5. Pi repairs unintended changes and reruns check.

### `writing_begin`

Captures:

- Canonical target path.
- Clear, procedure, or strict mode.
- Existing-file or new-file state.
- Raw-byte SHA-256.
- Strict UTF-8 source text.

Visible result stays compact. Source and hashes remain in session details. Tool rejects non-UTF-8 files and files larger than 2 MiB.

### `writing_check`

Returns one compact visible line:

- `clean`, `unchanged`, or `needs-review` status.
- Up to three affected source and current locations, grouped by line so overlapping detectors do not repeat one edit.
- Introduced finding count and up to three rule locations.
- Direct diff-review, repair, and rerun instruction.

Session details retain hashes and bounded structured deltas for provenance and branch restoration. Pi does not send these details to model. Visible output omits protected values, hashes, repeated detector results, and disclaimers.

Tool never blocks, rewrites, or reverts file. Protected change can be intentional when request targets version, command, URL, label, identifier, requirement level, or other protected value. Pi must judge each delta against user request.

`writing_check` never guesses baseline from Git or current text. Missing baseline returns `no-snapshot`.

## What checks cover

Protected-content comparison recognizes occurrence counts and Markdown containers for:

- Fenced, indented, and inline code.
- Link destinations and labels.
- Quoted diagnostics and bare URLs.
- Numbers, versions, times, percentages, units, and ranges.
- Paths, CLI flags, environment variables, and JSON keys.
- Recognized identifiers and bold labels.
- Modal phrases such as `must`, `must not`, `should`, `can`, `cannot`, `may`, `might`, and `could`.

Writing findings include bounded procedure and strict-mode heuristics. Baseline comparison separates introduced findings from existing warnings.

Checks do not prove preserved causality, factual completeness, actor roles, arbitrary semantic equivalence, procedure safety, or complete terminology fidelity. Pi still compares source and result claim by claim.

## Modes

### Clear

Default. Concise, complete prose and active voice for known actors. No hard vocabulary or sentence limits.

### Procedure

Conditions before controlled actions, warnings before dangerous actions, and verification after actions. Detected instructions use a 20-word target.

### Strict STE

Only for explicit STE or compliance-audit requests. Adds STE-oriented sentence and style checks. Complete vocabulary review requires official ASD-STE100 Issue 9 dictionary, which package does not include.

## Install

Review package source before installation.

From npm:

```bash
pi install npm:pi-ste-writing@0.1.0
```

From pinned Git tag after publication:

```bash
pi install git:github.com/stijnVanHorenbeek/pi-ste-writing@v0.1.0
```

Install project-local package by adding `-l`:

```bash
pi install git:github.com/stijnVanHorenbeek/pi-ste-writing@v0.1.0 -l
```

Try published tag for one Pi run:

```bash
pi -e git:github.com/stijnVanHorenbeek/pi-ste-writing@v0.1.0
```

For local development:

```bash
pi install /absolute/path/to/pi-ste-writing
```

Inspect installed packages with `pi list`. Use `pi config` or `pi config -l` to disable package resources. Remove npm installation with:

```bash
pi remove npm:pi-ste-writing
```

## Troubleshooting

### `/ste_doc` is missing

- Confirm package extension is enabled.
- Run `pi list` and inspect package source.
- Check startup diagnostics for extension errors.

### Writing tools are missing during automatic use

- Confirm skill loaded in current session.
- Use `/ste_doc <path>` for deterministic file work.
- Use Pi's standard `/skill:clear-technical-writing <task>` for custom tasks.

### `writing_check` reports `no-snapshot`

Pi must call `writing_begin` after reading and before mutation. Tool does not reconstruct source from Git.

### `writing_check` reports `needs-review`

Pi should inspect exact removed and added values. Requested changes can be intentional. Unrequested changes should be repaired before delivery.

## Development

Requires Node.js `>=22.19.0`, npm, and Git.

```bash
npm install --ignore-scripts
npm run typecheck
npm test
npm run check
npm pack --dry-run --json
```

Product checks cover TypeScript analysis, model-visible tool output, dynamic activation, session restoration, real Pi SDK activation, isolated command discovery, and package contents.

## Package layout

```text
extensions/writing-advisor.ts      `/ste_doc` and model-facing session tools
extensions/writing-analysis.ts     TypeScript linter and protected verifier
extensions/writing-snapshots.ts    UTF-8 snapshots and session restoration
skills/clear-technical-writing/    Writing guidance and references
docs/writing-tools.md              Tool contracts and limitations
tests/                             Product-focused TypeScript tests
```

## Provenance, trademark, and limits

Project adapts [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) at commit [`59bf670`](https://github.com/AminBlg/SimpleEnglish/commit/59bf6702197a5aadc96d197ea17f290d8d50dcd3), licensed under MIT License.

ASD-STE100 is registered trademark of ASD. Project is not affiliated with ASD, STEMG, or AminBlg. None of those organizations endorses it. Package does not include official ASD-STE100 dictionary and cannot certify ASD-STE100 compliance.

## License

MIT. See [`LICENSE`](LICENSE).
