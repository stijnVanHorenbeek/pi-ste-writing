# Hybrid release-candidate preregistration

## Status

This document freezes the next release-candidate design before candidate generation.
The previous schema-v2 release remains failed. Its scenarios and outputs are development
regressions only and cannot count as evidence for this cycle.

Frozen artifacts:

- Matrix: `evals/hybrid-release-candidate-matrix.json`
- Prose corpus: `evals/fixtures/hybrid-release-candidate.json`
- Structured routing control: `evals/hybrid-release-candidate-scenarios.json`
- Semantic and quality judge: `evals/hybrid-release-candidate-quality-judge.json`
- Generation runner: `evals/run_pi_bench.py`
- Objective scorer: `evals/score_fixtures.py`
- Judge runner: `evals/run_quality_judge.py`
- Required smoke: `evals/development-guard-smoke-matrix.json`

## Evidence design

Five unseen human-facing prose scenarios exercise new fictional domains, identifiers,
values, relationships, and wording. One fixtureless structured-output scenario is a
routing negative. Candidate models have not received these scenarios.

Conditions:

- `baseline`: package skill and guard unavailable.
- `native-skill`: normal progressive skill routing with `read` only.
- `guarded`: explicit `/clear-write --mode <mode>` with no built-in tools.

All prose scenarios use command-equivalent rewrite tasks and all three conditions. The
structured routing control uses baseline and native only. Three models and three
repetitions yield 153 generation cells:

- `openai-codex/gpt-5.6-sol:high`
- `github-copilot/claude-sonnet-5:low`
- `github-copilot/gemini-3.6-flash:medium`

Execution is bounded to three concurrent calls: one `openai-codex` call and two
`github-copilot` calls.

## Hybrid acceptance

Generation applies only objective deterministic gates:

- complete applicable cells and requested model identity;
- routing and skill-loading integrity;
- exact protected values, occurrence counts, and containers;
- exact ordered anchors for destructive procedures;
- exact structured-output contracts;
- guarded protocol and accepted-artifact integrity.

Objective checks do not claim open semantic equivalence. They contain no free-prose
semantic regexes, word windows, or approved-paraphrase lists.

After every objective source gate passes, the existing paired blind judge makes
source-relative semantic attestations while also reporting descriptive quality
preference. Semantic labels are:

- `equivalent`
- `not_equivalent`
- `uncertain`

The judge sees blinded candidates and cannot see source provider, model, condition, or
treatment names. Judges are cross-provider. Baseline-versus-native and
native-versus-guarded comparisons over five applicable prose scenarios yield 90 judge
calls. Native candidates receive two observations. Any adverse observation, uncertainty,
or conflict fails acceptance. Preference cannot override objective or semantic failure.
The structured routing control is not judged.

## Thresholds

All applicable generation and judgment completeness, identity, objective, procedure,
output-contract, guard-integrity, cross-provider, candidate-coverage, and semantic gates
are 100%. Maximum counts for `not_equivalent`, `uncertain`, conflicts, and
review-required outcomes are zero. Positive routing follows the frozen two-of-three
activation threshold per group; negative routing permits zero skill loads.

## Execution boundary

Before generation:

1. Commit and push this complete snapshot.
2. Require a clean Git tree and exact package, skill, extension, runner, scorer, corpus,
   scenario, matrix, and judge-config hashes.
3. Run the three-model development smoke on known development evidence.
4. If smoke exposes a defect, fix it and create a new preregistration commit before any
   held-out generation.
5. Attest that no candidate model has previously received these scenarios.

Generation command:

```bash
python3 evals/run_pi_bench.py \
  --matrix evals/hybrid-release-candidate-matrix.json \
  --results-dir evals/results/hybrid-release-candidate \
  --attest-no-prior-candidate-output
```

Judge command, only after all objective source gates pass:

```bash
python3 evals/run_quality_judge.py \
  --matrix evals/hybrid-release-candidate-matrix.json \
  --config evals/hybrid-release-candidate-quality-judge.json \
  --benchmark-results-dir evals/results/hybrid-release-candidate \
  --judge-results-dir evals/results/hybrid-release-candidate-judge
```

## No retrospective repair

After any held-out candidate output exists:

- do not alter package, prompt, runner, scorer, corpus, scenarios, matrix, judge config,
  thresholds, or fixtures to improve this cycle;
- do not retry a completed guarded job as a new job;
- retain failed, incomplete, stale, invalid, and partial evidence;
- do not convert human adjudication into a retrospective pass;
- use all observed scenarios only as development regressions for a later cycle.

The official ASD-STE100 Issue 9 PDF is not bundled. Official guidance can support
source-relative review, but no result certifies ASD-STE100 compliance or arbitrary
semantic equivalence. Package remains private and unpublished. Publication requires a
separate explicit user approval after all frozen gates pass.
