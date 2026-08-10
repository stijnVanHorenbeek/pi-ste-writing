# V2 verifier development notes

Status: development evidence only. Dirty working tree; not preregistered release evidence.

## Architecture review

Two fresh-context read-only reviews evaluated enforcement and Pi integration.

Accepted findings:

- Claim only accepted artifact is verified; unverified provider stream deltas can appear before final-message replacement.
- Keep trusted source in extension state; submit tool accepts job ID and draft only.
- Reject direct text, mixed text/tool output, sibling calls, duplicate submissions, stale jobs, and replay.
- Handle print mode separately because terminating tool result is not printed as final assistant text.
- Reuse Python protected-span extractor instead of maintaining TypeScript regex copy.
- Preserve V1 contract/evidence and add separate V2 contract.

Provider-reported architecture-review cost: approximately `$4.651710`:

- Enforcement contract review: `$1.730406`.
- Pi integration review: `$2.921304`.

Post-implementation correctness and contract reviews cost approximately `$0.3623502`:

- Guard correctness review: `$0.11053785`.
- Tests, contract, and docs review: `$0.25181235`.

Review findings led to EOF and variable-spacing mode parsing coverage, docs/container alignment, explicit bundled-linter dependency wording, and narrower count/container claims. Final blocker review cost `$0.09745905` and found no unresolved security blocker.

## Live development probes

Model: `github-copilot/gpt-5-mini:low`.

### JSON mode

Current multiset verifier accepted a first submission that preserved both inline protected occurrences and containers. Accepted tool result was: `The service may reduce latency. Before ticket \`OPS-6634\`, run \`check-latency --window=17m\`.`

Provider-reported current-probe cost: `$0.00151975`.

An earlier ordered-occurrence prototype rejected a safe value reorder and repaired it on a second turn at `$0.0024478`. That design was retired after tests showed it also rejected preregistered safe fixture rewrites. Current verifier gates counts and containers, not semantic role or occurrence order.

### RPC mode

Interactive RPC command returned successful prompt response and accepted tool result. Accepted draft preserved the one `OPS-6634` inline occurrence. Provider-reported cost: `$0.00080065`.

### Print mode

Guarded command produced nonempty final assistant text. Accepted output preserved inline command and ticket occurrence order/count. A second probe shadowed `python3` with deterministic exit 2; print mode emitted a verifier-error block and no candidate draft. Print mode does not expose provider cost metadata, so cost is unavailable.

### Isolation

Both probes used explicit local package loading plus `--no-extensions`, `--no-skills`, `--no-context-files`, `--no-prompt-templates`, `--no-themes`, `--no-session`, `--no-approve`, and `--offline`. Explicit package extension remained loaded while ambient extensions were disabled.

One earlier print attempt without `--no-extensions` crashed in unrelated ambient `pi-caveman` stale-context timer. No package conclusion was drawn from that attempt.

## Release implication

Probes validate development seam only. V2 still needs clean-commit repeated model probes and genuinely unseen preregistered release benchmark before publication consideration.
