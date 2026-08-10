# Hardening release candidate run notes

## Status

This release candidate failed frozen deterministic source gates. Blind semantic and quality judging did not run. Publication remains blocked.

Preregistered package snapshot:

- Commit: `11678942691506a2a61c4c825f9e36985322d86e`.
- Matrix SHA-256: `6aa0649d56cc8a04b141d686e1f0b2d57e0b9ee880a9cbfb146e1af02391d2d1`.
- Corpus SHA-256: `d418b4c380de69c69f9b78ea57870721d72903214aa3b0a64220041ffeeb78e1`.
- Structured scenario SHA-256: `34813b7d6f9577b40eec257c4bb346e5c6113a2336bcd4e0fc6cb535bbc980a6`.
- Judge config SHA-256: `831a8b9f1bc0c79d59a9837d7a14be93a98e88bfbdb2b0a1eab92a1e20232b3b`.
- Runner version: 11.
- Pi version: 0.84.1.
- Package tree was clean.

## Pre-generation controls

A first non-candidate-authored draft set was discarded before preregistration because its final author receipt exposed broad domain metadata to a candidate-model parent. No candidate generation used that set. A fresh non-candidate author created a materially disjoint replacement and compared it against both tracked fixtures and discarded draft. Independent non-candidate semantic/novelty and mechanical reviews returned GO with no blocker or major findings. Exact replacement source and task text was not exposed to candidate models before generation.

The frozen development smoke used known evidence and passed 3/3 cells with guard integrity 3/3. Smoke evidence is in `evals/results/hardening-release-candidate-development-smoke/` and does not count as release evidence.

## Generation result

Generation completed 151/153 expected cells.

- Completeness: 151/153; two failed cells.
- Condition integrity: not accepted.
- Model identity: 151/153.
- Routing safety: 151/153.
- Positive activation groups: 17/18.
- Objective contract: 96/99 passed expected applicable cells; one successful applicable cell failed and two cells were missing because of terminal routing failures.
- Procedure contract: 18/18.
- Gated output contract: 88/90; zero successful gated cells failed, and two cells were missing.
- Guard integrity: 45/45 exact accepted artifacts.
- Diagnostic structured output: 3/9; diagnostic only.

### Terminal routing failures

Both terminal failures were `github-copilot/gemini-3.6-flash:medium`, `native-skill`, `obsidian-sonar-anomaly`, repetitions 2 and 3.

Each cell used both configured attempts. All four attempts had the same privacy-safe routing signature:

- Skill loaded: true.
- Read calls: 3.
- Successful reads inside skill tree: 2.
- Failed reads: 1.
- Failed-read scope: `outside-skill`.
- Failed path SHA-256: `38d22c94e5c307b4ff604038eea33e60f057f6c12bb978c086b13a484ccf6096`.
- Error: `Model identity or routing safety did not pass.`

No plaintext failed path or candidate output is reproduced here. The repeated hash shows one stable attempted path across both repetitions and all configured attempts. Failed cells are permanent evidence and were not rerun as fresh jobs.

### Objective contract failure

One otherwise successful applicable cell failed `required-literal.inline_code`: `github-copilot/claude-sonnet-5:low`, `native-skill`, `cedar-ventilation-threshold`, repetition 2. This is a frozen protected-container failure. It was not repaired or rescored.

Baseline objective and structured-output diagnostics also contain failures, but baseline and diagnostic serialization do not gate acceptance. They cannot override or repair source-gate failures.

## Judge boundary

No `evals/results/hardening-release-candidate-judge/` directory exists. Judge calls were blocked because completeness, condition integrity, objective acceptance, and gated output-contract completeness did not pass. No preference or semantic judgment can override these deterministic failures.

## No retrospective repair

This candidate is permanently failed evidence. Do not rerun failed cells, change retries, alter fixtures/configs/package/scorers, rescore outputs, or invoke the blind judge for acceptance. Observed scenarios may become development regressions only.

Package remains private and unpublished. A future release attempt requires genuinely new held-out content, fresh independent review and preregistration, and explicit authorization.
