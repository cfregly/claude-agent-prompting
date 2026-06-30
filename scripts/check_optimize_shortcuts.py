#!/usr/bin/env python3
"""Validate public MCP optimization shortcuts against stored matrices."""

from __future__ import annotations

from pathlib import Path
import json
import sys
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from claude_agent_harness_opt.model_matrix import MatrixFilters, run_model_matrix  # noqa: E402
from scripts.optimize_mcp import TARGETS, Target, _csv_set, _normalize_target, resolve_target  # noqa: E402


def main() -> int:
    failures = check_optimize_shortcuts()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("optimize shortcut check passed")
    return 0


def check_optimize_shortcuts(
    root: Path = ROOT,
    targets: Iterable[Target] = TARGETS,
) -> list[str]:
    target_list = list(targets)
    failures: list[str] = []
    failures.extend(_check_duplicate_selectors(target_list))

    makefile = (root / "Makefile").read_text(encoding="utf-8") if (root / "Makefile").exists() else ""
    docs = _public_text(root)
    for target in target_list:
        failures.extend(_check_target(root, target, makefile, docs))
    return failures


def _check_duplicate_selectors(targets: list[Target]) -> list[str]:
    failures: list[str] = []
    seen: dict[str, str] = {}
    for target in targets:
        for selector in target.inputs:
            normalized = _normalize_target(selector)
            previous = seen.setdefault(normalized, target.inputs[0])
            if previous != target.inputs[0]:
                failures.append(
                    f"duplicate optimize selector {selector!r}: {previous} and {target.inputs[0]}"
                )
    return failures


def _check_target(root: Path, target: Target, makefile: str, docs: str) -> list[str]:
    primary = target.inputs[0]
    failures: list[str] = []
    if f"mcp={primary}" not in makefile:
        failures.append(f"Makefile: help output missing optimize shortcut mcp={primary}")
    if f"mcp={primary}" not in docs:
        failures.append(f"README/docs: missing public optimize shortcut mcp={primary}")

    failures.extend(_check_target_resolution(target))

    matrix_path = root / target.matrix
    if not matrix_path.is_file():
        failures.append(f"{primary}: matrix file missing: {target.matrix}")
        return failures

    try:
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{target.matrix}: invalid JSON: {exc}"]

    failures.extend(_check_matrix_bindings(target, matrix))
    failures.extend(_check_default_dry_selection(root, target, matrix_path))
    return failures


def _check_target_resolution(target: Target) -> list[str]:
    failures: list[str] = []
    expected = target.inputs[0]
    for selector in target.inputs:
        try:
            resolved = resolve_target(selector)
        except ValueError as exc:
            failures.append(f"{expected}: selector {selector!r} failed to resolve: {exc}")
            continue
        if resolved != target:
            failures.append(f"{expected}: selector {selector!r} resolved to {resolved.inputs[0]}")
    return failures


def _check_matrix_bindings(target: Target, matrix: dict[str, Any]) -> list[str]:
    primary = target.inputs[0]
    failures: list[str] = []
    variants = {item.get("name") for item in matrix.get("tool_variants", []) if isinstance(item, dict)}
    requested_variants = _csv_set(target.variants) or set()
    required_variants = requested_variants | {target.baseline_variant} | set(target.optimized_variants)
    for variant in sorted(required_variants):
        if variant and variant not in variants:
            failures.append(f"{primary}: variant {variant!r} missing from {target.matrix}")

    instruction_names = {
        item.get("name") for item in matrix.get("instruction_variants", []) if isinstance(item, dict)
    }
    for instruction in sorted(_csv_set(target.instruction_variants) or set()):
        if instruction not in instruction_names:
            failures.append(f"{primary}: instruction variant {instruction!r} missing from {target.matrix}")

    profiles = [profile for profile in matrix.get("profiles", []) if isinstance(profile, dict)]
    profile_names = {str(profile.get("name")) for profile in profiles}
    provider_names = {str(profile.get("provider")) for profile in profiles}
    for provider in sorted(_csv_set(target.default_providers) or set()):
        if provider not in profile_names and provider not in provider_names:
            failures.append(f"{primary}: provider/profile {provider!r} missing from {target.matrix}")

    harness_names = {
        harness
        for profile in profiles
        for harness in profile.get("harnesses", [])
        if isinstance(harness, str)
    }
    for harness in sorted(_csv_set(target.default_harnesses) or set()):
        if harness not in harness_names:
            failures.append(f"{primary}: harness {harness!r} missing from {target.matrix}")

    if not matrix.get("cases"):
        failures.append(f"{primary}: matrix has no cases")
    if not target.optimized_variants:
        failures.append(f"{primary}: missing optimized variants")
    return failures


def _check_default_dry_selection(root: Path, target: Target, matrix_path: Path) -> list[str]:
    filters = MatrixFilters(
        harnesses=_csv_set(target.default_harnesses),
        instruction_variants=_csv_set(target.instruction_variants),
        providers=_csv_set(target.default_providers),
        variants=_csv_set(target.variants),
    )
    try:
        result = run_model_matrix(
            matrix_path,
            live=False,
            filters=filters,
            max_cases=1,
        )
    except Exception as exc:  # noqa: BLE001 - checker reports any shortcut failure.
        return [f"{target.inputs[0]}: default dry-run failed: {exc}"]
    if not result.get("cells"):
        return [f"{target.inputs[0]}: default dry-run selected zero cells"]
    if not result.get("results"):
        return [f"{target.inputs[0]}: default dry-run produced zero case results"]
    return []


def _public_text(root: Path = ROOT) -> str:
    paths = [
        root / "README.md",
        *sorted((root / "docs").rglob("*.md")),
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists())


if __name__ == "__main__":
    raise SystemExit(main())
