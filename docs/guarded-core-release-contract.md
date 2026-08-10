# Prospective guarded-core release contract

This contract applies only to one future, genuinely new held-out release cycle. It does not rescore, repair, reinterpret, or replace prior evidence. Every retained candidate remains failed. No future candidate matrix or judge config exists yet.

## Supported cohort

Guarded-core release evidence is limited to these exact model specifications:

- `openai-codex/gpt-5.6-sol:high`
- `github-copilot/claude-sonnet-5:high`
- `github-copilot/claude-opus-4.6:high`

The guarded condition is the release gate. Native-skill and baseline conditions remain attempted and reported as compatibility and routing evidence, but their aggregate acceptance and global activation results are advisory. Failed, partial, missing, invalid, and stale evidence remains visible.

## Benchmark contract

A future schema-v3 matrix can use `run_kind: guarded-core-release-candidate` only with an exact, fail-closed `guarded_core` object. It binds:

- `condition: guarded`;
- exactly five declared prose scenario IDs;
- the three exact supported model specifications above;
- exactly three repetitions;
- `expected_cells: 45` (`5 × 3 × 3`);
- `expected_procedure_cells: 9` (exactly one procedure scenario across three models and three repetitions);
- `minimum_successful_cells: 44`;
- `minimum_successful_repetitions_per_model_scenario: 2`;
- `procedure_mode_requires_full_completion: true`;
- 100% rates among successful guarded-core cells for model identity, applicable routing safety, objective protected contract, applicable objective procedure, gated output contract, and correlated guard integrity;
- guarded-only objective and semantic-review gates with minimum candidate coverage `44/45`;
- `compatibility_cells_veto: false` and `global_activation_veto: false`.

Every procedure-mode guarded-core cell must complete successfully. A non-procedure failure is tolerated only when at least 44 core cells succeed and every model-scenario group still has at least two of three successful repetitions. Guard integrity is correlated on the same successful cells; a guard pass from another cell cannot compensate.

For this run kind only, `benchmark_accepted` reads `guarded_core_acceptance`. Existing release-candidate and development run kinds keep their existing gates.

## Blind judge contract

Future judging uses additive schema v4 and one baseline-versus-guarded blind pair per core candidate. Guarded is the only semantically gated condition. Judge config must bind the same supported model specifications and these exact limits:

- expected guarded-core candidates: 45;
- minimum unique semantic coverage: 44;
- cross-provider mapping: 100% of successful judgments;
- `not_equivalent`: 0;
- `uncertain`: at most 1;
- candidate conflicts: 0;
- guarded-core review-required outcomes: at most 1, corresponding to permitted uncertainty;
- every guarded candidate blocking-issue category: 0.

Schema-v4 source validation requires accepted `guarded_core_acceptance`. Failing advisory compatibility, global activation, baseline blocking issues, or other global aggregates do not veto judge execution or guarded-core acceptance. Only guarded candidate labels and blocking issues gate schema-v4 semantic acceptance. Missing, failed, invalid, and stale source or judge evidence remains reported.

Reports include a Wilson 95% interval for the observed equivalent proportion. Interval is descriptive only. It is not a population guarantee, certification, equivalence proof, or non-inferiority claim.

## Final-cycle governance

Before generation, commit one preregistered snapshot containing genuinely new held-out fixtures and configs. All three candidate models are excluded from authoring held-out fixtures or configs and from preregistration review before generation. This governance exclusion does not prohibit cross-provider blind quality judging after generation; judge provider must still differ from source provider and identities remain blinded.

Prior candidate outputs cannot be retrospectively rescored. No package, scorer, runner, fixture, prompt, judge, or threshold change can convert prior failed evidence into passing evidence.

One final held-out cycle is allowed. If it fails, stop: do not automatically generate, repair, or schedule further candidates. Any later cycle requires a new explicit user decision, not an automatic continuation.

Passing benchmark and judge contracts does not certify semantic safety, arbitrary semantic equivalence, ASD-STE100 compliance, or ASD-STE100 conformance. Publication remains a separate action and requires explicit user approval after evidence review.
