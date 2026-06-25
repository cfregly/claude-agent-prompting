"""Catalog of reusable harness optimization checks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_CATALOG = Path(__file__).resolve().parents[1] / "evals" / "checks" / "harness_optimization_checks.json"


def load_check_catalog(path: str | Path = DEFAULT_CATALOG) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("check catalog must be a JSON object")
    checks = data.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ValueError("check catalog must include non-empty checks")
    for check in checks:
        if not isinstance(check, dict):
            raise ValueError("each check must be an object")
        for key in ("id", "name", "signal", "promotion_evidence"):
            if not check.get(key):
                raise ValueError(f"check missing {key}")
    return data


def render_check_catalog_markdown(catalog: dict[str, Any]) -> str:
    lines = [
        f"# {catalog.get('name', 'Harness Optimization Checks')}",
        "",
        str(catalog.get("description", "")).strip(),
        "",
        "| Check | Signal | Promotion Evidence |",
        "|---|---|---|",
    ]
    for check in catalog.get("checks", []):
        lines.append(
            "| {name} | {signal} | {evidence} |".format(
                name=_cell(check.get("name", "")),
                signal=_cell(check.get("signal", "")),
                evidence=_cell(check.get("promotion_evidence", "")),
            )
        )
    return "\n".join(lines).rstrip() + "\n"


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
