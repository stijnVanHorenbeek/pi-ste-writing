#!/usr/bin/env python3
"""Score one rewrite against deterministic semantic-preservation fixtures."""

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS_PATH = ROOT / "evals" / "fixtures" / "semantic-preservation.json"
LINTER_PATH = (
    ROOT / "skills" / "clear-technical-writing" / "scripts" / "ste_lint.py"
)
FORMATS = ("json", "text")
OBJECTIVE_SOURCE_KINDS = {
    "inline_code",
    "fenced_code",
    "markdown_link",
    "bold_text",
    "identifier",
    "number",
    "date",
    "version",
    "unit",
}
DISCLAIMER = (
    "Deterministic checks cover only enumerated fixture rules; they do not prove "
    "full semantic equivalence or certify ASD-STE100 compliance."
)


def objective_values(text, kind):
    if kind in {"inline_code", "fenced_code", "markdown_link", "bold_text"}:
        return extracted_values(text, kind)
    patterns = {
        "identifier": r"(?<![A-Za-z0-9_])(?:[A-Z][A-Z0-9_]*[-_][A-Z0-9_-]+|[A-Z]{2,}[0-9]+)(?![A-Za-z0-9_])",
        "number": r"(?<![A-Za-z0-9_])[-+]?\d+(?:[.,]\d+)?(?:%|‰)?(?![A-Za-z0-9_])",
        "date": r"(?<!\d)\d{4}-\d{2}-\d{2}(?!\d)",
        "version": r"(?<![A-Za-z0-9])v?\d+\.\d+(?:\.\d+)*(?:[-+][A-Za-z0-9.-]+)?(?![A-Za-z0-9])",
        "unit": r"(?<![A-Za-z0-9_])[-+]?\d+(?:\.\d+)?\s?(?:(?:ms|s|min|h|Hz|kHz|MHz|GHz|B|KB|MB|GB|TB|V|A|W|°C|°F)\b|%(?![A-Za-z0-9_]))",
    }
    if kind not in patterns:
        raise ValueError(f"unsupported objective source kind: {kind}")
    return re.findall(patterns[kind], text)


def validate_corpus(corpus):
    if not isinstance(corpus, dict) or corpus.get("schema_version") not in {1, 2}:
        raise ValueError("fixture corpus schema_version must be 1 or 2")
    fixtures = corpus.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        raise ValueError("fixture corpus fixtures must be nonempty")
    if corpus["schema_version"] == 1:
        return
    fixture_ids = []
    for fixture in fixtures:
        if not isinstance(fixture, dict):
            raise ValueError("schema-v2 fixture must be an object")
        required = {
            "id", "mode", "task", "source", "expect_skill_loaded",
            "semantic_review_applicable", "objective_contract", "semantic_claims",
        }
        if set(fixture) != required:
            raise ValueError("schema-v2 fixture fields are invalid")
        fixture_ids.append(fixture.get("id"))
        if not all(
            isinstance(fixture.get(key), str) and fixture[key].strip()
            for key in ("id", "mode", "task", "source")
        ) or fixture["mode"] not in {"clear", "procedure", "strict"}:
            raise ValueError("schema-v2 fixture identity is invalid")
        if not isinstance(fixture["expect_skill_loaded"], bool) or not isinstance(
            fixture["semantic_review_applicable"], bool
        ):
            raise ValueError("schema-v2 fixture applicability is invalid")
        contract = fixture["objective_contract"]
        if not isinstance(contract, dict) or set(contract) != {
            "source_equality", "ordered_anchors"
        }:
            raise ValueError("schema-v2 objective contract fields are invalid")
        equality = contract["source_equality"]
        kinds = equality.get("kinds") if isinstance(equality, dict) else None
        if (
            not isinstance(equality, dict)
            or set(equality) != {"kinds", "occurrence_count", "container"}
            or not isinstance(kinds, list)
            or len(kinds) != len(set(kinds))
            or not all(kind in OBJECTIVE_SOURCE_KINDS for kind in kinds)
            or equality.get("occurrence_count") != "exact"
            or equality.get("container") != "exact"
        ):
            raise ValueError("schema-v2 objective contract source equality is invalid")
        anchors = contract["ordered_anchors"]
        if (
            not isinstance(anchors, list)
            or any(
                not isinstance(group, list)
                or len(group) < 2
                or not all(isinstance(anchor, str) and anchor for anchor in group)
                for group in anchors
            )
        ):
            raise ValueError("schema-v2 objective contract ordered anchors are invalid")
        for group in anchors:
            cursor = -1
            for anchor in group:
                cursor = fixture["source"].find(anchor, cursor + 1)
                if cursor < 0:
                    raise ValueError(
                        "schema-v2 objective contract anchors must occur in source order"
                    )
        claims = fixture["semantic_claims"]
        if (
            not isinstance(claims, list)
            or (fixture["semantic_review_applicable"] and not claims)
            or any(
                not isinstance(claim, dict)
                or set(claim) != {"id", "risk", "proposition"}
                or not all(
                    isinstance(claim[key], str) and claim[key].strip()
                    for key in claim
                )
                for claim in claims
            )
        ):
            raise ValueError("schema-v2 semantic claims are invalid")
    if len(fixture_ids) != len(set(fixture_ids)):
        raise ValueError("schema-v2 fixture IDs must be unique")


def counter_records(counter):
    return [
        {
            "value": list(value) if isinstance(value, tuple) else value,
            "count": count,
        }
        for value, count in sorted(counter.items(), key=lambda item: repr(item[0]))
    ]


def score_objective_rewrite(fixture, rewrite, candidate):
    source_failures = []
    anchor_failures = []
    contract = fixture["objective_contract"]
    for kind in contract["source_equality"]["kinds"]:
        expected = Counter(objective_values(fixture["source"], kind))
        actual = Counter(objective_values(rewrite, kind))
        if actual != expected:
            source_failures.append({
                "rule_id": f"source-equality.{kind}",
                "kind": kind,
                "expected": counter_records(expected),
                "actual": counter_records(actual),
            })
    for index, anchors in enumerate(contract["ordered_anchors"], 1):
        cursor = -1
        passed = True
        for anchor in anchors:
            position = rewrite.find(anchor, cursor + 1)
            if position < 0:
                passed = False
                break
            cursor = position
        if not passed:
            anchor_failures.append({
                "rule_id": "ordered-anchor",
                "group": index,
                "anchors": anchors,
            })
    return {
        "schema_version": 2,
        "fixture_id": fixture["id"],
        "candidate": candidate,
        "mode": fixture["mode"],
        "objective_contract": {
            "passed": not source_failures and not anchor_failures,
            "failed_rule_ids": sorted({
                failure["rule_id"]
                for failure in source_failures + anchor_failures
            }),
            "failures": source_failures + anchor_failures,
        },
        "objective_procedure": {
            "applicable": bool(contract["ordered_anchors"]),
            "passed": not anchor_failures if contract["ordered_anchors"] else None,
            "failed_rule_ids": sorted({failure["rule_id"] for failure in anchor_failures}),
            "failures": anchor_failures,
        },
        "semantic_review_applicable": fixture["semantic_review_applicable"],
        "disclaimer": DISCLAIMER,
    }


def extracted_values(text, check_type):
    if check_type == "inline_code":
        return re.findall(r"(?<!`)`([^`\n]+)`(?!`)", text)
    if check_type == "fenced_code":
        values = []
        pattern = re.compile(
            r"^(?P<indent>[ \t]{0,3})```[^\n]*\n(?P<value>.*?)"
            r"^[ \t]{0,3}```[ \t]*$",
            re.DOTALL | re.MULTILINE,
        )
        for match in pattern.finditer(text):
            indent = match.group("indent")
            value = "\n".join(
                line[len(indent) :] if indent and line.startswith(indent) else line
                for line in match.group("value").splitlines()
            )
            values.append(value)
        return values
    if check_type == "markdown_link":
        return re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)
    if check_type == "bold_text":
        return re.findall(r"\*\*([^*\n]+)\*\*", text)
    raise ValueError(f"unsupported check type: {check_type}")


def check_passes(text, check):
    check_type = check["type"]
    if check_type == "contains":
        count = text.count(check["value"])
        return count == check["count"] if "count" in check else count > 0
    if check_type == "regex":
        return re.search(check["pattern"], text) is not None
    if check_type == "precedes_regex":
        before = re.search(check["before_pattern"], text)
        after = re.search(check["after_pattern"], text)
        return before is not None and after is not None and before.start() < after.start()

    values = extracted_values(text, check_type)
    expected = (
        (check["label"], check["destination"])
        if check_type == "markdown_link"
        else check["value"]
    )
    return values.count(expected) == check.get("count", 1)


def empty_metric():
    return {
        "applicable": False,
        "passed": None,
        "rules_total": 0,
        "rules_passed": 0,
        "rules_failed": 0,
        "pass_rate": None,
        "failures": [],
    }


def metric_from_invariants(fixture, rewrite, categories):
    rules = [
        invariant
        for invariant in fixture["invariants"]
        if invariant["category"] in categories
    ]
    if not rules:
        return empty_metric()

    failures = []
    for rule in rules:
        failed_checks = [
            check for check in rule["checks"] if not check_passes(rewrite, check)
        ]
        if failed_checks:
            failures.append(
                {
                    "rule_id": rule["id"],
                    "description": rule["description"],
                    "failed_checks": failed_checks,
                }
            )

    total = len(rules)
    failed = len(failures)
    return {
        "applicable": True,
        "passed": failed == 0,
        "rules_total": total,
        "rules_passed": total - failed,
        "rules_failed": failed,
        "pass_rate": round((total - failed) / total, 6),
        "failures": failures,
    }


def forbidden_claim_metric(fixture, rewrite):
    claims = fixture["forbidden_claims"]
    if not claims:
        return empty_metric()

    failures = []
    for claim in claims:
        evidence = []
        for pattern in claim["patterns"]:
            if match := re.search(pattern, rewrite):
                line = rewrite.count("\n", 0, match.start()) + 1
                line_start = rewrite.rfind("\n", 0, match.start()) + 1
                evidence.append(
                    {
                        "pattern": pattern,
                        "text": match.group(0),
                        "line": line,
                        "column": match.start() - line_start + 1,
                    }
                )
        if evidence:
            failures.append(
                {
                    "rule_id": claim["id"],
                    "description": claim["description"],
                    "evidence": evidence,
                }
            )

    total = len(claims)
    failed = len(failures)
    return {
        "applicable": True,
        "passed": failed == 0,
        "rules_total": total,
        "rules_passed": total - failed,
        "rules_failed": failed,
        "pass_rate": round((total - failed) / total, 6),
        "failures": failures,
    }


@lru_cache(maxsize=1)
def load_linter():
    spec = importlib.util.spec_from_file_location("ste_writing_linter", LINTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load linter at {LINTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def selected_findings(report, category):
    return [
        finding for finding in report["findings"] if finding["category"] == category
    ]


def is_procedure_action_line(line, linter):
    if linter.is_instruction(line):
        return True
    candidate = re.sub(r"^\s*(?:\d+\.\s+|[-*]\s+)", "", line)
    condition = re.match(
        r"(?i)(?:if|when|after|before|unless)\b.+?,\s*([A-Za-z]+)\b",
        candidate,
    )
    return (
        condition is not None
        and condition.group(1).lower() in linter.IMPERATIVE_VERBS
    )


def step_numbering_findings(text, source, linter):
    analysis_text = linter.mask_headings(linter.mask_markdown(text))
    findings = []
    for match in re.finditer(r"^.*$", analysis_text, re.MULTILINE):
        line = match.group(0)
        if not line.strip() or not is_procedure_action_line(line, linter):
            continue
        original_line = text[match.start() : match.end()]
        if re.match(r"\s*\d+\.\s+", original_line):
            continue
        if re.search(
            r"(?i)\b(?:confirm|check|verify|ensure)\s+"
            r"(?:both|these|the following)\s+"
            r"(?:conditions|checks|requirements|items|steps):\s*$",
            original_line,
        ) and re.match(
            r"(?:[ \t]*\r?\n)+[ \t]*\d+\.\s+",
            text[match.end() :],
        ):
            continue
        findings.append(
            linter.make_finding(
                "step-numbering",
                "procedure",
                source,
                text,
                match.start(),
                original_line.strip(),
                "Put each procedure instruction in a numbered step.",
            )
        )
    return findings


def add_source_protection(metric, source, lint_report, linter):
    findings = [
        finding
        for finding in lint_report["findings"]
        if finding["rule"] == "protected-span"
        and finding.get("protected_kind") != "numeric-token"
    ]
    source_spans = linter.protected_spans(source)
    source_has_protected_value = any(
        values
        for kind, values in source_spans.items()
        if kind != "numeric-token"
    )
    if not source_has_protected_value and not findings:
        return metric

    failures = list(metric["failures"])
    if findings:
        failures.append(
            {
                "rule_id": "protected.source-equality",
                "description": (
                    "Preserve nonnumeric protected values and occurrence counts "
                    "by container."
                ),
                "changed_kinds": sorted(
                    {finding["protected_kind"] for finding in findings}
                ),
                "findings": findings,
            }
        )
    total = metric["rules_total"] + 1
    failed = len(failures)
    return {
        "applicable": True,
        "passed": failed == 0,
        "rules_total": total,
        "rules_passed": total - failed,
        "rules_failed": failed,
        "pass_rate": round((total - failed) / total, 6),
        "failures": failures,
    }


def score_rewrite(fixture, rewrite, candidate="<candidate>"):
    if "objective_contract" in fixture:
        return score_objective_rewrite(fixture, rewrite, candidate)
    metrics = {
        "protected_span_equality": metric_from_invariants(
            fixture, rewrite, {"protected_span"}
        ),
        "required_fact_retention": metric_from_invariants(
            fixture, rewrite, {"fact"}
        ),
        "forbidden_fact_invention": forbidden_claim_metric(fixture, rewrite),
        "modality_and_certainty_preservation": metric_from_invariants(
            fixture, rewrite, {"modality", "causality"}
        ),
        "repository_term_preservation": metric_from_invariants(
            fixture, rewrite, {"repository_term"}
        ),
    }

    linter = load_linter()
    lint_report = linter.lint_text(
        rewrite,
        fixture["mode"],
        candidate,
        fixture["source"],
    )
    metrics["protected_span_equality"] = add_source_protection(
        metrics["protected_span_equality"],
        fixture["source"],
        lint_report,
        linter,
    )
    procedure_rules = metric_from_invariants(fixture, rewrite, {"procedure"})
    procedure_findings = selected_findings(lint_report, "procedure")
    if fixture["mode"] == "procedure":
        procedure_findings.extend(
            step_numbering_findings(rewrite, candidate, linter)
        )
        procedure_findings.sort(
            key=lambda finding: (
                finding["line"],
                finding["column"],
                finding["rule"],
            )
        )
    procedure_applicable = (
        procedure_rules["applicable"] or fixture["mode"] == "procedure"
    )
    procedure_passed = None
    if procedure_applicable:
        procedure_passed = (
            procedure_rules["passed"] is not False and not procedure_findings
        )
    procedure = {
        "applicable": procedure_applicable,
        "passed": procedure_passed,
        "required_rules": procedure_rules,
        "warning_count": len(procedure_findings),
        "warnings": procedure_findings,
    }

    failed_rule_ids = {
        failure["rule_id"]
        for metric in metrics.values()
        for failure in metric["failures"]
    }
    failed_rule_ids.update(
        failure["rule_id"] for failure in procedure_rules["failures"]
    )
    failed_rule_ids.update(
        f"linter.{finding['rule']}" for finding in procedure_findings
    )

    style_findings = selected_findings(lint_report, "style")
    style = {
        "advisory": True,
        "warning_count": len(style_findings),
        "warnings_by_rule": dict(
            sorted(Counter(item["rule"] for item in style_findings).items())
        ),
        "findings": style_findings,
    }

    return {
        "schema_version": 1,
        "fixture_id": fixture["id"],
        "candidate": candidate,
        "mode": fixture["mode"],
        "semantic": {
            "gate_passed": not failed_rule_ids,
            "failed_rule_ids": sorted(failed_rule_ids),
            "metrics": metrics,
        },
        "procedure": procedure,
        "style": style,
        "disclaimer": DISCLAIMER,
    }


def read_text(path):
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def load_fixture(fixture_id, corpus_path=DEFAULT_CORPUS_PATH):
    corpus = json.loads(Path(corpus_path).read_text(encoding="utf-8"))
    validate_corpus(corpus)
    for fixture in corpus["fixtures"]:
        if fixture["id"] == fixture_id:
            return fixture
    raise ValueError(f"unknown fixture: {fixture_id}")


def metric_status(metric):
    if not metric["applicable"]:
        return "not-applicable"
    return "pass" if metric["passed"] else "FAIL"


def render_text(report):
    semantic = report["semantic"]
    lines = [
        f"fixture: {report['fixture_id']} ({report['mode']} mode)",
        f"semantic gate: {'PASS' if semantic['gate_passed'] else 'FAIL'}",
    ]
    for name, metric in semantic["metrics"].items():
        lines.append(
            f"  {name}: {metric_status(metric)} "
            f"({metric['rules_passed']}/{metric['rules_total']} rules)"
        )
        for failure in metric["failures"]:
            lines.append(
                f"    - {failure['rule_id']}: {failure['description']}"
            )

    procedure = report["procedure"]
    lines.append(f"procedure structure: {metric_status(procedure)}")
    for failure in procedure["required_rules"]["failures"]:
        lines.append(f"  - {failure['rule_id']}: {failure['description']}")
    for finding in procedure["warnings"]:
        lines.append(
            f"  - linter.{finding['rule']} at {finding['line']}:"
            f"{finding['column']}: {finding['message']}"
        )

    style = report["style"]
    lines.append(
        f"mechanical style warnings: {style['warning_count']} (advisory)"
    )
    for finding in style["findings"]:
        lines.append(
            f"  - {finding['rule']} at {finding['line']}:{finding['column']}: "
            f"{finding['message']}"
        )
    lines.append(report["disclaimer"])
    return "\n".join(lines) + "\n"


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture_id")
    parser.add_argument("path", nargs="?", default="-")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS_PATH)
    parser.add_argument("--format", choices=FORMATS, default="text")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        fixture = load_fixture(args.fixture_id, args.corpus)
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError) as error:
        parser.error(f"cannot read corpus {str(args.corpus)!r}: {error}")
    except ValueError as error:
        parser.error(str(error))
    try:
        rewrite = read_text(args.path)
    except (OSError, UnicodeError) as error:
        parser.error(f"cannot read candidate {args.path!r}: {error}")

    candidate = "<stdin>" if args.path == "-" else args.path
    report = score_rewrite(fixture, rewrite, candidate)
    report["corpus_sha256"] = hashlib.sha256(args.corpus.read_bytes()).hexdigest()
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        sys.stdout.write(render_text(report))
    return 0 if report["semantic"]["gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
