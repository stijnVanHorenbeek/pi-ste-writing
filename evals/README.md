# Evaluation

Package has no public release. Current package version is the first release candidate, `0.1.0-rc.1`.

Historical labels such as `V1`, `V2`, and matrix `version: 6` were internal design or benchmark-amendment identifiers. They were not package releases. Frozen pre-release configs and evidence now live under [`archive/pre-release/`](../archive/pre-release/README.md).

## Current release-candidate status

Evaluation stack includes:

- Preregistered Pi matrix runner.
- Closed-world semantic fixtures.
- Deterministic semantic and output-contract scoring.
- Native skill-routing checks.
- Blind cross-provider quality judgment.
- Guarded-verifier development probes.

Schema v3 adds hybrid semantic evaluation without changing schema-v1/v2 evidence. Fixture-corpus schema v3 limits objective checks to explicitly declared protected literals and their required order. It does not compare global occurrence counts or exact prose sentences. Paired blind judgments attest open semantic fidelity. Any `not_equivalent`, `uncertain`, or conflicting attestation fails. Preference stays descriptive and cannot override objective or semantic gates. Schema-v3 matrices accept historical schema-v2 or semantic-boundary schema-v3 fixture corpora through explicit paths; archived defaults remain unchanged.

Development probes, `fixtures/hybrid-regressions.json`, and archived scenarios cannot serve as unseen release evidence. All retained release candidates failed and remain frozen. Commit any future preregistration snapshot before development smoke or candidate generation. No package, runner, scorer, fixture, prompt, or judge change may retroactively change release evidence.

Prospective runner support now defines a guarded-core release contract; it does not create a candidate config or change historical evidence. See [`docs/guarded-core-release-contract.md`](../docs/guarded-core-release-contract.md). Future guarded-core evidence is limited to `openai-codex/gpt-5.6-sol:high`, `github-copilot/claude-sonnet-5:high`, and `github-copilot/claude-opus-4.6:high`. Guarded gates release; native and baseline remain attempted, visible, and advisory.

## Active files

- `run_pi_bench.py`: generation, resume, provenance, deterministic scoring, and reports.
- `run_quality_judge.py`: blind cross-provider judging after source gates pass.
- `score_fixtures.py`: closed-world semantic scorer.
- `fixtures/`: current regression fixtures, including schema-v3 semantic-boundary regressions.
- `benchmark-scenarios.json`: original scenario definitions retained for regression work.
- `development-guard-smoke-matrix.json`: required three-call guarded smoke on known development evidence.
- `development-hardening-reliability-matrix.json`: 18-cell, three-repetition probe over known guard and routing regressions; never release evidence.
- `release-candidate-matrix.json`: 153-cell schema-v2 ragged release matrix.
- `fixtures/release-candidate.json`: five unseen prose fixtures.
- `release-candidate-scenarios.json`: unseen exact-CSV routing control.
- `release-candidate-quality-judge.json`: 99 matched blind comparisons.
- `semantic-boundary-release-candidate-matrix.json`: frozen 153-cell schema-v3 matrix.
- `fixtures/semantic-boundary-release-candidate.json`: five held-out prose fixtures, now development regressions.
- `semantic-boundary-release-candidate-scenarios.json`: structured negative-routing control.
- `semantic-boundary-release-candidate-quality-judge.json`: frozen 90-cell blind judge config; judge did not run.
- `hardening-release-candidate-matrix.json`: 153-cell schema-v3 hardening release matrix.
- `fixtures/hardening-release-candidate.json`: five held-out prose fixtures for hardening cycle.
- `hardening-release-candidate-scenarios.json`: structured negative-routing control for hardening.
- `hardening-release-candidate-quality-judge.json`: 90-cell blind judge config for hardening.

Runner output defaults to ignored development paths under `evals/results/`. Commit evidence only after explicit review.

## Historical archive

Original matrix reached internal amendment `version: 6`; this was sixth matrix revision, not release six. It failed package acceptance. Independent follow-up also failed and its judge was not run.

Archived paths:

```text
archive/pre-release/evals/config/initial-skill-matrix.json
archive/pre-release/evals/config/initial-quality-judge.json
archive/pre-release/evals/config/independent-review-matrix.json
archive/pre-release/evals/config/independent-review-quality-judge.json
archive/pre-release/evals/evidence/initial-skill-matrix-final/
archive/pre-release/evals/evidence/independent-review/
archive/pre-release/evals/evidence/development/
```

Internal matrix IDs remain `v1` and `v1-independent-review` to preserve provenance. Use source commits recorded in evidence when reproducing historical runs. Do not regenerate archived evidence from current package state.

## Run the first-release evaluation

Commit all source changes first. Generation requires a clean Git tree because each raw cell records the exact package commit, Pi version, skill hash, and extension hash.

Run the required development smoke first:

```bash
python3 evals/run_pi_bench.py \
  --matrix evals/development-guard-smoke-matrix.json \
  --results-dir evals/results/development-guard-smoke
```

Then run the preregistered release matrix:

```bash
python3 evals/run_pi_bench.py \
  --matrix evals/release-candidate-matrix.json \
  --results-dir evals/results/release-candidate \
  --attest-no-prior-candidate-output
```

Release generation verifies that accepted smoke raw evidence matches the same immutable package snapshot.

Rebuild reports without model calls:

```bash
python3 evals/run_pi_bench.py \
  --matrix path/to/preregistered-matrix.json \
  --results-dir evals/results/current-run \
  --report-only
```

Exit 0 means matrix complete with accepted condition-integrity and semantic gates. Exit 1 means evidence incomplete or required gate failed. Invocation or configuration errors exit 2.

## Conditions

Schema-v1 archive conditions remain frozen as baseline, native-skill, and direct-prompt.

Schema-v2/v3 run kinds separate one-repetition `development-smoke`, three-repetition `development-probe`, preregistered `release-candidate`, and prospective `guarded-core-release-candidate` evidence. Development probes require explicit fail-closed policy markers and cannot count as release evidence. Guarded-core matrices gate only declared guarded cohorts; native and baseline evidence stays visible and advisory.

Schema v2 uses:

- `baseline`: no writing skill and no model-callable tools.
- `native-skill`: Pi loads only `clear-technical-writing`; model can use only `read` for progressive loading.
- `guarded`: Pi loads only the explicit guarded verifier extension and invokes exact `/clear-write --mode <mode>` source input with no built-in tools.

Per-scenario applicability creates a ragged matrix. The exact-CSV structured negative omits guarded because `/clear-write` cannot represent its serialization instructions. Native and guarded semantic gates are authoritative. Guard integrity is a separate 100% gate.

## Isolation and provenance

Matrix controls tools, extensions, skills, prompt templates, themes, context files, sessions, project trust, and Pi startup networking. Provider requests still run.

Each call uses an empty temporary working directory. Baseline and native conditions receive the same task input and system prompt. Guarded release scenarios are restricted to canonical, task-equivalent rewrite tasks. Native-versus-guarded is labeled an end-to-end package-path comparison, not a verifier-only effect.

Raw reuse requires matching:

- Cell identity.
- Runner version.
- Matrix SHA-256.
- Package commit and clean state.
- Pi version.
- Provider, model, and thinking level.

Stale and failed attempts remain visible. Existing matching successes resume without another call.

Each successful raw cell records provider/model identity, usage metadata, cost, duration, native skill-read evidence, deterministic semantic results, procedure results, exact output-contract results, and advisory style findings. Failed reads retain only path SHA-256 and `inside-skill`, `outside-skill`, or `unresolved` scope. Guarded submissions record unchanged-draft telemetry without rejected draft text. Hidden reasoning content is never stored.

## Reports and gates

Reports place semantic and output-contract results before style. Semantic failures remain authoritative; style or judge preference cannot override them. A structured negative routing control can mark exact serialization diagnostic with `output_contract_gate: false`; its no-load activation result remains authoritative, while formatting quality cannot fail package acceptance.

Positive automatic activation requires at least two loads across three repetitions. The structured-output negative requires zero loads. Applicable-cell completeness, model identity, routing safety, native and guarded semantics, applicable procedures, gated output contracts, and guard integrity each require 100%. Diagnostic routing-control serialization is reported separately. Exact thresholds are machine-validated from the preregistered matrix.

`failures.json` retains missing, stale, malformed, routing-invalid, and otherwise rejected cells. Incomplete matrix blocks aggregate claims.

## Prospective guarded-core gate

Additive schema-v3 run kind `guarded-core-release-candidate` requires an exact fail-closed `guarded_core` contract: five prose scenarios, three supported models, three repetitions, 45 expected guarded cells, at least 44 successes, at least two successes per model-scenario group, and complete procedure-mode guarded cells. All successful core cells require model identity, applicable routing safety, objective protected contracts, applicable objective procedure, gated output contracts, and correlated guard integrity at 100%. Compatibility cells and global activation remain reported but do not veto this core gate. `benchmark_accepted` uses only `guarded_core_acceptance` for this run kind; existing run kinds are unchanged.

Additive judge schema v4 uses baseline-versus-guarded blind pairs and gates guarded only. It binds the same model cohort, expects 45 unique core candidates, requires at least 44 covered, permits zero `not_equivalent`, at most one `uncertain`, zero conflicts, at most one guarded-core review-required outcome corresponding to that uncertainty, and zero guarded findings in every blocking category. Baseline findings remain advisory. Source authority is `guarded_core_acceptance`, not advisory global aggregates. Wilson 95% intervals describe observed equivalence only and provide no population guarantee.

No future config or held-out fixture has been created. One final genuinely new held-out cycle excludes all candidate models from held-out fixture/config authorship and preregistration review before generation; this does not bar blinded cross-provider quality judging afterward. It cannot rescore old evidence. Failure stops automatic further candidates. Passing is not semantic-safe or ASD-STE100 certification. Publication requires separate explicit approval.

## Blind quality judge

Run judge only after source generation passes required gates:

```bash
python3 evals/run_quality_judge.py \
  --config evals/release-candidate-quality-judge.json \
  --matrix evals/release-candidate-matrix.json \
  --benchmark-results-dir evals/results/release-candidate \
  --results-dir evals/results/release-candidate-judge
```

Judge receives task, source, and blinded candidate labels. It does not receive condition or generator identity. Cross-provider mapping reduces shared-provider bias.

Rubric covers factual fidelity, task completion, uncertainty and obligation, terminology, safety and actionability, readability, and concision.

The judge creates only matched baseline/native and native/guarded pairs. Preferences are descriptive, not a superiority claim. Deterministic semantic, output-contract, routing, or guard-integrity failures override judge preference. Judge-reported semantic, task, modality, terminology, or safety blockers require human resolution.

## Limits

Deterministic patterns cover declared fixture properties only. New claims and open prose still need source-relative review. Model judging is not ground truth. Costs are provider metadata, not billing records. No score proves arbitrary semantic equivalence or ASD-STE100 compliance.
