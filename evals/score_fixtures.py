#!/usr/bin/env python3
"""Score one rewrite against deterministic semantic-preservation fixtures."""

import argparse
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
DISCLAIMER = (
    "Deterministic checks cover only enumerated fixture rules; they do not prove "
    "full semantic equivalence or certify ASD-STE100 compliance."
)


def extracted_values(text, check_type):
    if check_type == "inline_code":
        return re.findall(r"(?<!`)`([^`\n]+)`(?!`)", text)
    if check_type == "fenced_code":
        return re.findall(r"```[^\n]*\n(.*?)\n```", text, flags=re.DOTALL)
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


def load_fixture(fixture_id):
    corpus = json.loads(DEFAULT_CORPUS_PATH.read_text(encoding="utf-8"))
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
    parser.add_argument("--format", choices=FORMATS, default="text")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        fixture = load_fixture(args.fixture_id)
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError) as error:
        parser.error(f"cannot read corpus {str(DEFAULT_CORPUS_PATH)!r}: {error}")
    except ValueError as error:
        parser.error(str(error))
    try:
        rewrite = read_text(args.path)
    except (OSError, UnicodeError) as error:
        parser.error(f"cannot read candidate {args.path!r}: {error}")

    candidate = "<stdin>" if args.path == "-" else args.path
    report = score_rewrite(fixture, rewrite, candidate)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        sys.stdout.write(render_text(report))
    return 0 if report["semantic"]["gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
