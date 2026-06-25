"""Render portable reports from optimizer and audit JSON output."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from .adapters import load_json


def load_report_input(path: str | Path) -> dict[str, Any]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError("report input must be a JSON object")
    return payload


def render_html_report(payload: dict[str, Any], *, title: str = "Harness Report") -> str:
    summary = _summary_rows(payload)
    rows = "\n".join(
        f"<tr><th>{html.escape(label)}</th><td>{html.escape(value)}</td></tr>"
        for label, value in summary
    )
    backing = "\n".join(
        f"<li>{html.escape(item)}</li>"
        for item in _backing_data_lines(payload)
    )
    backing_section = f"<h2>Backing Data</h2><ul>{backing}</ul>" if backing else ""
    tables = "\n".join(_tables(payload))
    raw = html.escape(json.dumps(payload, indent=2, sort_keys=True))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #202124; }}
    table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
    th, td {{ border: 1px solid #d0d7de; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f6f8fa; }}
    .pass {{ color: #116329; font-weight: 700; }}
    .fail {{ color: #a40e26; font-weight: 700; }}
    pre {{ background: #f6f8fa; padding: 16px; overflow: auto; }}
  </style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <table>
    <tbody>
{rows}
    </tbody>
  </table>
{backing_section}
{tables}
  <h2>Raw JSON</h2>
  <pre>{raw}</pre>
</body>
</html>
"""


def render_pr_comment(payload: dict[str, Any], *, title: str = "Harness Report") -> str:
    rows = _summary_rows(payload)
    lines = [f"## {title}", ""]
    for label, value in rows:
        lines.append(f"- **{label}:** {value}")
    backing = _backing_data_lines(payload)
    if backing:
        lines.extend(["", "### Backing Data", ""])
        lines.extend(f"- {item}" for item in backing[:16])
    failures = _failure_lines(payload)
    if failures:
        lines.extend(["", "### Attention", ""])
        lines.extend(f"- {item}" for item in failures[:12])
    else:
        lines.extend(["", "No failing checks were found in this report."])
    return "\n".join(lines) + "\n"


def write_report(text: str, out: str | Path) -> Path:
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _summary_rows(payload: dict[str, Any]) -> list[tuple[str, str]]:
    rows = [
        ("Name", str(payload.get("name") or payload.get("matrix") or "report")),
        ("Passed", "yes" if bool(payload.get("passed")) else "no"),
    ]
    score = _score(payload)
    if score is not None:
        rows.append(("Score", f"{score:.3f}"))
    summary = payload.get("summary")
    if isinstance(summary, dict):
        for key in ("total", "passed_cases", "failed_cases", "errors", "skipped"):
            if key in summary:
                rows.append((key.replace("_", " ").title(), str(summary[key])))
    if "live" in payload:
        rows.append(("Live", "yes" if payload.get("live") else "no"))
    if "dry_run" in payload:
        rows.append(("Dry Run", "yes" if payload.get("dry_run") else "no"))
    return rows


def _score(payload: dict[str, Any]) -> float | None:
    for key in ("overall_score", "score"):
        if key in payload:
            return float(payload[key])
    summary = payload.get("summary")
    if isinstance(summary, dict) and "score" in summary:
        return float(summary["score"])
    value_bar = payload.get("value_bar")
    if isinstance(value_bar, dict) and "score" in value_bar:
        return float(value_bar["score"])
    return None


def _tables(payload: dict[str, Any]) -> list[str]:
    tables = []
    for key in ("cells", "results", "checks", "traces"):
        value = payload.get(key)
        if isinstance(value, list) and value and all(isinstance(item, dict) for item in value):
            tables.append(_dict_table(key.replace("_", " ").title(), value[:50]))
    return tables


def _dict_table(title: str, rows: list[dict[str, Any]]) -> str:
    keys = sorted({key for row in rows for key in row if _is_scalar(row.get(key))})
    header = "".join(f"<th>{html.escape(str(key))}</th>" for key in keys)
    body = []
    for row in rows:
        cells = "".join(f"<td>{html.escape(str(row.get(key, '')))}</td>" for key in keys)
        body.append(f"<tr>{cells}</tr>")
    return f"<h2>{html.escape(title)}</h2><table><thead><tr>{header}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def _failure_lines(payload: dict[str, Any]) -> list[str]:
    failures = []
    for key in ("findings", "results", "checks", "traces"):
        value = payload.get(key)
        if not isinstance(value, list):
            continue
        for item in value:
            if isinstance(item, dict) and item.get("passed") is False:
                label = item.get("name") or item.get("case") or item.get("check") or key
                detail = item.get("detail") or item.get("status") or item.get("error") or "failed"
                failures.append(f"{label}: {detail}")
    for nested in ("tool_selection", "value_bar", "tool_inventory"):
        value = payload.get(nested)
        if isinstance(value, dict) and value.get("passed") is False:
            failures.append(f"{nested}: failed")
    return failures


def _backing_data_lines(payload: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    matrix = payload.get("matrix")
    if matrix:
        lines.append(f"matrix: {matrix}")
    if payload.get("live") is not None:
        lines.append(f"live run: {'yes' if payload.get('live') else 'no'}")
    summary = payload.get("summary")
    if isinstance(summary, dict):
        parts = []
        for key in ("total", "passed_cases", "failed_cases", "errors", "skipped", "score"):
            if key in summary:
                parts.append(f"{key}={summary[key]}")
        if parts:
            lines.append("summary: " + ", ".join(parts))
    value_bar = payload.get("value_bar")
    if isinstance(value_bar, dict):
        lines.extend(_value_bar_lines(value_bar))
    source = payload.get("source")
    if isinstance(source, dict):
        source_parts = []
        for key in ("package", "version", "repo", "commit", "local_mcp_server", "docs"):
            if source.get(key):
                source_parts.append(f"{key}={source[key]}")
        if source_parts:
            lines.append("source pin: " + ", ".join(source_parts))
    cells = payload.get("cells")
    if isinstance(cells, list) and cells:
        lines.extend(_cell_lines(cells))
    results = payload.get("results")
    if isinstance(results, list) and results:
        lines.extend(_result_lines(results))
    claude = payload.get("claude_judge")
    if isinstance(claude, dict):
        lines.extend(_claude_judge_lines(claude))
    return lines


def _value_bar_lines(value_bar: dict[str, Any]) -> list[str]:
    lines = []
    baseline = value_bar.get("baseline")
    candidate = value_bar.get("candidate")
    baseline_score = _nested_score(baseline)
    candidate_score = _nested_score(candidate)
    if baseline_score is not None and candidate_score is not None:
        delta = candidate_score - baseline_score
        minimum = float(value_bar.get("minimum_delta", 0.0))
        lines.append(
            f"value bar: baseline={baseline_score:.3f}, candidate={candidate_score:.3f}, "
            f"delta={delta:.3f}, minimum={minimum:.3f}"
        )
    claim = value_bar.get("claim")
    if claim:
        lines.append(f"value claim: {claim}")
    if isinstance(baseline, dict) and baseline.get("source"):
        lines.append(f"baseline source: {baseline['source']}")
    if isinstance(candidate, dict) and candidate.get("source"):
        lines.append(f"candidate source: {candidate['source']}")
    return lines


def _cell_lines(cells: list[Any]) -> list[str]:
    lines = []
    for item in cells[:8]:
        if not isinstance(item, dict):
            continue
        label = " / ".join(
            str(item.get(key, ""))
            for key in ("provider", "harness", "tool_variant", "instruction_variant")
            if item.get(key, "")
        )
        counts = ", ".join(
            f"{key}={item[key]}"
            for key in ("passed", "failed", "errors", "score")
            if key in item
        )
        if label and counts:
            lines.append(f"cell {label}: {counts}")
    return lines


def _result_lines(results: list[Any]) -> list[str]:
    status_counts: dict[str, int] = {}
    failed = []
    for item in results:
        if not isinstance(item, dict):
            continue
        status = str(item.get("status", "unknown"))
        status_counts[status] = status_counts.get(status, 0) + 1
        if status in {"failed", "error"} and len(failed) < 6:
            case = item.get("case") or item.get("name") or "unnamed case"
            labels = [
                str(item.get(key, ""))
                for key in ("provider", "harness", "tool_variant", "instruction_variant")
                if item.get(key, "")
            ]
            failed.append(f"{case} ({' / '.join(labels)}): {status}")
    lines = []
    if status_counts:
        lines.append(
            "result statuses: "
            + ", ".join(f"{key}={value}" for key, value in sorted(status_counts.items()))
        )
    lines.extend(f"failed result: {item}" for item in failed)
    return lines


def _claude_judge_lines(claude: dict[str, Any]) -> list[str]:
    lines = []
    if "enabled" in claude:
        lines.append(f"Claude judge: enabled={claude.get('enabled')}, passed={claude.get('passed')}")
    tool_selection = claude.get("tool_selection")
    if isinstance(tool_selection, dict) and tool_selection.get("score") is not None:
        lines.append(f"Claude tool-selection score: {float(tool_selection['score']):.3f}")
    traces = claude.get("traces")
    if isinstance(traces, list):
        for trace in traces[:6]:
            if isinstance(trace, dict) and trace.get("score") is not None:
                lines.append(
                    f"Claude trace {trace.get('name', '')}: score={float(trace['score']):.3f}, "
                    f"passed={trace.get('passed')}"
                )
    return lines


def _nested_score(value: Any) -> float | None:
    if isinstance(value, dict) and value.get("score") is not None:
        return float(value["score"])
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _is_scalar(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))
