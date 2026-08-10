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

Development probes, `fixtures/hybrid-regressions.json`, and archived scenarios cannot serve as unseen release evidence. Both retained release candidates failed and remain frozen. Commit any future preregistration snapshot before development smoke or candidate generation. No package, runner, scorer, fixture, prompt, or judge change may retroactively change release evidence.

## Active files

- `run_pi_bench.py`: generation, resume, provenance, deterministic scoring, and reports.
- `run_quality_judge.py`: blind cross-provider judging after source gates pass.
- `score_fixtures.py`: closed-world semantic scorer.
- `fixtures/`: current regression fixtures, including schema-v3 semantic-boundary regressions.
- `benchmark-scenarios.json`: original scenario definitions retained for regression work.
- `development-guard-smoke-matrix.json`: required three-call guarded smoke on known development evidence.
- `release-candidate-matrix.json`: 153-cell schema-v2 ragged release matrix.
- `fixtures/release-candidate.json`: five unseen prose fixtures.
- `release-candidate-scenarios.json`: unseen exact-CSV routing control.
- `release-candidate-quality-judge.json`: 99 matched blind comparisons.

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

Each successful raw cell records provider/model identity, usage metadata, cost, duration, native skill-read evidence, deterministic semantic results, procedure results, exact output-contract results, and advisory style findings. Hidden reasoning content is never stored.

## Reports and gates

Reports place semantic and output-contract results before style. Semantic failures remain authoritative; style or judge preference cannot override them. A structured negative routing control can mark exact serialization diagnostic with `output_contract_gate: false`; its no-load activation result remains authoritative, while formatting quality cannot fail package acceptance.

Positive automatic activation requires at least two loads across three repetitions. The structured-output negative requires zero loads. Applicable-cell completeness, model identity, routing safety, native and guarded semantics, applicable procedures, gated output contracts, and guard integrity each require 100%. Diagnostic routing-control serialization is reported separately. Exact thresholds are machine-validated from the preregistered matrix.

`failures.json` retains missing, stale, malformed, routing-invalid, and otherwise rejected cells. Incomplete matrix blocks aggregate claims.

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
