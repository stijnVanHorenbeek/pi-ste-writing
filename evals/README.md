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

Development probes and archived scenarios cannot serve as unseen release evidence. First release still requires a new matrix with genuinely unseen scenarios, committed before candidate generation. No package or scorer changes may retroactively change that result.

## Active files

- `run_pi_bench.py`: generation, resume, provenance, deterministic scoring, and reports.
- `run_quality_judge.py`: blind cross-provider judging after source gates pass.
- `score_fixtures.py`: closed-world semantic scorer.
- `fixtures/`: current regression fixtures.
- `benchmark-scenarios.json`: original scenario definitions retained for regression work.

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

## Run a preregistered matrix

Commit all source changes first. Generation requires clean Git tree because each raw cell records exact package commit and Pi version.

```bash
python3 evals/run_pi_bench.py \
  --matrix path/to/preregistered-matrix.json \
  --results-dir evals/results/current-run
```

Rebuild reports without model calls:

```bash
python3 evals/run_pi_bench.py \
  --matrix path/to/preregistered-matrix.json \
  --results-dir evals/results/current-run \
  --report-only
```

Exit 0 means matrix complete with accepted condition-integrity and semantic gates. Exit 1 means evidence incomplete or required gate failed. Invocation or configuration errors exit 2.

## Conditions

Standard matrix conditions:

- `baseline`: no writing skill and no model-callable tools.
- `native-skill`: Pi loads only `clear-technical-writing`; model can use only `read` for progressive loading.
- `direct-prompt`: complete `SKILL.md` is injected with skills and tools disabled. Diagnostic only.

Only native-skill condition gates package acceptance unless new preregistration explicitly says otherwise. Baseline and direct-prompt failures remain visible diagnostic evidence.

## Isolation and provenance

Matrix controls tools, extensions, skills, prompt templates, themes, context files, sessions, project trust, and Pi startup networking. Provider requests still run.

Each call uses empty temporary working directory. Baseline and adapted conditions receive same task input and system prompt.

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

Reports place semantic and exact output-contract results before style. Semantic failures remain authoritative; style or judge preference cannot override them.

Positive automatic activation normally requires at least two loads across three repetitions. Negative structured-output scenarios require zero loads. Exact thresholds must be fixed in preregistered matrix.

`failures.json` retains missing, stale, malformed, routing-invalid, and otherwise rejected cells. Incomplete matrix blocks aggregate claims.

## Blind quality judge

Run judge only after source generation passes required gates:

```bash
python3 evals/run_quality_judge.py \
  --config path/to/preregistered-judge.json \
  --matrix path/to/preregistered-matrix.json \
  --benchmark-results-dir evals/results/current-run \
  --results-dir evals/results/current-judge
```

Judge receives task, source, and blinded candidate labels. It does not receive condition or generator identity. Cross-provider mapping reduces shared-provider bias.

Rubric covers factual fidelity, task completion, uncertainty and obligation, terminology, safety and actionability, readability, and concision.

Deterministic semantic or output-contract failures override judge preference. Judge-reported semantic, task, modality, terminology, or safety blockers require human resolution.

## Limits

Deterministic patterns cover declared fixture properties only. New claims and open prose still need source-relative review. Model judging is not ground truth. Costs are provider metadata, not billing records. No score proves arbitrary semantic equivalence or ASD-STE100 compliance.
