# Guarded protected-content verifier contract

Status: release candidate, experimental, unpublished, and not release evidence.

Candidate package version: `0.1.0-rc.1`

This contract defines current package shape: progressively loaded writing skill plus opt-in Pi extension. It supersedes skill-only experimental package shape without rewriting archived pre-release contracts or failed benchmark evidence.

## Purpose

Model instructions alone did not reliably preserve protected occurrence counts and Markdown containers. Guarded rewrite path accepts draft only after deterministic protected-content verification of those properties.

Skill semantic-safety contract remains in force. Verifier acceptance does not prove arbitrary semantic equivalence, factual completeness, causal correctness, procedure safety, or ASD-STE100 compliance.

## Invocation

```text
/clear-write [--mode clear|procedure|strict] <source>
```

Source can follow mode on same line or next line. If interactive invocation has no source argument, Pi opens source editor. Non-interactive invocation requires inline source.

Command is explicit and one-shot. It does not enable persistent writing mode or change automatic skill routing.

## Trust boundary

- Extension captures source before model generation.
- Source remains extension-owned for one guarded job.
- Model receives opaque job ID and source text.
- Submit tool accepts only job ID and draft. It cannot replace source or expected inventory.
- Exactly one submit tool call, with no assistant prose or sibling tool call, is eligible for verification.
- Stale, replayed, mixed, duplicate, or cross-job submissions fail closed.
- State clears after acceptance, rejection limit, direct-output bypass, verifier failure, agent settlement, tree navigation, reload, session replacement, or shutdown.

## Deterministic gate

Package-owned `protected_verify.py` reuses protected-span extraction from advisory linter. It compares occurrence multisets by protected kind and structural Markdown container.

Current inventory includes:

- Inline and block code.
- Markdown link destinations and labels.
- Markdown bold text, including formatted UI labels.
- Quoted diagnostic blocks.
- Bare URLs.
- Numeric values, excluding ordered-list markers.
- Filesystem paths.
- CLI flags.
- Environment variables.
- JSON keys.
- Uppercase and CamelCase identifiers recognized by deterministic pattern.

Structural containers are flow text, heading level, and blockquote. Lists and tables count as flow so safe procedure restructuring can pass. Protected kind remains part of container identity, so inline-to-block and link-to-bare moves fail. Occurrence order and semantic role are not mechanically verified.

Verifier permits up to three candidate submissions. Failed candidate text is not returned as accepted output. Guard retains only SHA-256 of previous rejected draft for duplicate detection. An unchanged rejected draft receives explicit instruction to change draft before resubmission; duplicate detection does not reset or extend submission budget. Third protected-content mismatch ends guarded job with blocked result.

Python 3 is required. Verifier imports bundled `ste_lint.py`; no third-party Python package is required. Missing interpreter, timeout, malformed report, unexpected exit, and status/report disagreement fail closed.

## Output behavior

- TUI, JSON, and RPC: accepted draft is terminating tool-result artifact.
- Print mode: tool result triggers one follow-up; extension replaces finalized assistant message with exact accepted draft so stdout is nonempty.
- Direct or mixed assistant output is replaced with blocked marker and never labeled accepted.

Provider streaming can expose unverified text deltas before finalized message is replaced. Contract guarantees accepted artifact verification, not absence of transient provider stream text.

## Non-goals

Verifier does not mechanically prove:

- Preserved modality, uncertainty, causality, permissions, recommendations, or obligations.
- Retention of every unformatted fact or unknown-root-cause statement.
- Domain terminology not recognized by current deterministic inventory.
- Equivalent procedure ordering or warning placement.
- Semantic role or relationship between protected values that retain count and container.
- General Markdown or prose semantic equivalence.
- Protection against another trusted Pi extension that mutates messages, tools, or tool results after this extension.

These remain skill, scorer, review, and benchmark responsibilities. High-risk output still requires source review.

## Packaging and security

Candidate package manifest exposes:

- `./skills`
- `./extensions/clear-writing-guard.ts`

Extension has full Pi process permissions, reads package-owned guidance, creates private temporary source/draft files, invokes package-owned verifier with `python3` without shell interpolation, and removes temporary files in `finally`.

Users can disable extension separately with Pi package filters while retaining skill. Review extension source before installation.

## Release gate

Candidate remains experimental until all conditions pass from clean immutable commit:

1. Unit and integration tests pass.
2. Package dry run includes intended skill, extension, helper modules, and verifier; no bundled dependency.
3. Real Pi probes pass in TUI-equivalent JSON/RPC and print modes.
4. Protected count/container development probes pass across target model families.
5. New preregistered, genuinely unseen release benchmark passes source gates.
6. User explicitly approves publication.

Archived pre-release scenarios are development tests only. They cannot become unseen release evidence.
