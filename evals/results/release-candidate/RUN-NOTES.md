# First-release candidate run notes

Date: 2026-08-10

## Disposition

The preregistered source matrix did not pass. Do not run the blind quality judge and do not use this run to approve publication.

- Successful cells: 143/153
- Guard integrity: 43/45 successful guarded cells passed; overall gate failed because 2 guarded cells failed
- Semantic acceptance: 29/92 successful applicable cells passed; overall gate failed
- Procedure acceptance: 12/16 successful applicable procedure cells passed; overall gate failed
- Output contract: 92/92 successful applicable cells passed, but overall gate failed because 7 applicable cells were unsuccessful
- Condition integrity: failed
- Blind quality judge: not run because deterministic source gates failed

## Unresolved cells

Ten cells remained failed after preregistered attempts:

- Six Claude Sonnet 5 CSV control cells (three baseline and three native) returned no final assistant text on both attempts.
- Two Gemini Flash native Sablefen cells failed condition integrity on both attempts.
- One Claude guarded Calder cell reached an accepted third submission but also had unauthorized/unmatched tool events, so it failed closed.
- One Claude guarded Calder cell exhausted three submissions and ended blocked.

These failures remain source evidence. They were not retried as new guarded jobs or repaired after observing release outputs.

## Interpretation limits

Deterministic semantic failures have not been human-adjudicated. Counts describe the preregistered closed-world scorer only; they do not establish arbitrary semantic equivalence or classify every failure as genuine model error. Deterministic failures still block the preregistered judge and release decision.

The package remains private and unpublished. Publication requires separate explicit approval.
