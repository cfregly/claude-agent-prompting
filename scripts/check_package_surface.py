#!/usr/bin/env python3
"""Validate package metadata, import entry points, and generated artifact hygiene."""

from __future__ import annotations

from pathlib import Path, PurePosixPath
import subprocess
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
PROJECT_NAME = "claude-agent-harness-opt"
MODULE_NAME = "claude_agent_harness_opt"
CONSOLE_SCRIPT = "claude-agent-harness-opt"
CONSOLE_TARGET = "claude_agent_harness_opt.cli:main"
STALE_PACKAGE_NAMES = ("claude_agent_harness_optimization",)
REQUIRED_GITIGNORE_PATTERNS = (
    ".env",
    ".venv/",
    "__pycache__/",
    "*.pyc",
    "*.egg-info/",
    ".pytest_cache/",
    "dist/",
    "build/",
)


def main() -> int:
    failures = check_package_surface()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("package surface check passed")
    return 0


def check_package_surface(
    root: Path = ROOT,
    *,
    tracked_paths: list[str] | None = None,
    run_smoke: bool = True,
) -> list[str]:
    failures: list[str] = []
    failures.extend(_check_pyproject(root))
    failures.extend(_check_license_file(root))
    failures.extend(_check_package_tree(root))
    failures.extend(_check_gitignore(root))
    tracked = tracked_paths if tracked_paths is not None else _git_tracked_paths(root)
    failures.extend(_check_tracked_artifacts(tracked))
    if run_smoke:
        failures.extend(_check_runtime_entrypoint(root))
    return failures


def _check_pyproject(root: Path = ROOT) -> list[str]:
    path = root / "pyproject.toml"
    if not path.exists():
        return ["pyproject.toml: missing"]
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        return [f"pyproject.toml: invalid TOML: {exc}"]

    failures: list[str] = []
    build_system = data.get("build-system", {})
    if build_system.get("build-backend") != "setuptools.build_meta":
        failures.append("pyproject.toml: build-backend must be setuptools.build_meta")
    requires = build_system.get("requires", [])
    if not isinstance(requires, list) or not any(str(item).startswith("setuptools") for item in requires):
        failures.append("pyproject.toml: build-system.requires must include setuptools")

    project = data.get("project", {})
    if project.get("name") != PROJECT_NAME:
        failures.append(f"pyproject.toml: project.name must be {PROJECT_NAME}")
    if project.get("readme") != "README.md":
        failures.append("pyproject.toml: project.readme must be README.md")
    if project.get("requires-python") != ">=3.11":
        failures.append("pyproject.toml: requires-python must be >=3.11")
    license_info = project.get("license", {})
    if not isinstance(license_info, dict) or license_info.get("text") != "MIT":
        failures.append("pyproject.toml: project.license.text must be MIT")

    scripts = project.get("scripts", {})
    if scripts.get(CONSOLE_SCRIPT) != CONSOLE_TARGET:
        failures.append(f"pyproject.toml: console script {CONSOLE_SCRIPT} must target {CONSOLE_TARGET}")
    return failures


def _check_license_file(root: Path = ROOT) -> list[str]:
    path = root / "LICENSE"
    if not path.exists():
        return ["LICENSE: missing"]
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    if not text.startswith("MIT License\n"):
        failures.append("LICENSE: must start with MIT License")
    if "Copyright (c) 2026 Contributors" not in text:
        failures.append("LICENSE: missing expected copyright holder")
    if "Permission is hereby granted, free of charge" not in text:
        failures.append("LICENSE: missing MIT permission grant")
    return failures


def _check_package_tree(root: Path = ROOT) -> list[str]:
    package_dir = root / MODULE_NAME
    failures: list[str] = []
    if not package_dir.is_dir():
        return [f"{MODULE_NAME}: missing package directory"]
    for filename in ("__init__.py", "__main__.py", "cli.py"):
        if not (package_dir / filename).is_file():
            failures.append(f"{MODULE_NAME}/{filename}: missing")

    main_path = package_dir / "__main__.py"
    if main_path.exists():
        text = main_path.read_text(encoding="utf-8")
        if "from .cli import main" not in text or "raise SystemExit(main())" not in text:
            failures.append(f"{MODULE_NAME}/__main__.py: must delegate to cli.main")

    cli_path = package_dir / "cli.py"
    if cli_path.exists() and "def main(" not in cli_path.read_text(encoding="utf-8"):
        failures.append(f"{MODULE_NAME}/cli.py: missing main function")

    for stale_name in STALE_PACKAGE_NAMES:
        stale_dir = root / stale_name
        if not stale_dir.exists():
            continue
        stale_sources = [
            path
            for path in stale_dir.rglob("*.py")
            if "__pycache__" not in path.relative_to(stale_dir).parts
        ]
        if stale_sources:
            failures.append(f"{stale_name}: stale package source must not be present")
    return failures


def _check_gitignore(root: Path = ROOT) -> list[str]:
    path = root / ".gitignore"
    if not path.exists():
        return [".gitignore: missing"]
    patterns = set(path.read_text(encoding="utf-8").splitlines())
    return [
        f".gitignore: missing generated artifact pattern {pattern}"
        for pattern in REQUIRED_GITIGNORE_PATTERNS
        if pattern not in patterns
    ]


def _check_tracked_artifacts(tracked_paths: list[str]) -> list[str]:
    failures: list[str] = []
    for raw_path in tracked_paths:
        path = PurePosixPath(raw_path)
        parts = set(path.parts)
        if "__pycache__" in parts or raw_path.endswith(".pyc"):
            failures.append(f"{raw_path}: tracked Python bytecode is not allowed")
        if ".pytest_cache" in parts:
            failures.append(f"{raw_path}: tracked pytest cache is not allowed")
        if path.parts and path.parts[0] in {"dist", "build"}:
            failures.append(f"{raw_path}: tracked build artifact is not allowed")
        if any(part.endswith(".egg-info") for part in path.parts):
            failures.append(f"{raw_path}: tracked egg-info artifact is not allowed")
    return failures


def _check_runtime_entrypoint(root: Path = ROOT) -> list[str]:
    result = subprocess.run(
        [sys.executable, "-m", MODULE_NAME, "--help"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return [f"{MODULE_NAME}: python -m help failed with exit code {result.returncode}"]
    if f"usage: {CONSOLE_SCRIPT}" not in result.stdout:
        return [f"{MODULE_NAME}: python -m help does not use console script name"]
    return []


def _git_tracked_paths(root: Path = ROOT) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


if __name__ == "__main__":
    raise SystemExit(main())
