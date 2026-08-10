# Pre-release archive

No public package release exists yet. Files here record experiments performed before the first release candidate.

Historical files used internal labels such as `V1`, `V2`, and matrix `version: 6`. Those labels meant design generation or benchmark amendment—not package releases. Internal IDs remain unchanged so committed evidence keeps provenance.

## Contents

- `docs/skill-only-experiment-contract.md`: frozen skill-only design contract, historically labeled `V1`.
- `evals/config/initial-skill-matrix.json`: original benchmark matrix. Its internal `version: 6` means sixth matrix amendment.
- `evals/config/initial-quality-judge.json`: original matrix judge configuration.
- `evals/config/independent-review-*.json`: preregistered follow-up configuration.
- `evals/evidence/initial-skill-matrix-final/`: final failed original-matrix evidence, formerly stored as `results/v6`.
- `evals/evidence/independent-review/`: failed independent follow-up and adjudication evidence.
- `evals/evidence/development/`: post-adjudication and guarded-verifier development probes.

`local-untracked-evidence/` can contain ignored local attempts that were never committed as evidence.

## Evidence policy

Archive paths and labels are historical. Do not present them as package versions, published releases, or unseen release evidence. Do not rewrite old outcomes after scorer or package changes. New release-candidate evidence needs a new preregistered matrix and clean immutable source commit.
