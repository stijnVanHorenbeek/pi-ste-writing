# Strict STE rule map

This catalog adapts the ASD-STE100 Issue 9 rule mapping published by the upstream
project. It is not the official rule text.

## Application boundary

Apply `references/semantic-preservation.md` before this catalog. Technical correctness,
source meaning, safety, user intent, modality, and repository terminology override every
style rule here.

Use the complete catalog only in strict STE mode, after an explicit request for STE or
an STE-oriented audit. A document can contain descriptive and procedural passages.
Classify each passage separately; do not force one mode onto the full document.

For an existing source, report a rule conflict instead of making a semantically unsafe
rewrite. Preserve protected content and exact technical names, including identifiers,
commands, paths, API fields, UI labels, product names, and established domain terms.

Rule 5.4 applies only when an action-controlling condition governs a procedural command.
It does not require moving a descriptive condition, a condition inside quoted text, or a
condition in code or machine-readable data.

## Strict STE requirements versus software guidance

| Topic | Strict STE use | Pragmatic software guidance |
|---|---|---|
| Vocabulary and word forms | Check Rules 1.1-1.14, 3.1-3.5, and 9.2 against the official dictionary. | Preserve repository terminology and improve surrounding prose. |
| Sentence length | Enforce Rules 5.1 and 6.3 after semantic checks. | Prefer concise prose; do not split sentences when the split changes scope or logic. |
| Procedures | Apply Rules 5.1-5.5 to each procedural passage. | Use imperatives, one action per step, and condition-first commands when safe. |
| Descriptions | Apply Rules 6.1-6.6 to each descriptive passage. | Group related facts and make evidence relationships explicit. |
| Safety text | Apply Rules 7.1-7.3 without lowering or inventing a risk level. | Put the warning before a dangerous operation; put the command before its consequence inside the warning. |
| Punctuation and counting | Apply Rules 8.1-8.7 during strict verification. | Follow repository and output-contract formatting. |
| Terminology | Treat valid domain words under Rules 1.5, 1.8, and 1.12. | Keep exact technical names and distinct project concepts unchanged. |

### Software warning order

For destructive commands and other dangerous software operations:

1. Put the warning block before the dangerous operation.
2. Put each action-controlling condition before its command.
3. Put the required command before the risk or possible consequence.

Preserve the source risk level and repository warning convention. Do not invent a formal
signal-word classification when the source does not establish one.

### Unsafe as a global coding-agent default

Do not apply these strict transformations automatically to normal coding work:

- Dictionary-driven substitutions can change facts, modality, or domain meaning.
- Hard 20-word and 25-word limits can break logical scope or exact output contracts.
- The three-word noun limit can damage established product and API names.
- American English spelling can conflict with repository style or quoted text.
- A global condition-first pass can corrupt descriptive prose, code, and schemas.
- Strict punctuation and verb-form restrictions can make technical explanations less
  precise.

Modal replacement is especially unsafe. Do not change `should` to `must` when the source
states a recommendation. Do not change `may` to `can` when the source states permission
or uncertain possibility. If no strict rewrite preserves the distinction, retain the
source modal and report the unresolved strict-rule conflict.

## Section 1: Words

| Rule | Local paraphrase |
|---|---|
| 1.1 | Use an approved word, a technical noun, or a technical verb. |
| 1.2 | Use an approved word only as its approved part of speech. |
| 1.3 | Use an approved word only with its approved meaning. |
| 1.4 | Use only approved forms of verbs and adjectives. |
| 1.5 | A domain-specific word can be a technical noun. |
| 1.6 | Use an unapproved word only as a technical noun or part of one. |
| 1.7 | Do not use a technical noun as a verb. |
| 1.8 | Use technical nouns established by the applicable project or industry. |
| 1.9 | Prefer a short, clear technical noun when you can choose its name. |
| 1.10 | Do not use regional language, slang, or jargon as a technical noun. |
| 1.11 | Use one name for one item or concept. |
| 1.12 | A domain-specific word can be a technical verb. |
| 1.13 | Do not use a technical verb as a noun. |
| 1.14 | Use American English spelling. |

## Section 2: Multi-word nouns

| Rule | Local paraphrase |
|---|---|
| 2.1 | Keep a multi-word noun to three words or fewer. |
| 2.2 | For a longer technical noun, give its full form once and then use an approved short form or hyphenation. |

## Section 3: Verbs

| Rule | Local paraphrase |
|---|---|
| 3.1 | Use only verb forms supplied by the approved dictionary entry. |
| 3.2 | Limit verbs to the infinitive, imperative, simple present, simple past, simple future, or adjectival past participle. |
| 3.3 | Use a past participle only as an adjective. |
| 3.4 | Do not use auxiliary verbs to make complex verb constructions. |
| 3.5 | Use an `-ing` form only as a technical noun or part of one, not as a verb. |
| 3.6 | Use active voice; descriptive text can use passive voice when the agent is unknown. |
| 3.7 | Express an action with a verb instead of an action noun. |

## Section 4: Sentences

| Rule | Local paraphrase |
|---|---|
| 4.1 | Write sentences that are short and clear. |
| 4.2 | Do not omit required words or use contractions to shorten a sentence. |
| 4.3 | Put complex material in a vertical list. |
| 4.4 | Use explicit connecting words between related sentences. |
| 4.5 | Use an article or demonstrative adjective before a noun when grammar requires one. |

## Section 5: Procedural writing

| Rule | Local paraphrase |
|---|---|
| 5.1 | Limit each procedural sentence, including a warning or caution, to 20 words. |
| 5.2 | Give one instruction per sentence unless actions must occur at the same time. |
| 5.3 | Write instructions in the imperative. |
| 5.4 | Put an action-controlling condition before its instruction and separate it with a comma. |
| 5.5 | Put information, not instructions, in a note; apply the descriptive sentence limit to notes. |

## Section 6: Descriptive writing

| Rule | Local paraphrase |
|---|---|
| 6.1 | Introduce information gradually, with one new fact per sentence. |
| 6.2 | Use key words and phrases to make the logical structure visible. |
| 6.3 | Limit each descriptive sentence to 25 words. |
| 6.4 | Put related information in the same paragraph. |
| 6.5 | Keep one topic in each paragraph. |
| 6.6 | Limit a paragraph to six sentences. |

## Section 7: Safety instructions

| Rule | Local paraphrase |
|---|---|
| 7.1 | Use the specified signal word to identify the risk level. |
| 7.2 | Begin with a clear command, or with a condition that is followed by its command. |
| 7.3 | Give the risk or possible result after the required command. |

## Section 8: Punctuation and word count

| Rule | Local paraphrase |
|---|---|
| 8.1 | Use standard punctuation except the semicolon. |
| 8.2 | Use hyphens to connect words that function as one unit. |
| 8.3 | Use parentheses only for permitted content such as references, item numbers, abbreviations, plurals, explanations, or alternatives. |
| 8.4 | For word counting, treat the lead-in before a vertical list as a complete sentence. |
| 8.5 | Count text inside one pair of parentheses as one word. |
| 8.6 | Count each number, number with a unit, abbreviation, alphanumeric identifier, quotation, title, label, or proper noun as one word. |
| 8.7 | Count a hyphenated term as one word. |

## Section 9: Writing practices

| Rule | Local paraphrase |
|---|---|
| 9.1 | Restructure a sentence when word-for-word substitution does not work. |
| 9.2 | Use each approved word with its approved meaning and part of speech. |
| 9.3 | Do not make phrasal verbs. |
| 9.4 | Keep terminology and writing style consistent through the document. |

## General recommendations

These recommendations support strict review but are not part of the 53 numbered rules.

| ID | Local paraphrase |
|---|---|
| GR-1 | Keep the conjunction `that`. |
| GR-2 | Use `with` only when its relationship is unambiguous. |
| GR-3 | Give every pronoun a clear referent. |
| GR-4 | Prefer `this` with a noun instead of bare `this`. |
| GR-5 | Avoid words that can mislead readers because of false similarity across languages. |
| GR-6 | Replace Latin abbreviations with explicit English; do not leave an open-ended `etc.` list. |
| GR-7 | Use inclusive language. |
| GR-8 | Use a possessive apostrophe only when its construction is clear and correct. |

For software prose, GR-1, GR-3, GR-4, and GR-6 often improve clarity without changing
meaning. The semantic and terminology boundaries still apply.

## Dictionary and verification limits

The official ASD-STE100 dictionary is not included in this package.
No official dictionary entries are reproduced. Obtain the official Issue 9 standard and dictionary
from [ASD](https://www.asd-ste100.org/request.html) for vocabulary review.

Do not infer dictionary approval from this catalog, the linter, or model knowledge.
Without the official dictionary, Rules 1.1-1.4, 3.1, and 9.2 cannot receive a complete
word-level check. A software term can qualify as a technical noun or technical verb, but
that classification does not approve unrelated general vocabulary.

A strict audit must separate:

- Deterministic findings, such as sentence counts and protected-text differences.
- Judgment findings, such as passage classification and active-voice exceptions.
- Dictionary-dependent findings that require the official standard.
- Semantic conflicts where a source-faithful rewrite retains a strict-rule violation.

This package, its linter, and its review process cannot certify ASD-STE100 compliance.
For every compliance-oriented audit, include this disclaimer:

> This audit is advisory and cannot certify ASD-STE100 compliance. Final approval rests
> with the writer using the official standard and dictionary.
