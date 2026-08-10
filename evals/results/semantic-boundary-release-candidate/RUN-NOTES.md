# Semantic-boundary release-candidate run notes

## Status

This frozen candidate failed its preregistered source gates and is retained as failed evidence.
Blind semantic and quality judging did not run.

- Development smoke: 3/3 successful; all smoke gates accepted.
- Release generation: 151/153 successful.
- Package commit: `bbffefd4b8e843e7057195ccc4e39df418b3fe79`.
- Matrix SHA-256: `98d36a80267e64f6bd271dd1ca805d53344f00fb24044068896da128c88fdcb7`.
- Runner version: 9.
- Pi version: 0.84.1.
- Package tree was clean at generation.

## Successful applicable evidence

Every successful applicable sample passed its deterministic gate:

- Objective contract: 97/97 successful applicable samples; 99 expected.
- Objective procedure: 17/17 successful applicable samples; 18 expected.
- Gated output contract: 88/88 successful applicable samples; 90 expected.
- Guard integrity: 44/44 successful guarded samples; 45 expected.
- Condition integrity: 151/151 successful samples; 153 expected.
- Diagnostic structured output: 3/9 passed; diagnostic only and not an acceptance gate.

Completeness failures prevent acceptance despite zero deterministic failures among successful applicable samples.

## Retained failures

1. `github-copilot/claude-sonnet-5:low`, guarded `hyperion-refuel-sequence`, repetition 2:
   - Error: `Pi benchmark call returned no final assistant text`.
   - Guard observed one job and three contiguous submissions.
   - Attempts 1 and 2 returned `retry`; attempt 3 returned `blocked`.
   - No submission was accepted and no accepted artifact exists.
   - Drafts and verifier feedback remain redacted; evidence contains hashes and byte counts only.
   - This terminal guarded job must not be retried as a fresh job.

2. `github-copilot/gemini-3.6-flash:medium`, native-skill `nexus-protocol-state`, repetition 3:
   - Both configured attempts failed condition integrity.
   - Skill entrypoint loaded, but each attempt included one failed skill-tree read, so routing safety failed closed.
   - No further attempt was made.

## Commands

Smoke:

```bash
python3 evals/run_pi_bench.py \
  --matrix evals/development-guard-smoke-matrix.json \
  --results-dir evals/results/semantic-boundary-development-guard-smoke
```

Release generation:

```bash
python3 evals/run_pi_bench.py \
  --matrix evals/semantic-boundary-release-candidate-matrix.json \
  --results-dir evals/results/semantic-boundary-release-candidate \
  --attest-no-prior-candidate-output
```

## Freeze boundary

No package, skill, prompt, runner, scorer, fixture, scenario, matrix, judge config, or threshold was changed after candidate output existed. Failed and partial evidence remains visible. These scenarios are development regressions for future cycles. Publication remains blocked.
