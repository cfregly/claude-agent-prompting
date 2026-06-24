"""Run trace-review suites and produce machine or Markdown reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .trace_review import load_trace, review_trace


def load_suite(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_trace_suite(path: str | Path) -> dict[str, Any]:
    suite_path = Path(path)
    suite = load_suite(suite_path)
    base_dir = suite_path.parent
    cases = []

    for case in suite.get("cases", []):
        trace_path = _resolve(base_dir, case["trace"])
        review = review_trace(load_trace(trace_path))
        expected_passed = case.get("expect_passed", True)
        min_score = float(case.get("min_score", 0.0))
        max_score = float(case.get("max_score", 1.0))
        expectation_met = (
            review.passed is bool(expected_passed)
            and review.score >= min_score
            and review.score <= max_score
        )
        cases.append(
            {
                "expectation_met": expectation_met,
                "expected_passed": bool(expected_passed),
                "max_score": max_score,
                "min_score": min_score,
                "name": case.get("name", trace_path.stem),
                "review": review.to_dict(),
                "trace": str(trace_path),
            }
        )

    passed = bool(cases) and all(case["expectation_met"] for case in cases)
    return {
        "cases": cases,
        "name": suite.get("name", suite_path.stem),
        "passed": passed,
        "summary": {
            "cases": len(cases),
            "met_expectations": sum(1 for case in cases if case["expectation_met"]),
        },
    }


def render_suite_markdown(result: dict[str, Any]) -> str:
    lines = [
        f"# {result['name']}",
        "",
        f"Passed: {'yes' if result['passed'] else 'no'}",
        "",
        "| Case | Expectation | Score | Result |",
        "|---|---:|---:|---:|",
    ]
    for case in result["cases"]:
        expected = "pass" if case["expected_passed"] else "fail"
        actual = "met" if case["expectation_met"] else "missed"
        lines.append(
            f"| {case['name']} | {expected} | {case['review']['score']:.3f} | {actual} |"
        )

    lines.extend(["", "## Findings"])
    for case in result["cases"]:
        failed = [
            finding
            for finding in case["review"]["findings"]
            if not finding["passed"]
        ]
        lines.append("")
        lines.append(f"### {case['name']}")
        if not failed:
            lines.append("No failed checks.")
            continue
        for finding in failed:
            lines.append(
                f"- `{finding['check']}` ({finding['severity']}): {finding['detail']}"
            )
    return "\n".join(lines) + "\n"


def _resolve(base_dir: Path, path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return (base_dir / candidate).resolve()
