import re
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = (
    ROOT
    / "skills"
    / "clear-technical-writing"
    / "references"
    / "ste-rules.md"
)
EXPECTED_RULES = {
    *(f"1.{number}" for number in range(1, 15)),
    *(f"2.{number}" for number in range(1, 3)),
    *(f"3.{number}" for number in range(1, 8)),
    *(f"4.{number}" for number in range(1, 6)),
    *(f"5.{number}" for number in range(1, 6)),
    *(f"6.{number}" for number in range(1, 7)),
    *(f"7.{number}" for number in range(1, 4)),
    *(f"8.{number}" for number in range(1, 8)),
    *(f"9.{number}" for number in range(1, 5)),
}
EXPECTED_PARAPHRASES = {
    "1.1": "Use an approved word, a technical noun, or a technical verb.",
    "1.2": "Use an approved word only as its approved part of speech.",
    "1.3": "Use an approved word only with its approved meaning.",
    "1.4": "Use only approved forms of verbs and adjectives.",
    "1.5": "A domain-specific word can be a technical noun.",
    "1.6": "Use an unapproved word only as a technical noun or part of one.",
    "1.7": "Do not use a technical noun as a verb.",
    "1.8": "Use technical nouns established by the applicable project or industry.",
    "1.9": "Prefer a short, clear technical noun when you can choose its name.",
    "1.10": "Do not use regional language, slang, or jargon as a technical noun.",
    "1.11": "Use one name for one item or concept.",
    "1.12": "A domain-specific word can be a technical verb.",
    "1.13": "Do not use a technical verb as a noun.",
    "1.14": "Use American English spelling.",
    "2.1": "Keep a multi-word noun to three words or fewer.",
    "2.2": (
        "For a longer technical noun, give its full form once and then use an "
        "approved short form or hyphenation."
    ),
    "3.1": "Use only verb forms supplied by the approved dictionary entry.",
    "3.2": (
        "Limit verbs to the infinitive, imperative, simple present, simple past, "
        "simple future, or adjectival past participle."
    ),
    "3.3": "Use a past participle only as an adjective.",
    "3.4": "Do not use auxiliary verbs to make complex verb constructions.",
    "3.5": (
        "Use an `-ing` form only as a technical noun or part of one, not as a verb."
    ),
    "3.6": (
        "Use active voice; descriptive text can use passive voice when the agent "
        "is unknown."
    ),
    "3.7": "Express an action with a verb instead of an action noun.",
    "4.1": "Write sentences that are short and clear.",
    "4.2": (
        "Do not omit required words or use contractions to shorten a sentence."
    ),
    "4.3": "Put complex material in a vertical list.",
    "4.4": "Use explicit connecting words between related sentences.",
    "4.5": (
        "Use an article or demonstrative adjective before a noun when grammar "
        "requires one."
    ),
    "5.1": (
        "Limit each procedural sentence, including a warning or caution, to 20 words."
    ),
    "5.2": (
        "Give one instruction per sentence unless actions must occur at the same time."
    ),
    "5.3": "Write instructions in the imperative.",
    "5.4": (
        "Put an action-controlling condition before its instruction and separate "
        "it with a comma."
    ),
    "5.5": (
        "Put information, not instructions, in a note; apply the descriptive "
        "sentence limit to notes."
    ),
    "6.1": "Introduce information gradually, with one new fact per sentence.",
    "6.2": "Use key words and phrases to make the logical structure visible.",
    "6.3": "Limit each descriptive sentence to 25 words.",
    "6.4": "Put related information in the same paragraph.",
    "6.5": "Keep one topic in each paragraph.",
    "6.6": "Limit a paragraph to six sentences.",
    "7.1": "Use the specified signal word to identify the risk level.",
    "7.2": (
        "Begin with a clear command, or with a condition that is followed by its command."
    ),
    "7.3": "Give the risk or possible result after the required command.",
    "8.1": "Use standard punctuation except the semicolon.",
    "8.2": "Use hyphens to connect words that function as one unit.",
    "8.3": (
        "Use parentheses only for permitted content such as references, item "
        "numbers, abbreviations, plurals, explanations, or alternatives."
    ),
    "8.4": (
        "For word counting, treat the lead-in before a vertical list as a complete "
        "sentence."
    ),
    "8.5": "Count text inside one pair of parentheses as one word.",
    "8.6": (
        "Count each number, number with a unit, abbreviation, alphanumeric "
        "identifier, quotation, title, label, or proper noun as one word."
    ),
    "8.7": "Count a hyphenated term as one word.",
    "9.1": (
        "Restructure a sentence when word-for-word substitution does not work."
    ),
    "9.2": "Use each approved word with its approved meaning and part of speech.",
    "9.3": "Do not make phrasal verbs.",
    "9.4": "Keep terminology and writing style consistent through the document.",
    "GR-1": "Keep the conjunction `that`.",
    "GR-2": "Use `with` only when its relationship is unambiguous.",
    "GR-3": "Give every pronoun a clear referent.",
    "GR-4": "Prefer `this` with a noun instead of bare `this`.",
    "GR-5": (
        "Avoid words that can mislead readers because of false similarity across "
        "languages."
    ),
    "GR-6": (
        "Replace Latin abbreviations with explicit English; do not leave an "
        "open-ended `etc.` list."
    ),
    "GR-7": "Use inclusive language.",
    "GR-8": (
        "Use a possessive apostrophe only when its construction is clear and correct."
    ),
}


class STERulesReferenceTest(unittest.TestCase):
    def test_catalog_has_every_issue_9_rule_once(self):
        text = REFERENCE.read_text()
        rules = re.findall(r"^\|\s*(\d+\.\d+)\s*\|", text, re.MULTILINE)

        self.assertEqual(len(EXPECTED_RULES), 53)
        self.assertEqual(set(rules), EXPECTED_RULES)
        self.assertEqual(
            {rule: count for rule, count in Counter(rules).items() if count != 1},
            {},
        )

    def test_catalog_maps_each_id_to_pinned_local_paraphrase(self):
        text = REFERENCE.read_text()
        rows = dict(
            re.findall(
                r"^\|\s*((?:\d+\.\d+)|(?:GR-\d+))\s*\|\s*(.*?)\s*\|$",
                text,
                re.MULTILINE,
            )
        )

        self.assertEqual(rows, EXPECTED_PARAPHRASES)

    def test_reference_scopes_strict_rules_behind_semantic_safety(self):
        text = REFERENCE.read_text()

        required = [
            "## Application boundary",
            "## Strict STE requirements versus software guidance",
            "Unsafe as a global coding-agent default",
            "`references/semantic-preservation.md`",
            "action-controlling condition",
            "descriptive condition",
            "repository terminology",
            "exact technical names",
            "Do not change `should` to `must`",
            "Do not change `may` to `can`",
        ]
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_catalog_has_every_general_recommendation_once(self):
        text = REFERENCE.read_text()
        recommendations = re.findall(r"^\|\s*(GR-[1-8])\s*\|", text, re.MULTILINE)

        self.assertEqual(Counter(recommendations), Counter(f"GR-{n}" for n in range(1, 9)))

    def test_software_warning_order_is_explicit(self):
        text = REFERENCE.read_text()
        required = [
            "### Software warning order",
            "Put the warning block before the dangerous operation.",
            "Put each action-controlling condition before its command.",
            "Put the required command before the risk or possible consequence.",
        ]

        positions = [text.find(phrase) for phrase in required]
        self.assertNotIn(-1, positions)
        self.assertEqual(positions, sorted(positions))

    def test_reference_has_dictionary_certification_and_provenance_caveats(self):
        text = REFERENCE.read_text()

        required = [
            "## Dictionary and verification limits",
            "official ASD-STE100 dictionary is not included",
            "Do not infer dictionary approval",
            "cannot certify ASD-STE100 compliance",
            "compliance-oriented audit",
            "No official dictionary entries are reproduced",
            "## Provenance",
            "https://github.com/AminBlg/SimpleEnglish",
            "59bf6702197a5aadc96d197ea17f290d8d50dcd3",
            "skills/simple-english/SKILL.md",
            "Copyright (c) 2026 AminBlg",
            "ASD-STE100 is a registered trademark of ASD",
            "not affiliated with ASD, STEMG, or AminBlg",
        ]
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
