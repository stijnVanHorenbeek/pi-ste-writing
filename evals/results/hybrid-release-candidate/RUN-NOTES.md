# Hybrid release-candidate run notes

Date: 2026-08-10

## Disposition

The schema-v3 source matrix did not pass. Do not run the paired semantic/quality judge and do not approve publication from this evidence.

- Successful cells: 149/153
- Guard integrity: 45/45 passed
- Objective acceptance: 65/98 successful applicable cells passed; 99 were expected
- Objective procedure acceptance: 6/18 passed
- Output contract: 92/98 successful applicable cells passed
- Condition integrity: failed because completeness and activation requirements were not met
- Semantic and quality judge: not run because objective source gates failed

## Unresolved calls

Four cells remained failed after preregistered attempts:

- Three Claude Sonnet 5 baseline Valerius cells returned no final assistant text.
- One Gemini Flash native Aethel cell failed condition integrity.

## Objective findings

Objective failures were retained exactly as produced:

- `source-equality.number`: 41
- `source-equality.inline_code`: 33
- `ordered-anchor`: 18
- `output-contract`: 12
- `source-equality.identifier`: 10
- `source-equality.bold_text`: 9
- `source-equality.date`: 4

The procedure fixture's ordered anchors included exact literal source sentences. Natural rewrites could preserve commands and meaning while changing those sentences, so 12/18 applicable native/guarded procedure cells failed that objective gate. This is a preregistered fixture-design diagnosis, not grounds to alter or rescore this cycle.

All 45 guarded cells passed the mechanical verifier. Guard success still attests only recognized protected occurrence/container preservation, not open semantic equivalence.

## Freeze policy

No package, prompt, runner, scorer, corpus, scenario, matrix, judge-config, threshold, or fixture change was made after held-out output. Failed and partial evidence remains visible. These scenarios are now development regressions only.

The package remains private and unpublished. Publication requires a later accepted cycle and separate explicit user approval.
