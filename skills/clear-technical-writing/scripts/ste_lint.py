#!/usr/bin/env python3
"""Heuristic, advisory technical-writing linter.

Adapted from AminBlg/SimpleEnglish at commit
59bf6702197a5aadc96d197ea17f290d8d50dcd3.
Copyright (c) 2026 AminBlg.
Licensed under the MIT License; see the repository root LICENSE file.
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


MODES = ("clear", "procedure", "strict")
FORMATS = ("json", "text")
DISCLAIMER = "Advisory only; does not certify ASD-STE100 compliance."
CONTRACTION_RE = re.compile(
    r"\b(?:\w+n't|"
    r"(?:I|you|we|they|he|she|it|that|there|here|what|who|where|when|why|how)"
    r"'(?:ll|re|ve|d|s))\b",
    re.IGNORECASE,
)
LATIN_RE = re.compile(r"\b(?:e\.g\.|i\.e\.|etc\.?)", re.IGNORECASE)
INLINE_CODE_RE = re.compile(
    r"(?<!`)(?P<ticks>`+)(?!`)(?P<value>[^\n]*?)(?P=ticks)(?!`)"
)
FENCE_OPEN_RE = re.compile(
    r"^[ \t]{0,3}(?P<marker>`{3,}|~{3,})[^\n]*(?:\n|$)", re.MULTILINE
)
INDENTED_CODE_RE = re.compile(r"(?:^(?: {4}|\t).*(?:\n|$))+", re.MULTILINE)
LINK_OPEN_RE = re.compile(r"\[[^\]\n]*\]\(")
DIAGNOSTIC_RE = re.compile(
    r"^>\s*(?:Error|Log|Test):.*$", re.MULTILINE | re.IGNORECASE
)
URL_RE = re.compile(r"https?://[^\s)>]+")
NUMBER_RE = re.compile(
    r"(?<![\w.])(?:\d{1,2}:\d{2}(?::\d{2})?|"
    r"v?\d[\d,]*(?:\.\d+)*(?:-\d[\d,]*(?:\.\d+)*)*"
    r"%?(?:\s*(?:ms|seconds?|minutes?|hours?|days?|MB|GB|TB))?)",
    re.IGNORECASE,
)
PATH_RE = re.compile(
    r"(?<![\w])(?:/|\.{1,2}/)[A-Za-z0-9._~${}-]+(?:/[A-Za-z0-9._~${}-]+)*"
    r"|\b[A-Za-z]:\\[^\s`\"']+"
)
IMPERATIVE_VERBS = {
    "add",
    "apply",
    "call",
    "check",
    "choose",
    "click",
    "copy",
    "configure",
    "confirm",
    "contact",
    "create",
    "delete",
    "download",
    "edit",
    "ensure",
    "enter",
    "execute",
    "install",
    "make",
    "open",
    "press",
    "read",
    "remove",
    "replace",
    "restore",
    "restart",
    "retry",
    "run",
    "save",
    "select",
    "set",
    "start",
    "stop",
    "update",
    "upload",
    "use",
    "verify",
    "wait",
    "write",
}


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="-")
    parser.add_argument("--mode", choices=MODES, default="clear")
    parser.add_argument("--format", choices=FORMATS, default="text")
    parser.add_argument("--source")
    parser.add_argument("--strict-gate", action="store_true")
    return parser


def read_text(path):
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text()


def location(text, offset):
    line = text.count("\n", 0, offset) + 1
    line_start = text.rfind("\n", 0, offset) + 1
    return line, offset - line_start + 1


def mask_range(characters, start, end):
    for index in range(start, end):
        if characters[index] != "\n":
            characters[index] = " "


def mask_headings(text):
    characters = list(text)
    for match in re.finditer(r"^#{1,6}\s+.*$", text, re.MULTILINE):
        mask_range(characters, match.start(), match.end())
    return "".join(characters)


def fenced_code_spans(text):
    spans = []
    position = 0
    while opener := FENCE_OPEN_RE.search(text, position):
        marker = opener.group("marker")
        closer_re = re.compile(
            rf"^[ \t]{{0,3}}{re.escape(marker[0])}{{{len(marker)},}}[ \t]*(?:\n|$)",
            re.MULTILINE,
        )
        closer = closer_re.search(text, opener.end())
        if closer is None:
            spans.append(
                {
                    "start": opener.start(),
                    "end": len(text),
                    "value_start": opener.end(),
                    "value": text[opener.end() :],
                }
            )
            break
        spans.append(
            {
                "start": opener.start(),
                "end": closer.end(),
                "value_start": opener.end(),
                "value": text[opener.end() : closer.start()],
            }
        )
        position = closer.end()
    return spans


def link_destination_spans(text):
    spans = []
    for opener in LINK_OPEN_RE.finditer(text):
        start = opener.end()
        depth = 0
        position = start
        while position < len(text):
            character = text[position]
            if character == "\\" and position + 1 < len(text):
                position += 2
                continue
            if character == "\n":
                break
            if character == "(":
                depth += 1
            elif character == ")":
                if depth == 0:
                    spans.append(
                        {
                            "start": opener.start(),
                            "end": position + 1,
                            "value_start": start,
                            "value": text[start:position],
                        }
                    )
                    break
                depth -= 1
            position += 1
    return spans


def mask_markdown(text):
    characters = list(text)
    for span in fenced_code_spans(text):
        mask_range(characters, span["start"], span["end"])
    patterns = [
        re.compile(r"\A---\s*\n.*?^---\s*$", re.MULTILINE | re.DOTALL),
        INDENTED_CODE_RE,
        INLINE_CODE_RE,
        DIAGNOSTIC_RE,
        URL_RE,
    ]
    for pattern in patterns:
        for match in pattern.finditer(text):
            mask_range(characters, match.start(), match.end())
    for span in link_destination_spans(text):
        mask_range(characters, span["value_start"], span["end"] - 1)
    return "".join(characters)


def sentence_spans(text):
    boundary_text = list(text)
    for index in range(1, len(boundary_text) - 1):
        if (
            boundary_text[index] == "."
            and boundary_text[index - 1].isdigit()
            and boundary_text[index + 1].isdigit()
        ):
            boundary_text[index] = "·"
    for match in LATIN_RE.finditer(text):
        for index in range(match.start(), match.end()):
            if boundary_text[index] == ".":
                boundary_text[index] = "·"

    start = 0
    for index, character in enumerate(boundary_text):
        if character not in ".!?":
            continue
        end = index + 1
        while end < len(boundary_text) and boundary_text[end] in "\"'”’)]}*_":
            end += 1
        if end < len(boundary_text) and not boundary_text[end].isspace():
            continue
        leading = len(text[start:end]) - len(text[start:end].lstrip())
        if text[start + leading : end].strip():
            yield start + leading, end
        start = end
    leading = len(text[start:]) - len(text[start:].lstrip())
    if text[start + leading :].strip():
        yield start + leading, len(text)


def is_instruction(sentence):
    candidate = re.sub(r"^(?:#+\s+|[-*]\s+|\d+\.\s+)", "", sentence.strip())
    match = re.match(r"([A-Za-z]+)\b", candidate)
    return match is not None and match.group(1).lower() in IMPERATIVE_VERBS


def in_ranges(offset, ranges):
    return any(start <= offset < end for start, end in ranges)


def protected_spans(text):
    fenced_spans = fenced_code_spans(text)
    fenced_ranges = [(span["start"], span["end"]) for span in fenced_spans]
    indented_matches = [
        match
        for match in INDENTED_CODE_RE.finditer(text)
        if not in_ranges(match.start(), fenced_ranges)
    ]
    code_ranges = fenced_ranges + [
        (match.start(), match.end()) for match in indented_matches
    ]
    inline_matches = [
        match
        for match in INLINE_CODE_RE.finditer(text)
        if not in_ranges(match.start(), code_ranges)
    ]
    link_spans = link_destination_spans(text)
    diagnostic_matches = list(DIAGNOSTIC_RE.finditer(text))
    url_matches = list(URL_RE.finditer(text))
    url_ranges = [(match.start(), match.end()) for match in url_matches]
    non_bare_url_ranges = (
        code_ranges
        + [(match.start(), match.end()) for match in inline_matches]
        + [(span["start"], span["end"]) for span in link_spans]
        + [(match.start(), match.end()) for match in diagnostic_matches]
    )

    fenced_values = [
        (span["value"], span["value_start"]) for span in fenced_spans
    ]
    for match in indented_matches:
        lines = match.group(0).splitlines(keepends=True)
        value = "".join(
            line[4:] if line.startswith("    ") else line[1:] for line in lines
        )
        indent = 4 if match.group(0).startswith("    ") else 1
        fenced_values.append((value, match.start() + indent))

    return {
        "inline-code": [
            (match.group("value"), match.start("value"))
            for match in inline_matches
        ],
        "fenced-code": fenced_values,
        "link-destination": [
            (span["value"], span["value_start"]) for span in link_spans
        ],
        "quoted-diagnostic": [
            (match.group(0).strip(), match.start()) for match in diagnostic_matches
        ],
        "bare-url": [
            (match.group(0), match.start())
            for match in url_matches
            if not in_ranges(match.start(), non_bare_url_ranges)
        ],
        "numeric-token": [
            (match.group(0), match.start()) for match in NUMBER_RE.finditer(text)
        ],
        "path": [
            (match.group(0), match.start())
            for match in PATH_RE.finditer(text)
            if not in_ranges(match.start(), url_ranges)
        ],
    }


def occurrence_counter(occurrences):
    return Counter(value for value, _ in occurrences)


def changed_span(expected, actual):
    remaining = occurrence_counter(expected)
    for value, offset in actual:
        if remaining[value] > 0:
            remaining[value] -= 1
        else:
            return value, offset
    missing = occurrence_counter(expected) - occurrence_counter(actual)
    return f"missing {next(iter(missing))}", 0


def make_finding(rule, category, source, text, offset, offending_text, message, **extra):
    line, column = location(text, offset)
    finding = {
        "rule": rule,
        "category": category,
        "severity": "warning",
        "source": source,
        "line": line,
        "column": column,
        "text": offending_text,
        "message": message,
    }
    finding.update(extra)
    return finding


def lint_text(text, mode, source, source_text=None):
    findings = []
    analysis_text = mask_markdown(text)
    if source_text is not None:
        expected_spans = protected_spans(source_text)
        actual_spans = protected_spans(text)
        for kind in expected_spans:
            if occurrence_counter(expected_spans[kind]) == occurrence_counter(
                actual_spans[kind]
            ):
                continue
            offending_text, offset = changed_span(
                expected_spans[kind], actual_spans[kind]
            )
            findings.append(
                make_finding(
                    "protected-span",
                    "semantic",
                    source,
                    text,
                    offset,
                    offending_text,
                    f"Protected {kind} values differ from source.",
                    protected_kind=kind,
                )
            )
    if mode == "strict":
        for match in re.finditer(
            r"\b(should|may|might|could)\b", analysis_text, flags=re.IGNORECASE
        ):
            modal = match.group(0)
            findings.append(
                make_finding(
                    "modal",
                    "semantic",
                    source,
                    text,
                    match.start(),
                    modal,
                    f'Review modal "{modal}"; preserve its meaning. '
                    "Strict STE may require a different construction.",
                )
            )
        for match in CONTRACTION_RE.finditer(analysis_text):
            findings.append(
                make_finding(
                    "contraction",
                    "style",
                    source,
                    text,
                    match.start(),
                    text[match.start() : match.end()],
                    "Avoid contractions in strict STE; preserve the original meaning.",
                )
            )
        for match in LATIN_RE.finditer(analysis_text):
            findings.append(
                make_finding(
                    "latin-abbreviation",
                    "style",
                    source,
                    text,
                    match.start(),
                    text[match.start() : match.end()],
                    "Avoid Latin abbreviations in strict STE.",
                )
            )

    sentence_text = mask_headings(analysis_text)
    spans = list(sentence_spans(sentence_text))
    if mode in {"procedure", "strict"}:
        for start, end in spans:
            sentence = sentence_text[start:end]
            instruction = is_instruction(sentence)
            if mode == "procedure" and not instruction:
                continue
            limit = 20 if instruction else 25
            word_count = len(sentence.split())
            if word_count <= limit:
                continue
            findings.append(
                make_finding(
                    "sentence-length",
                    "style",
                    source,
                    text,
                    start,
                    text[start:end].strip(),
                    f"Sentence has {word_count} words; {mode} mode limit is {limit}.",
                )
            )

    if mode == "procedure":
        for start, end in spans:
            sentence = sentence_text[start:end].strip()
            if not is_instruction(sentence):
                continue
            condition = re.search(r"\b(if|when)\b", sentence, flags=re.IGNORECASE)
            if condition is None:
                continue
            findings.append(
                make_finding(
                    "condition-order",
                    "procedure",
                    source,
                    text,
                    start,
                    text[start:end].strip(),
                    "Put the action-controlling condition before the instruction.",
                )
            )

    findings.sort(key=lambda finding: (finding["line"], finding["column"], finding["rule"]))
    return {
        "advisory": True,
        "mode": mode,
        "findings": findings,
        "summary": {"warnings": len(findings)},
        "disclaimer": DISCLAIMER,
    }


def render_text(report):
    count = report["summary"]["warnings"]
    noun = "warning" if count == 1 else "warnings"
    lines = [f"ste-lint: {count} {noun} ({report['mode']} mode)"]
    for finding in report["findings"]:
        lines.append(
            f"{finding['source']}:{finding['line']}:{finding['column']}: "
            f"warning {finding['rule']}/{finding['category']}: {finding['message']}"
        )
    lines.append(report["disclaimer"])
    return "\n".join(lines) + "\n"


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        text = read_text(args.path)
    except (OSError, UnicodeError) as error:
        parser.error(f"cannot read input {args.path!r}: {error}")
    try:
        source_text = read_text(args.source) if args.source else None
    except (OSError, UnicodeError) as error:
        parser.error(f"cannot read source {args.source!r}: {error}")

    source_name = "<stdin>" if args.path == "-" else args.path
    report = lint_text(text, args.mode, source_name, source_text)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        sys.stdout.write(render_text(report))
    if args.strict_gate and report["findings"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
