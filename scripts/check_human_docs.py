#!/usr/bin/env python3
"""Validate public Markdown keeps human-readable content before audit detail."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_MARKDOWN_GLOBS = ("README.md", "docs/**/*.md", "evals/pr_packets/**/*.md")
LLM_SUMMARY = "<summary>LLM / Machine-readable details</summary>"
REPO_LINK = "https://github.com/cfregly/claude-agent-harness-opt/"
ROOT_HUMAN_SECTIONS = (
    "## Demo",
    "## Share This",
    "## Quickstart",
    "## What it implements",
    "## How It Works",
    "## Start Here",
    "## Shareable Bundles",
)
ROOT_MACHINE_HEADINGS = (
    "## Layout",
    "## Founder Packets",
    "## Claude Code Skill",
    "## Claude Judge",
    "## Tool Selection Optimization",
    "## Verify it",
    "## Sources",
)
MACHINE_DETAIL_RE = re.compile(
    r"(?i)(?:scripts/check_|matrix-coverage|matrix-coverage-suite|claude_agent_harness_opt|"
    r"evals/(?:results|model_matrix|targets|pr_packets)|evidence\.json|schema|"
    r"check_family|tool_selection_cases|source pins|coverage\.required)"
)


def main() -> int:
    failures = check_human_docs()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("human docs check passed")
    return 0


def check_human_docs(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    for path in _public_markdown_paths(root):
        text = path.read_text(encoding="utf-8")
        rel = _rel(path, root)
        failures.extend(_check_details_balance(rel, text))
        if rel.as_posix() == "README.md":
            failures.extend(_check_root_readme(rel, text))
        elif _is_bundle_index(rel):
            failures.extend(_check_bundle_index(rel, text))
        elif _is_sendable_packet(rel):
            failures.extend(_check_sendable_packet(rel, text))
        else:
            failures.extend(_check_machine_detail_placement(rel, text))
    return failures


def _check_details_balance(rel: Path, text: str) -> list[str]:
    failures: list[str] = []
    if text.count("<details>") != text.count("</details>"):
        failures.append(f"{rel}: unbalanced <details> disclosures")
    if LLM_SUMMARY in text and "</details>" not in text:
        failures.append(f"{rel}: LLM disclosure is missing closing </details>")
    return failures


def _check_root_readme(rel: Path, text: str) -> list[str]:
    failures: list[str] = []
    summary_index = text.find(LLM_SUMMARY)
    if summary_index == -1:
        failures.append(f"{rel}: missing bottom LLM / Machine-readable details disclosure")
        summary_index = len(text)

    previous = -1
    for heading in ROOT_HUMAN_SECTIONS:
        index = text.find(heading)
        if index == -1:
            failures.append(f"{rel}: missing human-facing section {heading}")
            continue
        if index > summary_index:
            failures.append(f"{rel}: human-facing section {heading} is inside LLM details")
        if index < previous:
            failures.append(f"{rel}: section {heading} is out of human-first order")
        previous = index

    for heading in ROOT_MACHINE_HEADINGS:
        index = text.find(heading)
        if index != -1 and index < summary_index:
            failures.append(f"{rel}: machine section {heading} appears before LLM details")

    if "## License" in text and summary_index > text.find("## License"):
        failures.append(f"{rel}: LLM details must stay above License and below human sections")
    if "scripts/check_" in text[:summary_index]:
        failures.append(f"{rel}: checker inventory appears above LLM details")
    return failures


def _check_sendable_packet(rel: Path, text: str) -> list[str]:
    failures: list[str] = []
    first_lines = "\n".join(text.splitlines()[:12])
    human_index = text.find("## Human Summary")
    bundle_index = text.find("## Full Bundle")
    if "Share link: [" not in first_lines:
        failures.append(f"{rel}: share link must be clickable in the first 12 lines")
    if "Share link: [" in first_lines and REPO_LINK not in first_lines:
        failures.append(f"{rel}: share link must use a public GitHub URL")
    if human_index == -1:
        failures.append(f"{rel}: missing ## Human Summary before artifact links")
    if bundle_index == -1:
        failures.append(f"{rel}: missing ## Full Bundle")
    if human_index != -1 and bundle_index != -1 and human_index > bundle_index:
        failures.append(f"{rel}: Human Summary must appear before Full Bundle")
    if bundle_index != -1 and bundle_index > 900:
        failures.append(f"{rel}: Full Bundle links are too far from the top")
    return failures


def _check_bundle_index(rel: Path, text: str) -> list[str]:
    failures: list[str] = []
    bundles_index = text.find("## Shareable Bundles")
    summary_index = text.find(LLM_SUMMARY)
    if bundles_index == -1:
        failures.append(f"{rel}: missing ## Shareable Bundles")
    if summary_index == -1:
        failures.append(f"{rel}: machine-heavy doc must end with LLM / Machine-readable details")
    elif bundles_index != -1 and bundles_index > summary_index:
        failures.append(f"{rel}: Shareable Bundles table must appear before LLM details")
    return failures


def _check_machine_detail_placement(rel: Path, text: str) -> list[str]:
    failures: list[str] = []
    signals = _machine_detail_count(text)
    summary_index = text.find(LLM_SUMMARY)
    if _needs_llm_details(text, signals) and summary_index == -1:
        failures.append(f"{rel}: machine-heavy doc must end with LLM / Machine-readable details")
        return failures
    if summary_index != -1:
        before = text[:summary_index]
        if _machine_detail_count(before) >= 12:
            failures.append(f"{rel}: too much machine-readable detail appears before LLM disclosure")
        if len(before.splitlines()) > 140:
            failures.append(f"{rel}: human-facing content before LLM disclosure is too long")
    return failures


def _needs_llm_details(text: str, signals: int) -> bool:
    lines = len(text.splitlines())
    return (lines >= 120 and signals >= 8) or signals >= 20


def _machine_detail_count(text: str) -> int:
    return len(MACHINE_DETAIL_RE.findall(text))


def _is_sendable_packet(rel: Path) -> bool:
    parts = rel.parts
    if len(parts) >= 4 and parts[0] == "docs" and parts[1] == "findings" and rel.name == "README.md":
        return True
    if len(parts) >= 4 and parts[0] == "evals" and parts[1] == "pr_packets" and rel.name == "README.md":
        return True
    return False


def _is_bundle_index(rel: Path) -> bool:
    return rel.as_posix() == "docs/findings/README.md"


def _public_markdown_paths(root: Path = ROOT) -> list[Path]:
    paths: set[Path] = set()
    for pattern in PUBLIC_MARKDOWN_GLOBS:
        paths.update(path for path in root.glob(pattern) if path.is_file())
    return sorted(paths)


def _rel(path: Path, root: Path = ROOT) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return path


if __name__ == "__main__":
    raise SystemExit(main())
