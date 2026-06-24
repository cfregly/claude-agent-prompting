"""Review a submitted agent bundle: tools, traces, and optional report."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .prompt_builder import lint_tools
from .trace_review import load_trace, review_trace


def load_agent_bundle(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def review_agent_bundle(path: str | Path) -> dict[str, Any]:
    bundle_path = Path(path)
    bundle = load_agent_bundle(bundle_path)
    base_dir = bundle_path.parent

    tool_issues = lint_tools(bundle.get("tools", []))
    traces = []
    for item in bundle.get("traces", []):
        trace_path = _resolve(base_dir, item["trace"])
        review = review_trace(load_trace(trace_path))
        traces.append(
            {
                "name": item.get("name", trace_path.stem),
                "passed": review.passed,
                "score": review.score,
                "scores": review.scores,
                "trace": str(trace_path),
            }
        )

    trace_score = _average([trace["score"] for trace in traces])
    tool_score = 1.0 if not tool_issues else 0.0
    overall = round((tool_score + trace_score) / 2, 3) if traces else tool_score

    return {
        "name": bundle.get("name", bundle_path.stem),
        "overall_score": overall,
        "passed": not tool_issues and all(trace["passed"] for trace in traces),
        "tool_inventory": {
            "issues": tool_issues,
            "passed": not tool_issues,
            "score": tool_score,
            "tools": len(bundle.get("tools", [])),
        },
        "traces": traces,
    }


def render_agent_audit_markdown(result: dict[str, Any]) -> str:
    lines = [
        f"# {result['name']}",
        "",
        f"Passed: {'yes' if result['passed'] else 'no'}",
        f"Overall score: {result['overall_score']:.3f}",
        "",
        "## Tool Inventory",
        "",
        f"Tools reviewed: {result['tool_inventory']['tools']}",
        f"Tool score: {result['tool_inventory']['score']:.3f}",
    ]

    issues = result["tool_inventory"]["issues"]
    if issues:
        lines.extend(["", "Tool issues:"])
        lines.extend(f"- {issue}" for issue in issues)
    else:
        lines.extend(["", "No tool inventory issues."])

    lines.extend(["", "## Trace Scores", "", "| Trace | Score | Passed |", "|---|---:|---:|"])
    for trace in result["traces"]:
        lines.append(
            f"| {trace['name']} | {trace['score']:.3f} | {'yes' if trace['passed'] else 'no'} |"
        )

    return "\n".join(lines) + "\n"


def _average(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 3)


def _resolve(base_dir: Path, path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return (base_dir / candidate).resolve()
