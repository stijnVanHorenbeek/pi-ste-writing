# First-release candidate preregistration

Status: frozen design draft. Commit this file, its configs, fixtures, scorer, runner, and package before any release-candidate generation.

The package is unpublished. Archived scenarios and development probes are regressions only and do not count as unseen release evidence.

## Frozen artifacts

- Generation matrix: `evals/release-candidate-matrix.json`
- Semantic fixtures: `evals/fixtures/release-candidate.json`
- Structured routing control: `evals/release-candidate-scenarios.json`
- Blind judge: `evals/release-candidate-quality-judge.json`
- Required development smoke: `evals/development-guard-smoke-matrix.json`
- Generation runner: `evals/run_pi_bench.py`
- Judge runner: `evals/run_quality_judge.py`
- Deterministic scorer: `evals/score_fixtures.py`

The release matrix binds the exact judge-config path and SHA-256 before generation; schema-v2 judging rejects substituted configs and requires the source package commit.

The release scenarios are unseen held-out instances of previously tested semantic-risk families. They use new fictional domains, identifiers, values, commands, paths, links, relationships, and exact wording; none appeared in prior candidate generation. They were independently drafted and reviewed without invoking candidate models. The development smoke deliberately uses an old regression fixture and is not release evidence.

## Conditions and cohorts

Schema v2 has three declared conditions:

- `baseline`: package skills and extensions unavailable; no model-callable tools.
- `native-skill`: only `clear-technical-writing` is available, with `read` for progressive loading.
- `guarded`: explicit `/clear-write --mode <mode>` loads only the guarded verifier extension and no built-in tools.

The ragged matrix reports two linked cohorts:

1. **Routing/control cohort:** baseline and native-skill on all six scenarios.
2. **Rewrite-path cohort:** baseline, native-skill, and guarded on five canonical, task-equivalent prose rewrites.

`hushvale-spore-transfer-csv` excludes guarded because `/clear-write` accepts only mode and source and cannot represent its exact CSV serialization task. That exclusion is frozen before generation and is omitted from denominators rather than counted as a failure.

Native-versus-guarded is an end-to-end package-path comparison. It is not a verifier-only causal estimate: guarded invocation is explicit, injects package guidance, and can perform protected-content repair turns.

## Models and bounded execution

Generation portfolio:

- `openai-codex/gpt-5.6-sol:high`
- `github-copilot/claude-sonnet-5:low`
- `github-copilot/gemini-3.6-flash:medium`

There are three repetitions. Five scenarios have 27 cells each and the structured negative has 18, for **153 applicable generation cells**.

At most three calls run concurrently:

- one `openai-codex` call;
- up to two `github-copilot` calls.

Schema-v1 archived matrices retain their original sequential Cartesian behavior.

## Required development smoke

Before unseen generation, run exactly three guarded calls in parallel—one per generation model—using the known `release-facts-and-causes` regression fixture:

```bash
python3 evals/run_pi_bench.py \
  --matrix evals/development-guard-smoke-matrix.json \
  --results-dir evals/results/development-guard-smoke
```

The smoke must validate explicit extension loading, authorized submit evidence, exact accepted-output linkage, deterministic scoring, resume data, provider-reported cost capture, immutable snapshots, and provider concurrency bounds. Native activation is explicitly not applicable to this guarded-only smoke.

Release generation refuses to start unless the smoke result and raw evidence are accepted and match the same runner version and hash, scorer hash, package commit, clean state, Pi version, skill hash, and extension hash. If smoke reveals a runner defect, repair it, commit a new preregistration snapshot, and rerun the smoke. The repaired snapshot—not this one—becomes the release preregistration.

## Deterministic acceptance gates

All rates below use applicable cells only:

- Cell completeness: 100%.
- Model identity: 100%.
- Routing safety and ambient-resource isolation: 100%.
- Native semantic gate: 100%.
- Native applicable procedure gate: 100%.
- Native output-contract gate: 100%.
- Guarded semantic gate: 100%.
- Guarded applicable procedure gate: 100%.
- Guarded output-contract gate: 100%.
- Guard mechanical-integrity gate: 100%.
- Positive native activation: at least 2 of 3 repetitions for every model and positive scenario.
- Structured negative native activation: exactly 0 of 3 for every model.

A guarded success requires all of the following:

- one to three `submit_clear_rewrite` submissions;
- each submission message contains exactly one submit call, optional thinking, and no text or sibling call;
- assistant-call, tool-start, and tool-end IDs and arguments correlate;
- one job ID is used throughout;
- attempts are contiguous;
- statuses are zero or more `retry` values followed by exactly one `accepted`;
- accepted call draft, result-detail draft, result text, and terminal print artifact match byte-for-byte; when Pi emits no follow-up assistant message after accepted `toolUse`, the trusted accepted tool-result text is the terminal print artifact;
- no direct output, unauthorized tool, malformed, dangling, blocked, verifier-error, or post-acceptance event;
- guard isolation flags are present;
- submitted source and draft text are not retained in guard telemetry; only hashes, byte counts, statuses, attempts, and provider metadata are stored.

A completed guard protocol failure is not retried as a fresh job. Outer retries are allowed only for failures before any guarded submission. Failed, partial, stale, malformed, and transport evidence remains visible.

The verifier attests only recognized protected occurrence counts and coarse Markdown containers. It does not attest semantic roles, arbitrary facts, ordering, modality, causality, or equivalence. Deterministic semantic and procedure scoring remains separate and authoritative.

## Blind quality review

Only after source gates pass, generate matched blind judgments:

```bash
python3 evals/run_quality_judge.py \
  --config evals/release-candidate-quality-judge.json \
  --matrix evals/release-candidate-matrix.json \
  --benchmark-results-dir evals/results/release-candidate \
  --results-dir evals/results/release-candidate-judge
```

Matched comparisons:

- baseline versus native: 54 judgments;
- native versus guarded: 45 judgments;
- total: **99 judgments**.

Codex Sol judges Copilot source outputs. Copilot Gemini Flash judges Codex source outputs. Provider limits remain one Codex and up to two Copilot calls.

Acceptance requires 100% judge completeness, 100% cross-provider mapping, and zero judgments requiring human review because of blocking semantic, task, modality, terminology, or safety findings. Preference and ordinal scores are descriptive only; this preregistration makes no superiority or non-inferiority claim.

Deterministic semantic, output-contract, routing, and guard-integrity failures override judge preference.

## No post-output tuning

Release generation additionally requires the explicit `--attest-no-prior-candidate-output` operator handshake. Do not provide it if any model has already received these release scenarios.

After any release-candidate output exists, do not repair or tune the package, prompts, runner, scorer, fixtures, scenario applicability, judge rubric, or thresholds based on that output. Any necessary change invalidates unseen release evidence and requires new unseen scenarios plus a new preregistration commit.

Do not store hidden reasoning. Retain only provider-reported usage and reasoning-token metadata.

No result proves arbitrary semantic equivalence or ASD-STE100 certification/compliance. Strict vocabulary review requires the official dictionary.

Publication is a separate step and requires explicit user approval even if every gate passes.
