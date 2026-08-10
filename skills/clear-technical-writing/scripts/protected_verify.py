#!/usr/bin/env python3
"""Verify protected literal occurrences in a rewritten document."""

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from ste_lint import protected_spans


CLI_FLAG_RE = re.compile(
    r"(?<![\w-])--[A-Za-z0-9][A-Za-z0-9-]*(?:=[^\s`]+)?"
)
ENVIRONMENT_VARIABLE_RE = re.compile(
    r"(?<!\w)(?:\$\{[A-Za-z_][A-Za-z0-9_]*\}|\$[A-Za-z_][A-Za-z0-9_]*)"
)
LINK_LABEL_RE = re.compile(r"\[([^\]\n]*)\]\(")
BOLD_TEXT_RE = re.compile(
    r"(?<!\*)\*\*(?!\*)([^\n]+?)(?<!\*)\*\*(?!\*)"
    r"|(?<!_)__(?!_)([^\n]+?)(?<!_)__(?!_)"
)
JSON_KEY_RE = re.compile(r'"((?:\\.|[^"\\])*)"\s*:')
IDENTIFIER_RE = re.compile(
    r"\b(?:[A-Z]{2,}[A-Z0-9_-]*|[A-Z][a-z0-9]+(?:[A-Z][A-Za-z0-9]*)+)\b"
)

DISCLAIMER = (
    "Mechanical protected-content verification only; does not prove semantic "
    "equivalence or ASD-STE100 compliance."
)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path")
    parser.add_argument("--source", required=True)
    return parser


def structural_container(text, offset):
    line_start = text.rfind("\n", 0, offset) + 1
    line_end = text.find("\n", offset)
    if line_end == -1:
        line_end = len(text)
    line = text[line_start:line_end]
    stripped = line.lstrip()
    if match := re.match(r"(#{1,6})\s+", stripped):
        return f"heading-{len(match.group(1))}"
    if stripped.startswith(">"):
        return "blockquote"
    return "flow"


def is_ordered_list_marker(text, value, offset):
    line_start = text.rfind("\n", 0, offset) + 1
    if text[line_start:offset].strip():
        return False
    suffix = text[offset + len(value) :]
    return re.match(r"[.)]\s+", suffix) is not None


def in_match_ranges(offset, matches):
    return any(match.start() <= offset < match.end() for match in matches)


def inventory(text):
    occurrences_by_kind = protected_spans(text)
    occurrences_by_kind["numeric-token"] = [
        (value.rstrip(","), offset)
        for value, offset in occurrences_by_kind["numeric-token"]
        if not is_ordered_list_marker(text, value, offset)
    ]
    cli_flag_matches = list(CLI_FLAG_RE.finditer(text))
    environment_matches = list(ENVIRONMENT_VARIABLE_RE.finditer(text))
    occurrences_by_kind["cli-flag"] = [
        (match.group(0), match.start()) for match in cli_flag_matches
    ]
    occurrences_by_kind["environment-variable"] = [
        (match.group(0), match.start()) for match in environment_matches
    ]
    occurrences_by_kind["link-label"] = [
        (match.group(1), match.start(1)) for match in LINK_LABEL_RE.finditer(text)
    ]
    occurrences_by_kind["bold-text"] = [
        (
            match.group(1) if match.group(1) is not None else match.group(2),
            match.start(1) if match.group(1) is not None else match.start(2),
        )
        for match in BOLD_TEXT_RE.finditer(text)
    ]
    occurrences_by_kind["json-key"] = [
        (match.group(1), match.start(1)) for match in JSON_KEY_RE.finditer(text)
    ]
    occurrences_by_kind["identifier"] = [
        (match.group(0), match.start())
        for match in IDENTIFIER_RE.finditer(text)
        if not in_match_ranges(match.start(), environment_matches)
    ]
    return {
        kind: [
            {"value": value, "container": structural_container(text, offset)}
            for value, offset in occurrences
        ]
        for kind, occurrences in occurrences_by_kind.items()
    }


def occurrence_counter(entries):
    return Counter((entry["value"], entry["container"]) for entry in entries)


def verify(source, draft):
    expected = inventory(source)
    actual = inventory(draft)
    violations = [
        {
            "rule": "protected-occurrence",
            "kind": kind,
            "expected": expected[kind],
            "actual": actual[kind],
        }
        for kind in expected
        if occurrence_counter(expected[kind]) != occurrence_counter(actual[kind])
    ]
    return {
        "ok": not violations,
        "violations": violations,
        "disclaimer": DISCLAIMER,
    }


def main():
    args = build_parser().parse_args()
    try:
        source = Path(args.source).read_text(encoding="utf-8")
        draft = Path(args.path).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise SystemExit(f"cannot read verifier input: {error}") from error
    report = verify(source, draft)
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
