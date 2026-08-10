# Semantic boundary release-candidate preregistration

## Status

This document freezes the semantic boundary release-candidate design before candidate generation.
This cycle exercises genuinely new prose fixtures and structured routing controls. No candidate-generation call has received these exact source/task inputs or produced output for them.

Frozen artifacts:

- Matrix: `evals/semantic-boundary-release-candidate-matrix.json`
- Prose corpus: `evals/fixtures/semantic-boundary-release-candidate.json`
- Structured routing control: `evals/semantic-boundary-release-candidate-scenarios.json`
- Semantic and quality judge: `evals/semantic-boundary-release-candidate-quality-judge.json`
- Generation runner: `evals/run_pi_bench.py` (runner version 9)
- Objective scorer: `evals/score_fixtures.py`
- Judge runner: `evals/run_quality_judge.py`
- Required smoke: `evals/development-guard-smoke-matrix.json`
- Required smoke evidence: `evals/results/semantic-boundary-development-guard-smoke/`

Frozen artifact hashes are committed in this snapshot.

## Evidence design

Five unseen human-facing prose scenarios exercise new fictional domains (spacecraft telemetry,
medical device calibration, reactor fuel loading, network protocol state machines, mining sensor
analysis), identifiers, values, relationships, technical terms, and wording. Entities, phrasing,
and fact combinations are materially disjoint from every prior fixture. One fixtureless
structured-output scenario provides routing negative control. No prior candidate-generation output exists for these scenarios.

Conditions:

- `baseline`: package skill and guard unavailable.
- `native-skill`: normal progressive skill routing with `read` only.
- `guarded`: explicit `/clear-write --mode <mode>` with no built-in tools.

All prose scenarios use command-equivalent rewrite tasks and all three conditions. The
structured routing control uses baseline and native only, with output contract retained as
diagnostic marker. Activation and skill non-loading are authoritative; the output contract
does not gate acceptance for the diagnostic scenario.

Three models and three repetitions yield 153 generation cells:

- `openai-codex/gpt-5.6-sol:high` (1 concurrent call maximum)
- `github-copilot/claude-sonnet-5:low` (2 concurrent calls maximum for github-copilot)
- `github-copilot/gemini-3.6-flash:medium`

Expected generation cells: 153
Expected gated output-contract cells: 90 (5 prose × 2 gated conditions × 3 models × 3 reps)
Expected diagnostic output cells within gated conditions: 9 (1 structured × native-skill × 3 models × 3 reps). Baseline outputs remain non-authoritative diagnostics.

Execution is bounded to three concurrent calls: one `openai-codex` call and two
`github-copilot` calls.

## Schema v3 contract

Schema version 3 uses required literals for unique protected container values and ordered
literals for immutable procedure tokens only. Corpus defines:

- Exact task text
- `expect_skill_loaded: true` for prose scenarios requiring semantic review
- `semantic_review_applicable: true` for gated semantic attestation
- `required_literals` covering every unique protected inline-code, fenced-code, markdown-link,
  or bold value at least once in its original container
- `ordered_literals` only for immutable commands and machine-return tokens in procedures
- Claim-by-claim source-relative semantic propositions covering actors, modality/certainty,
  factual assertions/negations, causality/thresholds, terminology roles, and procedure safety

Schema v3 does not include:

- Exact prose anchors
- Global occurrence equality for ordinary numbers, dates, units, identifiers outside protected
  containers
- Regex or window-based semantic checks
- Official dictionary content or ASD-STE100 compliance certification

Structured routing scenario marks `expect_skill_loaded: false` and `output_contract_gate: false`.
Skill activation/non-loading is authoritative; exact output contract remains diagnostic serialization
boundary only.

## Hybrid acceptance

Generation applies only objective deterministic gates:

- 100% applicable cell completeness and requested model identity
- 100% routing and skill-loading integrity
- 100% exact protected values per `required_literals` in declared containers
- 100% exact ordered procedure tokens per `ordered_literals`
- 100% exact structured-output contracts where `output_contract_gate: true`
- 100% guarded protocol and accepted-artifact integrity

Objective checks do not claim open semantic equivalence.

After every objective source gate passes, the existing paired blind judge makes
source-relative semantic attestations while also reporting descriptive quality
preference. Semantic labels are:

- `equivalent`
- `not_equivalent`
- `uncertain`

The judge sees blinded candidates and cannot see source provider, model, condition, or
treatment names. Judges are cross-provider. Baseline-versus-native and
native-versus-guarded comparisons over five applicable prose scenarios yield 90 judge
calls (5 × 2 × 3 × 3). Native candidates receive two observations. Any adverse observation,
uncertainty, or conflict fails acceptance. Preference cannot override objective or semantic
failure. The diagnostic structured routing control is not judged.

## Thresholds

All applicable generation and judgment completeness, identity, objective contract, objective
procedure, output-contract (where gated), guard-integrity, cross-provider, candidate-coverage,
and semantic gates are 100%. Maximum counts for `not_equivalent`, `uncertain`, conflicts, and
review-required outcomes are zero.

Positive routing follows the frozen two-of-three activation threshold per group; negative routing
permits zero skill loads. The diagnostic scenario serialization boundary does not gate acceptance.

## Execution boundary

Before generation:

1. Commit and push this complete snapshot.
2. Require a clean Git tree and exact package, skill, extension, runner, scorer, corpus,
   scenario, matrix, and judge-config hashes.
3. Run the three-model development smoke on known development evidence at
   `results/semantic-boundary-development-guard-smoke/`.
4. If smoke exposes a defect, fix it and create a new preregistration commit before any
   held-out generation.
5. Attest that no candidate-generation output exists for these exact scenario inputs.

Smoke command:

```bash
python3 evals/run_pi_bench.py \
  --matrix evals/development-guard-smoke-matrix.json \
  --results-dir evals/results/semantic-boundary-development-guard-smoke
```

Generation command:

```bash
python3 evals/run_pi_bench.py \
  --matrix evals/semantic-boundary-release-candidate-matrix.json \
  --results-dir evals/results/semantic-boundary-release-candidate \
  --attest-no-prior-candidate-output
```

Judge command, only after all objective source gates pass:

```bash
python3 evals/run_quality_judge.py \
  --matrix evals/semantic-boundary-release-candidate-matrix.json \
  --config evals/semantic-boundary-release-candidate-quality-judge.json \
  --benchmark-results-dir evals/results/semantic-boundary-release-candidate \
  --results-dir evals/results/semantic-boundary-release-candidate-judge
```

## No retrospective repair

After any held-out candidate output exists:

- Do not alter package, prompt, runner, scorer, corpus, scenarios, matrix, judge config,
  thresholds, or fixtures to improve this cycle
- Do not retry a completed guarded job as a new job
- Retain failed, incomplete, stale, invalid, and partial evidence
- Do not convert human adjudication into a retrospective pass
- Use all observed scenarios only as development regressions for a later cycle

## Supporting guidance and boundaries

The official ASD-STE100 Issue 9 PDF at `/Users/stijn/Downloads/ASD-STE100_ISSUE9.pdf` is
available locally as a reference for source-relative review but is not redistributed in the
repository. Official guidance can inform semantic equivalence assessments, but no result
certifies ASD-STE100 compliance or arbitrary semantic equivalence.

Package remains private and unpublished. Publication requires a separate explicit user
approval after all frozen gates pass. This commit stops before smoke and generation.

Seen scenarios from this cycle become development regressions for future cycles.
