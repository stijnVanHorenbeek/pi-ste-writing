# Official-STE-supported semantic adjudication

Date: 2026-08-10
Status: post-run diagnostic; does not alter preregistered acceptance

## Scope and authority

This review covers all 127 deterministic semantic-rule flags in successful native-skill and guarded release-candidate cells. One reviewer examined each scenario. Two fresh reviewers then independently challenged all proposed genuine, ambiguous, and major false-positive families.

The user-provided ASD-STE100 Issue 9 PDF at `~/Downloads/ASD-STE100_ISSUE9.pdf` was consulted locally. It is not copied into this repository or package. Page references below are PDF page numbers.

Official guidance supports, but does not replace, source-relative semantic review:

- Page 47: replacement words must not change sentence meaning.
- Rule 1.11, page 57: do not use different technical nouns for the same item.
- Rule 9.1, pages 115-116: use a different sentence construction when word-for-word replacement is insufficient; alternatives must not change meaning.
- Rule 9.4, page 122: use terminology and wording consistently.

ASD-STE100 is not an arbitrary semantic-equivalence oracle. The source fixture remains authoritative for facts, causality, modality, actors, permissions, prohibitions, technical roles, and procedure safety. This review does not certify ASD-STE100 compliance.

## Final classification

| Classification | Flag occurrences | Share |
|---|---:|---:|
| Deterministic-scorer false positive | 97 | 76.4% |
| Protected occurrence/container contract only | 16 | 12.6% |
| Genuine semantic or source-fidelity change | 9 | 7.1% |
| Ambiguous | 5 | 3.9% |
| **Total** | **127** | **100%** |

Nine genuine flag occurrences represent seven underlying semantic changes in six outputs because two recommendation-strengthening defects each triggered two complementary rules.

Sixteen protected-contract flags represent eight underlying occurrence/container changes. Reviewers found no changed proposition in those cases, but the outputs still violate the package's exact protected-content contract.

## Rule-family disposition

| Rule family | False positive | Contract only | Genuine | Ambiguous |
|---|---:|---:|---:|---:|
| `morrow.confirmed-mica` | 12 | 0 | 0 | 0 |
| `morrow.unknown-31` | 8 | 0 | 0 | 0 |
| `morrow.two-sided-boundary` | 8 | 0 | 2 | 1 |
| `morrow.solvent-exclusion` | 0 | 0 | 0 | 1 |
| `sablefen.combined-permission` | 9 | 0 | 0 | 0 |
| `sablefen.no-duty` | 3 | 0 | 0 | 0 |
| `sablefen.inactive-override` | 4 | 0 | 0 | 0 |
| `sablefen.runner-scope` | 1 | 0 | 0 | 2 |
| `sablefen.forbidden-photo-duty` | 0 | 0 | 2 | 0 |
| `sablefen.photo-recommendation` | 0 | 0 | 2 | 0 |
| `sablefen.lock-obligation` | 0 | 0 | 1 | 0 |
| `sablefen.identifiers` | 0 | 2 | 0 | 0 |
| Sablefen `protected.source-equality` | 0 | 2 | 0 | 0 |
| `calder.scope` | 0 | 0 | 1 | 0 |
| `brineglass.terms` | 16 | 0 | 0 | 0 |
| `brineglass.pipeline` | 2 | 0 | 0 | 0 |
| `brineglass.protected` | 0 | 1 | 0 | 0 |
| Brineglass `protected.source-equality` | 0 | 1 | 0 | 0 |
| `mireglass.no-failure-claim` | 15 | 0 | 0 | 1 |
| `mireglass.retained-estimate` | 10 | 0 | 0 | 0 |
| `mireglass.restart-effect` | 7 | 0 | 0 | 0 |
| `mireglass.restart-prohibition` | 2 | 0 | 0 | 0 |
| `mireglass.release-trigger` | 0 | 5 | 0 | 0 |
| Mireglass `protected.source-equality` | 0 | 5 | 0 | 0 |
| `mireglass.inspect-recommendation` | 0 | 0 | 1 | 0 |
| **Total** | **97** | **16** | **9** | **5** |

## Genuine changes

### Morrowglass: causal boundary strengthened

Files:

- `openai-codex_gpt-5.6-sol_high__native-skill__morrowglass-rejection-analysis__r01.json`
- `openai-codex_gpt-5.6-sol_high__native-skill__morrowglass-rejection-analysis__r03.json`

The source says evidence does not confirm full causation and does not exclude a causal contribution. The outputs apply both uncertainty verbs to “contributing cause,” additionally denying confirmation of contribution. This collapses two different causal thresholds.

### Sablefen: recommendation became obligation

Files:

- `github-copilot_claude-sonnet-5_low__native-skill__sablefen-drawer-access-policy__r02.json`
- `github-copilot_claude-sonnet-5_low__native-skill__sablefen-drawer-access-policy__r03.json`

The source says the curator `should` photograph the seal. Both outputs say the curator `must` photograph it. Each change triggered `sablefen.forbidden-photo-duty` and `sablefen.photo-recommendation`.

### Sablefen: responsible actor removed

File:

- `github-copilot_claude-sonnet-5_low__native-skill__sablefen-drawer-access-policy__r02.json`

The source assigns curators responsibility for keeping the drawer locked. The output states only that the drawer must stay locked. Required state remains, but explicit accountability is lost.

### Calder: factual guarantee became instruction

File:

- `github-copilot_claude-sonnet-5_low__native-skill__calder-anti-rollback-fuse-procedure__r03.json`

The source states that the procedure does not alter active spectrometer `QW-88K`. The output says not to alter it. A factual assurance became an operator prohibition.

### Mireglass: recommendation became required action

File:

- `github-copilot_claude-sonnet-5_low__native-skill__mireglass-holdover-service-notice__r03.json`

The source says technicians `should inspect` after the threshold. The output places an imperative inspection step under “Required actions.”

## Protected-contract-only changes

- Two OpenAI native Sablefen outputs replace the second inline `D-19` occurrence with a clear coreference such as “the drawer.” Meaning remains recoverable; exact identifier occurrence count fails.
- One Claude native Brineglass output changes first occurrences of `sounding` and `tracing` from inline code to quotation marks. Definitions remain intact; protected containers fail.
- Five native Mireglass outputs repeat inline-code `holdover` more often than the source. Meaning remains consistent; exact occurrence counts fail. Fixture-specific and generic rules report each underlying change twice.

## Ambiguous cases

- Claude native Morrowglass r02 changes the subject from all “evidence” to “this timing,” possibly narrowing evidentiary scope.
- OpenAI native Morrowglass r02 omits the explicit “alarm increase” scope after excluding solvent carryover; local context may recover it.
- Claude native Sablefen r02 changes `can`/`must not` to `may`/`may not`; policy context supports permission/prohibition, but literal modal scope changes.
- Claude native Sablefen r03 changes capability `can view` to permission `may view`.
- Claude native Mireglass r03 changes “does not say the probe failed” to “does not indicate probe failure,” possibly strengthening absence of assertion into absence of diagnostic evidence.

## False-positive pattern diagnosis

The 97 false-positive flags primarily come from lexical and order-sensitive patterns:

- `21 of 52` rejected when rendered as `21 of the 52` or when denominator remained clear in adjacent context.
- `means` rejected when rendered as `refers to` or `defines` without changing term-to-concept mapping.
- Read/write pipeline roles rejected when API field order changed but actor, action, data, path, and field stayed intact.
- `keeps showing` rejected as `continues displaying`.
- `may remove` rejected as `may clear`.
- Equivalent conditions rejected because of `once`, `but only`, punctuation, clause order, or an extra article.
- Explicit optionality and inactive-permit overrides rejected outside narrow phrase windows.

The official guide supports preserving meaning and terminology; it does not support treating one surface phrase as the only valid realization.

## Release disposition

This adjudication is diagnostic only. It does not rewrite raw evidence, change the preregistered scorer, or convert the failed run into a pass. Current release acceptance remains failed, and the blind quality judge remains blocked.

Any scorer or package changes must treat these scenarios as development regressions and must be evaluated in a new preregistered benchmark with genuinely new held-out scenarios.
