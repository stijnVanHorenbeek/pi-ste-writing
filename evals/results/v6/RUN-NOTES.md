# V1 matrix version 6 run notes

Status: **not accepted**

This directory preserves complete generation evidence for matrix `v1` version 6 at package commit `61700956572775e85a0d79def70eff40505bf858`.

## Completion

- Generation cells: 162/162 successful.
- Model identity: 162/162 matched.
- Routing safety: 162/162 passed.
- Positive/negative activation groups: 17/18 passed.
- Native-skill semantic samples: 49/54 passed.
- Final version 6 judge run: not started because source acceptance gates did not pass.

## Blocking evidence

- Claude Sonnet 5 did not auto-load skill for `correlation-with-unknown-root-cause` in any of three repetitions. Earlier targeted probes reached two of three, showing routing variance rather than deterministic activation.
- Two Claude procedure outputs repeated protected `CHG-4821`, changing occurrence count.
- One Claude release output changed exact date format from `2026-07-14` to `July 14, 2026`.
- One Gemini terminology output used `config specifies ...`, `settings specifies ...`, and `options specifies ...`; deterministic closed-world rule did not attest this mapping.
- One GPT-5.6 Sol policy output changed `test restoration` to `test backup restoration`; deterministic closed-world rule did not attest this phrase.

Last two findings may be semantically acceptable, but V1 keeps unrecognized open paraphrases as failures instead of weakening gate after run.

## Cost and limits

Provider-reported cost metadata for version 6 generation cells totals approximately `$1.804093`:

- `openai-codex`: `$1.115706`
- `github-copilot`: `$0.688387`

This excludes targeted probes and earlier matrix versions. Provider cost metadata is not billing record.

No hidden reasoning content is stored. `reasoning_tokens` contains provider-reported counts only.

## Stop decision

Tuning stopped after version 6 because remaining failures are routing variance, genuine protected-value changes, or paraphrases needing independent attestation. Further prompt tuning against same six scenarios risks benchmark overfitting.
