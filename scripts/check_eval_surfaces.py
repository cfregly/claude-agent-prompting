#!/usr/bin/env python3
"""Validate retained non-matrix eval surfaces without live credentials."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from claude_agent_harness_opt.e2e import E2EError, run_e2e_spec  # noqa: E402
from claude_agent_harness_opt.harness_checks import load_check_catalog  # noqa: E402
from claude_agent_harness_opt.live_harness import (  # noqa: E402
    LiveHarnessError,
    run_live_harness_spec,
)
from claude_agent_harness_opt.trace_suite import run_trace_suite  # noqa: E402


E2E_DIR = ROOT / "evals" / "e2e"
LIVE_HARNESSES_DIR = ROOT / "evals" / "live_harnesses"
TRACE_SUITES_DIR = ROOT / "evals" / "suites"
CHECKS_DIR = ROOT / "evals" / "checks"


def main() -> int:
    failures = check_eval_surfaces()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("eval surface check passed")
    return 0


def check_eval_surfaces() -> list[str]:
    failures: list[str] = []
    failures.extend(_check_e2e_specs())
    failures.extend(_check_live_harness_specs())
    failures.extend(_check_trace_suites())
    failures.extend(_check_check_catalogs())
    return failures


def _check_e2e_specs() -> list[str]:
    failures: list[str] = []
    paths = sorted(E2E_DIR.glob("*.json"))
    if not paths:
        return ["evals/e2e: no E2E specs found"]
    for path in paths:
        rel = path.relative_to(ROOT)
        try:
            spec = _load_object(path)
        except ValueError as exc:
            failures.append(f"{rel}: {exc}")
            continue
        failures.extend(_check_e2e_spec_shape(rel, spec))
        try:
            result = run_e2e_spec(path, dry_run=True)
        except E2EError as exc:
            failures.append(f"{rel}: dry-run failed: {exc}")
            continue
        if not result.get("passed"):
            failures.append(f"{rel}: dry-run did not pass")
        if not result.get("checks"):
            failures.append(f"{rel}: dry-run produced no checks")
    return failures


def _check_e2e_spec_shape(rel: Path, spec: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if not str(spec.get("name", "")).strip():
        failures.append(f"{rel}: missing name")
    required_env = spec.get("env", {}).get("required", [])
    if not isinstance(required_env, list) or not required_env:
        failures.append(f"{rel}: env.required must be a nonempty list")
    checks = spec.get("checks")
    if not isinstance(checks, list) or not checks:
        failures.append(f"{rel}: checks must be a nonempty list")
        return failures
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            failures.append(f"{rel}: checks[{index}] must be an object")
            continue
        prefix = f"{rel}: checks[{index}]"
        if not str(check.get("name", "")).strip():
            failures.append(f"{prefix} missing name")
        if check.get("type", "http_json") != "http_json":
            failures.append(f"{prefix} type must be http_json")
        method = str(check.get("method", "GET")).upper()
        if method not in {"GET", "HEAD"}:
            failures.append(f"{prefix} method must be GET or HEAD for read-only specs")
        if check.get("read_only") is not True:
            failures.append(f"{prefix} read_only must be true")
        if not str(check.get("url", "")).strip():
            failures.append(f"{prefix} missing url")
        if "expect_status" not in check:
            failures.append(f"{prefix} missing expect_status")
        if not any(key in check for key in ("expect_json_path", "expect_json_value", "expect_json_contains")):
            failures.append(f"{prefix} missing JSON expectation")
    return failures


def _check_live_harness_specs() -> list[str]:
    failures: list[str] = []
    paths = sorted(LIVE_HARNESSES_DIR.glob("*.json"))
    if not paths:
        return ["evals/live_harnesses: no live harness specs found"]
    with tempfile.TemporaryDirectory(prefix="aho-live-harness-dry-run-") as tmpdir:
        for path in paths:
            rel = path.relative_to(ROOT)
            try:
                spec = _load_object(path)
            except ValueError as exc:
                failures.append(f"{rel}: {exc}")
                continue
            failures.extend(_check_live_harness_spec_shape(rel, spec))
            try:
                result = run_live_harness_spec(path, dry_run=True, out_dir=tmpdir)
            except LiveHarnessError as exc:
                failures.append(f"{rel}: dry-run failed: {exc}")
                continue
            if not result.get("passed"):
                failures.append(f"{rel}: dry-run did not pass")
            expected_cells = len(spec.get("cases", [])) * len(spec.get("harnesses", []))
            if len(result.get("results", [])) != expected_cells:
                failures.append(f"{rel}: dry-run did not select every case/harness cell")
    return failures


def _check_live_harness_spec_shape(rel: Path, spec: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if not str(spec.get("name", "")).strip():
        failures.append(f"{rel}: missing name")
    cases = spec.get("cases")
    harnesses = spec.get("harnesses")
    if not isinstance(cases, list) or not cases:
        failures.append(f"{rel}: cases must be a nonempty list")
    if not isinstance(harnesses, list) or not harnesses:
        failures.append(f"{rel}: harnesses must be a nonempty list")
    value_bar = spec.get("value_bar")
    if not isinstance(value_bar, dict) or not str(value_bar.get("claim", "")).strip():
        failures.append(f"{rel}: value_bar.claim must be present")
    if isinstance(value_bar, dict) and not str(value_bar.get("adversarial_check", "")).strip():
        failures.append(f"{rel}: value_bar.adversarial_check must be present")
    for index, case in enumerate(cases if isinstance(cases, list) else []):
        if not isinstance(case, dict):
            failures.append(f"{rel}: cases[{index}] must be an object")
            continue
        if not str(case.get("name", "")).strip():
            failures.append(f"{rel}: cases[{index}] missing name")
        if not str(case.get("prompt_template", case.get("prompt", ""))).strip():
            failures.append(f"{rel}: cases[{index}] missing prompt_template")
    for index, harness in enumerate(harnesses if isinstance(harnesses, list) else []):
        if not isinstance(harness, dict):
            failures.append(f"{rel}: harnesses[{index}] must be an object")
            continue
        if not str(harness.get("name", "")).strip():
            failures.append(f"{rel}: harnesses[{index}] missing name")
        command = harness.get("command")
        if not isinstance(command, list) or not command:
            failures.append(f"{rel}: harnesses[{index}] command must be a nonempty list")
        if not str(harness.get("adapter", "")).strip():
            failures.append(f"{rel}: harnesses[{index}] missing adapter")
    return failures


def _check_trace_suites() -> list[str]:
    failures: list[str] = []
    paths = sorted(TRACE_SUITES_DIR.glob("*.json"))
    if not paths:
        return ["evals/suites: no trace suites found"]
    for path in paths:
        rel = path.relative_to(ROOT)
        try:
            result = run_trace_suite(path)
        except Exception as exc:  # noqa: BLE001 - report malformed suites without hiding others.
            failures.append(f"{rel}: trace suite failed: {exc}")
            continue
        if not result.get("passed"):
            failures.append(f"{rel}: trace suite expectations did not pass")
        if not result.get("cases"):
            failures.append(f"{rel}: trace suite has no cases")
    return failures


def _check_check_catalogs() -> list[str]:
    failures: list[str] = []
    paths = sorted(CHECKS_DIR.glob("*.json"))
    if not paths:
        return ["evals/checks: no check catalogs found"]
    seen_ids: set[str] = set()
    for path in paths:
        rel = path.relative_to(ROOT)
        try:
            catalog = load_check_catalog(path)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{rel}: check catalog failed: {exc}")
            continue
        for check in catalog.get("checks", []):
            check_id = str(check.get("id", ""))
            if check_id in seen_ids:
                failures.append(f"{rel}: duplicate check id across catalogs: {check_id}")
            seen_ids.add(check_id)
            if not str(check.get("prompt_pattern", "")).strip():
                failures.append(f"{rel}: check {check_id} missing prompt_pattern")
    return failures


def _load_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("must be a JSON object")
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
