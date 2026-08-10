# Independent V1 follow-up run notes

Status: **not accepted; incomplete**

This directory preserves generation evidence for `v1-independent-review` version 1 at package commit `b7cd7540a05176269bc14315863db4ffc7d97ec1`. Fresh-context reviewers authored, rejected, redrafted, and revalidated the six scenarios before this commit and before any candidate output existed. No skill, prompt, fixture, scorer, or matrix changes were made after candidate generation began.

## Completion

- Generation cells successful: 159/162.
- Model identity matches: 159/162.
- Routing-safety passes: 159/162.
- Native positive/negative activation groups: 17/18.
- Native semantic samples: 33/54 passed.
- Final independent judge: not started because source completeness, activation, and semantic gates failed.

Three unresolved cells are all `github-copilot/claude-sonnet-5:low`, `direct-prompt`, `orbital-greenhouse-modal-policy`, repetitions 1–3. Each returned no final assistant text in four recorded attempts. These diagnostic transport failures are retained and still make the preregistered matrix incomplete.

## Blocking evidence

- Claude Sonnet 5 did not automatically load the native skill for `broker-failover-correlation-unknown-cause` in any of three repetitions. Other positive activation groups met the two-of-three threshold, and all three structured-output groups correctly stayed unloaded.
- Native semantic gates passed 12/18 GPT-5.6 Sol samples, 7/18 Claude Sonnet 5 samples, and 14/18 Gemini 3.6 Flash samples.
- Failure clusters include two-sided incident correlation/unknown-cause retention, confirmed-versus-sequence-only release findings, modal distinctions, protected occurrence counts, and safe procedure structure.
- Some failures may reflect conservative closed-world phrase coverage rather than changed meaning. Preregistration forbids post-output scorer tuning, so they remain failures without retrospective amendment.

## Cost

Provider-reported metadata for independent-review work totals approximately `$7.229049`:

- Scenario authoring and independent preregistration audits: `$5.496416`.
- Generation, retained partial responses, and retries: `$1.732633`.
- Final judge: `$0` because source gates failed.

This exceeds the earlier `$5–$6` estimate by approximately `$1.23`; repeated independent draft audits caused the overrun. Provider cost metadata is not a billing record and failed empty responses can lack cost metadata.

No hidden reasoning content is stored. `reasoning_tokens` fields contain provider-reported counts only.

## Post-run blinded adjudication

Eighteen deterministic failures where the native skill loaded received blinded cross-provider review. Two package-contract disputes received separate arbitration.

- Genuine release-blocking failures: 6.
- Deterministic evaluator false positives: 12.
- Ambiguous: 0.
- Additional provider-reported adjudication cost: approximately `$0.728698`.

Genuine failures were two inline-to-fenced command moves, three protected occurrence-count changes, and one omitted unknown-root-cause fact. False positives came from narrow patterns for safe causal, modal, measurement, and unknown-cause paraphrases. Adjudication does not retroactively change the preregistered result; it makes the failed scenarios development evidence for later revisions. See `adjudication/summary.json`.

## Decision

Independent evidence does not support V1 release under the declared contract. Package remains unpublished. Further tuning against these scenarios would invalidate their role as unseen independent evidence and risk benchmark overfitting.
