# Development hardening reliability probe

## Status

Development-only probe passed its frozen gates. It is not release evidence and cannot support publication.

- Matrix: `development-hardening-reliability` version 1.
- Package commit: `0c369f25053a4890ade4a8e8d236b845472e5170`.
- Matrix SHA-256: `288710e5ebac9b992408464bc7c2fc998f08adda8ebf4aad58479be74b9400bc`.
- Runner version: 11.
- Pi version: 0.84.1.
- Package tree was clean.
- Completeness: 18/18.
- Objective contract: 18/18.
- Objective procedure: 9/9.
- Output contract: 18/18.
- Guard integrity: 9/9.
- Final routing safety: 18/18.

No blind semantic or quality judge ran.

## Guard regression

All nine guarded cells produced exact accepted artifacts.

- Seven cells were accepted on first submission.
- One cell revised after first rejection and was accepted on second submission.
- One cell submitted an unchanged rejected draft on its second submission. New SHA-only telemetry recorded one unchanged resubmission. Explicit duplicate feedback was returned, and changed third submission was accepted.

This directly exercised duplicate-draft detection and repair feedback without changing three-submission limit or storing rejected draft text.

## Native routing regression

All nine native cells ended with successful routing safety and objective/output checks.

- Eight final responses loaded skill.
- One final response did not load skill. Activation was intentionally diagnostic for this development probe, so this did not fail frozen probe contract. Across three model groups, observed load counts were 3/3, 3/3, and 2/3, which meet existing release activation threshold diagnostically; this is not retrospective release scoring.
- One native cell retained failed first attempt: skill loaded, two reads succeeded inside skill tree, and one read failed with `outside-skill` scope. Only path SHA-256 was retained. Second configured attempt succeeded with no failed reads.
- Zero final successful responses contained failed-read telemetry.

Path normalization removed deterministic broken links, but model read behavior remains stochastic. Future release evidence still needs clean routing under frozen retry and activation policies.

## Partial and unresolved evidence

`results.json` retains one completed first attempt that failed condition integrity before successful retry. No cells remain unresolved. Generated report therefore shows one retained partial output and `None` for unresolved cells.

## Command

```bash
python3 evals/run_pi_bench.py \
  --matrix evals/development-hardening-reliability-matrix.json \
  --results-dir evals/results/development-hardening-reliability
```

## Boundary

Seen regression fixtures remain development-only. Frozen release evidence was not changed or rescored. No new held-out fixture, preregistration, release smoke, release generation, judgment, or publication action occurred.
