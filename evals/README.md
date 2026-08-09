# V1 evaluation

V1 uses a preregistered Pi matrix, closed-world semantic fixtures, deterministic scoring, and blind independent review. It does not claim ASD-STE100 certification or complete open-prose equivalence.

## Preregistered matrix

`v1-matrix.json` fixes six scenario IDs, three conditions, three models with explicit providers and thinking levels, and three repetitions. Five scenarios use closed-world semantic fixtures; one checks an exact schema-constrained JSON contract. Every model, condition, and scenario needs three successful samples. Version 2 lowered Claude Sonnet 5 from medium to low thinking to reduce GitHub Copilot cost. Version 3 records evidence-driven fixture, output-contract, and modal-preservation corrections after first completed run.

Conditions:

- `baseline`: no writing skill and no model-callable tools.
- `native-skill`: Pi loads only `clear-technical-writing`; model can use only `read` so progressive skill loading works.
- `direct-prompt`: complete `SKILL.md` text is injected with skills and tools disabled. This condition is diagnostic, not a substitute for native loading.

Version 3 makes `native-skill` the package acceptance gate. Baseline and direct-prompt remain complete diagnostic controls: their failures stay authoritative for those outputs and visible in reports, but expected control failures do not veto package release.

Matrix changes require a versioned amendment with a recorded reason. Raw results store the matrix SHA-256, so results from changed matrices cannot be silently reused.

## Run

Commit all source changes first. Generation requires a clean Git working tree because each raw cell records exact package commit and Pi version.

```bash
python3 evals/run_pi_bench.py \
  --matrix evals/v1-matrix.json \
  --results-dir evals/results/v1
```

Rebuild reports without model calls:

```bash
python3 evals/run_pi_bench.py \
  --matrix evals/v1-matrix.json \
  --results-dir evals/results/v1 \
  --report-only
```

Exit 0 means matrix complete with accepted condition-integrity and semantic gates. Exit 1 means evidence is incomplete or a required gate failed. Invocation or configuration errors exit 2.

## Isolation

Matrix controls tools, extensions, skills, prompt templates, themes, context files, sessions, project trust, and Pi startup networking. V1 disables ambient resources, persistent sessions, project trust, and startup network checks. Provider requests still run. Native condition explicitly loads package skill and allows only `read`.

Each call uses an empty temporary working directory. Baseline and adapted conditions receive same task input and system prompt.

## Resume and raw evidence

Existing matching successful cells are skipped. Failed cells keep attempt history and retry on next run. Raw reuse requires identical cell identity, runner version, matrix hash, package commit, dirty state, and Pi version. Stale results remain visible and are not overwritten.

Each successful raw cell records:

- Requested and returned provider/model identity.
- Thinking level.
- Input, provider output, reasoning, visible-output, cache, and total token metadata with explicit availability.
- Cost and duration.
- Native skill-read evidence.
- Deterministic semantic, procedure, Exact output-contract, and advisory style results.

Unavailable reasoning metadata remains `null`; provider output counts include reasoning where Pi reports that relationship. Hidden reasoning content is never stored. Non-stop partial outputs remain in failed-attempt records and receive separate aggregate failure evidence.

## Reports

`results.json` and `RESULTS.md` report semantic metrics before style metrics. Semantic and exact output-contract failures remain authoritative. Style findings cannot override them. Usage, cost, duration, population standard deviation, routing evidence, and unresolved cells follow.

`failures.json` lists failed, missing, stale, and invalid cells. Incomplete matrices block final benchmark claims.

Exact output-contract checks support plain-text framing rules and schema-constrained JSON objects with required keys, additional-property control, and property types.

## Independent quality judge

Run judging only after benchmark generation completes. Source benchmark must come from a clean package commit, and judge generation must use same matrix and skill snapshot. Evaluator-only fixes can use a newer clean commit; reports record both commits:

```bash
python3 evals/run_quality_judge.py \
  --config evals/quality-judge.json \
  --matrix evals/v1-matrix.json \
  --benchmark-results-dir evals/results/v1 \
  --results-dir evals/results/v1/judge
```

Rebuild judge reports without model calls:

```bash
python3 evals/run_quality_judge.py \
  --benchmark-results-dir evals/results/v1 \
  --results-dir evals/results/v1/judge \
  --report-only
```

`quality-judge.json` preregisters two comparisons for every model, scenario, and source repetition:

- `baseline-vs-native` is primary skill comparison.
- `baseline-vs-direct-prompt` is diagnostic comparison.

Three source repetitions provide repeated samples. First two repetitions swap candidate order; later orders use deterministic hashing. Judge receives only task, source, and labels `Candidate A` and `Candidate B`. Condition, generator model, and provider stay out of judge prompt.

Current mappings use a different provider from source generator: OpenAI-generated candidates use Gemini 3.6 Flash at low thinking through GitHub Copilot; GitHub Copilot-generated candidates use OpenAI. Judge config version 2 made this change before first run to reduce GitHub Copilot cost. V1 expects 108 judgments: 3 generator models × 2 comparisons × 6 scenarios × 3 source repetitions.

Rubric scores each candidate from 1–5, or marks dimension not applicable:

- Factual and semantic fidelity.
- Task completion and completeness.
- Correct uncertainty and obligation.
- Technical terminology.
- Safety and actionability.
- Readability and concision.

Before judging or reporting, runner recomputes source completeness, condition integrity, and semantic acceptance from benchmark raw cells and rejects aggregate mismatches. Judge verdict transport accepts raw JSON or one enclosing `json` code fence, then enforces exact object schema. Raw judge cells retain blind assignment, candidate and prompt hashes, provider identity, usage/cost metadata, attempts, verdict, and unblinded outcome. Existing valid successes resume without calls. Failed or invalid verdicts remain visible and retry within configured limit.

Reports keep deterministic semantic authority separate from ordinal judge preference. If one candidate fails deterministic semantic or output-contract gates, passing candidate wins regardless of judge preference. If both fail, neither wins. Judge-reported semantic, task, modality, terminology, or safety blockers require human resolution and suppress preference-based acceptance.

Exit 0 requires complete cross-provider judgments, accepted source semantic and condition-integrity gates, and zero unresolved judge blockers. Exit 1 means evidence remains incomplete or unaccepted. Configuration and invocation errors exit 2.

### Judge limits

Model judging is not ground truth. Blind labels reduce but do not eliminate positional, style, or treatment-identification bias. Cross-provider review reduces shared-provider bias but does not prove independence. Scores do not prove semantic equivalence or ASD-STE100 compliance. Deterministic failures remain authoritative, and judge blockers require human review before release claims.

## Limits

Deterministic patterns cover declared fixture properties only. New claims and open prose still need attested source review. Provider costs are metadata, not billing records. Runner never requests or stores hidden reasoning content.
