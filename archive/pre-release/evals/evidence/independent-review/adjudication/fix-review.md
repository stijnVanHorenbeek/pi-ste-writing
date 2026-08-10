## Review

**Verdict: NO-GO.** Two blocker classes: scorer now accepts semantic contradictions; router broadened excluded scope.

### Blockers

- **Blocker — over-broad scorer relaxations create false negatives.** `evals/fixtures/independent-review.json:70`, `:127`, and `:209` admit negation or omit required causal relation. Direct probes against full scorer all returned `gate_passed=True`:
  - Helios: `61% of these failures were unrelated to expired GPU leases` passes `helios.confirmed-cause` because line 70 requires only nearby tokens, not causal polarity.
  - Broker: `temporal correlation, but the failover did not cause the increase` passes because line 209 accepts `temporal correlation` alone; narrow forbidden pattern at `:203` misses this disproof sibling.
  - Greenhouse: `might not require 17 minutes` passes because line 127 allows arbitrary text, including `not`, between `might` and `require`.
  Same probes fail against `HEAD` fixture and pass against worktree fixture. Regression introduced by diff. Fix patterns to encode relation and polarity; add these exact negative regressions to tests.

- **Blocker — quoted-diagnostic exclusion removed and behavior regressed.** `skills/clear-technical-writing/SKILL.md:8-10` replaces explicit `raw tool output, logs, or quoted diagnostics` boundary with `raw/schema-constrained output, log interpretation`. Contract still excludes quoted diagnostics at `docs/v1-acceptance-contract.md:83-92`; README agrees at `README.md:152-160`. Targeted Pi probe using `github-copilot/gemini-3.6-flash:low` loaded skill for `Rewrite this quoted diagnostic to sound clearer: "ERROR E731: shard quorum unavailable"` (`entry_reads=1`). Negative activation permits zero loads. Restore explicit raw-tool/log/quoted-diagnostic boundary. Current router test at `tests/test_skill_router.py:60-72` omits these exclusions, so test cannot catch regression.

### Correct

- **Correct — adjudicated outcomes match summary.** Added regression at `tests/test_eval_metrics.py:143-177` and direct report dump show all 12 `evaluator_false_positive` cases pass; all 6 `genuine_failure` cases fail. Genuine cases retain upheld failure signals: cases 03-04 container/source equality, case 05 source equality, cases 07-08 protected count, case 09 unknown cause.
- **Correct — protected handling made operational in instructions.** `skills/clear-technical-writing/SKILL.md:63-65` requires one-to-one mapping, forbids repeats in common generated sections, and forbids inline/fence moves. `skills/clear-technical-writing/references/semantic-preservation.md:138-145` requires value/count/container/role inventory and rejection of added, removed, duplicated, or moved occurrences.
- **Correct — frontmatter shorter and target routing improved.** Folded description shrank 645 to 498 characters and explicitly names incident reports plus root-cause/correlation findings at `skills/clear-technical-writing/SKILL.md:4-7`. Positive one-shot Pi probes for incident correlation and root-cause rewrites both loaded skill. Patch-summary writing-pass probe also loaded; code-review negative did not.
- **Correct — size gate passes.** `SKILL.md` is 3,991 bytes, within 4,000-byte cap enforced at `tests/test_skill_router.py:74-75`.
- **Correct — original recorded outputs stay unchanged.** Git status under `evals/results/independent-review/` shows only documented append to `RUN-NOTES.md`; raw cells, `results.json`, `failures.json`, `RESULTS.md`, generation log, and adjudication files are clean. `RUN-NOTES.md:37-46` explicitly records post-run adjudication and says preregistered result is not retroactively changed.
- **Correct — diff focused.** Six changed files all relate to scorer adjudication, routing/protected guidance, tests, or run notes. No staged files. `git diff --check` clean.
- **Correct — focused and full suites pass.** Focused: 33 tests. Full: 148 tests.

### Nonblocking risks

- **Medium — tests assert verdict booleans, not upheld reason IDs.** `tests/test_eval_metrics.py:172-177` could keep a genuine case red solely through unrelated false-positive rules. Cases 03-05 currently still report adjudicated false-positive rule IDs alongside genuine failures. Assert expected upheld IDs per genuine case.
- **Medium — sibling coverage too narrow.** `tests/test_eval_metrics.py:96-141` covers six obvious Helios/greenhouse phrases but no broker disproof sibling and no negated admitted paraphrase. Blocker probes demonstrate gap.
- **Low — activation probes are one run each on one model.** Useful targeted evidence, not acceptance-threshold rerun. After frontmatter fix, run three repetitions per changed positive/negative prompt; negative quoted diagnostic must remain 0/3, positives need at least 2/3.
- **Low — 9-byte budget margin.** 3,991-byte file leaves little room for exclusion fix. Compress elsewhere while retaining explicit contract terms.

### Targeted activation probe results

`github-copilot/gemini-3.6-flash:low`, isolated Pi JSON mode, explicit-only skill discovery, read-only tool:

| Probe | Expected | Observed |
|---|---:|---:|
| Incident correlation rewrite | load | loaded; 1 entrypoint read |
| Root-cause rewrite | load | loaded; 1 entrypoint read |
| Patch summary with writing-pass request | load | loaded; 1 entrypoint read |
| Quoted diagnostic rewrite | no load | **loaded; regression** |
| Code review | no load | not loaded |

## Required next steps

1. Tighten line 70 causal-scope pattern, line 127 modal pattern, and line 209 correlation neutrality check.
2. Add failing regression texts from blocker probes.
3. Restore explicit `raw tool output`, `logs`, and `quoted diagnostics` frontmatter exclusions; retain writing-pass exception for patch summaries.
4. Re-run focused/full tests and 3x targeted activation probes.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Concrete blocker and risk findings cite SKILL.md:8-10, independent-review.json:70/127/203/209, test_eval_metrics.py:96-177, and contract/README boundaries; direct regression probes included."
    }
  ],
  "changedFiles": [
    "evals/fixtures/independent-review.json",
    "evals/results/independent-review/RUN-NOTES.md",
    "skills/clear-technical-writing/SKILL.md",
    "skills/clear-technical-writing/references/semantic-preservation.md",
    "tests/test_eval_metrics.py",
    "tests/test_skill_router.py"
  ],
  "testsAddedOrUpdated": [
    "tests/test_eval_metrics.py",
    "tests/test_skill_router.py"
  ],
  "commandsRun": [
    {
      "command": "python3 -m unittest tests.test_eval_metrics tests.test_skill_router -v",
      "result": "passed",
      "summary": "33 focused tests passed."
    },
    {
      "command": "python3 -m unittest discover -s tests -v",
      "result": "passed",
      "summary": "148 full-suite tests passed."
    },
    {
      "command": "wc/diff/frontmatter size checks plus git diff --check",
      "result": "passed",
      "summary": "SKILL.md 3991 bytes; description 498 chars versus 645 at HEAD; diff check clean."
    },
    {
      "command": "adjudication scorer dump for all 18 summary cases",
      "result": "passed",
      "summary": "12/12 evaluator false positives passed; 6/6 genuine failures failed."
    },
    {
      "command": "custom semantic sibling probes against HEAD and worktree fixtures",
      "result": "failed",
      "summary": "Worktree incorrectly passed Helios negated cause, broker disproved link, and greenhouse negated duration; HEAD rejected each."
    },
    {
      "command": "five isolated Pi activation probes with github-copilot/gemini-3.6-flash:low",
      "result": "failed",
      "summary": "Incident/root-cause/writing-pass positives loaded and code-review negative stayed unloaded, but quoted-diagnostic negative loaded."
    }
  ],
  "validationOutput": [
    "GO/NO-GO: NO-GO for commit.",
    "All adjudicated target outcomes match 12 pass / 6 fail.",
    "Three newly admitted semantic contradictions pass full gate.",
    "Quoted-diagnostic negative activation loaded skill.",
    "Original raw/results/failures/RESULTS artifacts unchanged; RUN-NOTES append documents adjudication."
  ],
  "residualRisks": [
    "Genuine-failure test checks only gate false, not adjudication-upheld failure IDs.",
    "Forbidden-sibling tests omit broker disproof and negated modal/causal variants.",
    "Activation evidence is single-run, single-model targeted probing.",
    "SKILL.md has only 9 bytes remaining under cap."
  ],
  "noStagedFiles": true,
  "diffSummary": "Scorer regex relaxations for 12 adjudicated false positives; shorter router frontmatter; explicit one-to-one protected handling; adjudication/run-note and regression-test additions.",
  "reviewFindings": [
    "blocker: evals/fixtures/independent-review.json:70,127,209 - widened regexes admit contradictory cause, link, and modality rewrites",
    "blocker: skills/clear-technical-writing/SKILL.md:8-10 - quoted-diagnostic exclusion removed; live negative probe activates skill",
    "note: tests/test_eval_metrics.py:96-177 - sibling and genuine-reason assertions are incomplete",
    "note: skills/clear-technical-writing/SKILL.md - size passes at 3991 bytes but margin is 9 bytes"
  ],
  "manualNotes": "Review-only: no source files edited. Findings artifact written to required runtime path."
}
```
