#!/usr/bin/env python3
"""Validate retained prompt templates and agent recipes."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from claude_agent_harness_opt.prompt_builder import (  # noqa: E402
    RecipeError,
    lint_tools,
    load_recipe,
    render_prompt,
)
from claude_agent_harness_opt.suitability import score_use_case  # noqa: E402


VALUE_PHRASE = "adversarially-confirmed to add value"
RECIPE_DIR = "recipes"
PROMPT_DIR = "prompts"

REQUIRED_RENDERED_SECTIONS = (
    "<agent_task>",
    "<success_criteria>",
    "<done_when>",
    "<tool_call_budgets>",
    "<tool_selection>",
    "<thinking_guidance>",
    "<value_bar>",
    "<safety_and_reversibility>",
    "<context_management>",
    "<operating_loop>",
)

REQUIRED_THINKING_KEYS = ("initial_plan", "after_tool_result", "self_check")
ALLOWED_RECIPE_VERDICTS = {"agent", "workflow_or_agent_with_review"}

PROMPT_CONTRACTS = {
    "agent_system_template.md": {
        "requires_text_fence": True,
        "required_phrases": (
            "# Agent System Prompt Template",
            "<agent_task>",
            "<success_criteria>",
            "<tool_selection>",
            "<tool_call_budgets>",
            "<thinking_guidance>",
            "<safety_and_reversibility>",
            "classify complexity",
            "tool-call budget",
            "value claim",
            VALUE_PHRASE,
        ),
    },
    "llm_judge.md": {
        "requires_text_fence": True,
        "required_phrases": (
            "# LLM Judge Prompt",
            "<rubric>",
            "<agent_output>",
            "Value claim",
            "minimum improvement",
            "adversarial challenge",
            "Return JSON",
            "value_bar_passed",
        ),
    },
}


def main() -> int:
    failures = check_prompt_recipe_surfaces()
    if failures:
        print("\n".join(sorted(failures)))
        return 1
    print("prompt/recipe surface check passed")
    return 0


def check_prompt_recipe_surfaces(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    failures.extend(_check_recipes(root))
    failures.extend(_check_prompt_templates(root))
    return failures


def _check_recipes(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    recipe_dir = root / RECIPE_DIR
    if not recipe_dir.exists():
        return [f"{RECIPE_DIR}: missing recipe directory"]

    paths = sorted(recipe_dir.glob("*.json"))
    if not paths:
        return [f"{RECIPE_DIR}: no recipe files found"]

    seen_names: set[str] = set()
    for path in paths:
        rel = path.relative_to(root)
        try:
            recipe = load_recipe(path)
        except (OSError, ValueError, RecipeError) as exc:
            failures.append(f"{rel}: failed to load recipe: {exc}")
            continue

        name = str(recipe.get("name", "")).strip()
        if name != path.stem:
            failures.append(f"{rel}: recipe.name must match file stem")
        if name in seen_names:
            failures.append(f"{rel}: duplicate recipe.name: {name}")
        seen_names.add(name)

        failures.extend(_check_recipe_shape(rel, recipe))
        failures.extend(_check_recipe_score(rel, recipe))
        failures.extend(_check_rendered_recipe(rel, recipe))

        for issue in lint_tools(recipe):
            failures.append(f"{rel}: tool lint failed: {issue}")

    return failures


def _check_recipe_shape(rel: Path, recipe: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    failures.extend(_require_nonempty_list(rel, recipe, "success_criteria"))
    failures.extend(_require_nonempty_list(rel, recipe, "done_when"))

    budgets = recipe.get("budgets", {})
    if isinstance(budgets, dict):
        try:
            simple = int(budgets.get("simple", 0))
            standard = int(budgets.get("standard", 0))
            complex_budget = int(budgets.get("complex", 0))
        except (TypeError, ValueError):
            failures.append(f"{rel}: budgets must be integers")
        else:
            if not simple <= standard <= complex_budget:
                failures.append(f"{rel}: budgets must be monotonic simple <= standard <= complex")

    tools = recipe.get("tools", [])
    if isinstance(tools, list):
        for index, tool in enumerate(tools):
            if not isinstance(tool, dict):
                failures.append(f"{rel}: tools[{index}] must be an object")
                continue
            quality_checks = tool.get("quality_checks")
            if not isinstance(quality_checks, list) or not quality_checks:
                failures.append(f"{rel}: tools[{index}] missing quality_checks")

    thinking = recipe.get("thinking")
    if not isinstance(thinking, dict):
        failures.append(f"{rel}: thinking must be an object")
    else:
        for key in REQUIRED_THINKING_KEYS:
            failures.extend(_require_nonempty_list(rel, thinking, key, f"thinking.{key}"))

    guardrails = recipe.get("guardrails")
    if not isinstance(guardrails, dict):
        failures.append(f"{rel}: guardrails must be an object")
    else:
        failures.extend(
            _require_nonempty_list(rel, guardrails, "confirm_before", "guardrails.confirm_before")
        )
        failures.extend(_require_nonempty_list(rel, guardrails, "never", "guardrails.never"))

    context = recipe.get("context")
    if not isinstance(context, dict):
        failures.append(f"{rel}: context must be an object")
    else:
        for key in ("strategy", "progress_file", "compact_when", "subagent_policy"):
            if not str(context.get(key, "")).strip():
                failures.append(f"{rel}: context.{key} must be present")

    if not isinstance(recipe.get("parallel_tool_calls"), bool):
        failures.append(f"{rel}: parallel_tool_calls must be boolean")

    return failures


def _check_recipe_score(rel: Path, recipe: dict[str, Any]) -> list[str]:
    try:
        score = score_use_case(recipe.get("use_case", {}))
    except (TypeError, ValueError) as exc:
        return [f"{rel}: use_case failed to score: {exc}"]

    if score["verdict"] not in ALLOWED_RECIPE_VERDICTS:
        return [f"{rel}: use_case verdict is not agent-ready: {score['verdict']}"]
    return []


def _check_rendered_recipe(rel: Path, recipe: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    try:
        rendered = render_prompt(recipe)
    except (TypeError, ValueError, RecipeError) as exc:
        return [f"{rel}: failed to render recipe: {exc}"]

    for section in REQUIRED_RENDERED_SECTIONS:
        if section not in rendered:
            failures.append(f"{rel}: rendered prompt missing {section}")
    if VALUE_PHRASE not in rendered:
        failures.append(f"{rel}: rendered prompt missing '{VALUE_PHRASE}'")

    for tool in recipe.get("tools", []):
        if isinstance(tool, dict):
            name = str(tool.get("name", "")).strip()
            if name and name not in rendered:
                failures.append(f"{rel}: rendered prompt missing tool name {name}")

    return failures


def _check_prompt_templates(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    prompt_dir = root / PROMPT_DIR
    if not prompt_dir.exists():
        return [f"{PROMPT_DIR}: missing prompt directory"]

    paths = sorted(prompt_dir.glob("*.md"))
    if not paths:
        return [f"{PROMPT_DIR}: no prompt templates found"]

    found_names = {path.name for path in paths}
    for expected_name in sorted(set(PROMPT_CONTRACTS) - found_names):
        failures.append(f"{PROMPT_DIR}/{expected_name}: missing contracted prompt template")
    for unknown_name in sorted(found_names - set(PROMPT_CONTRACTS)):
        failures.append(f"{PROMPT_DIR}/{unknown_name}: prompt template has no surface contract")

    for path in paths:
        contract = PROMPT_CONTRACTS.get(path.name)
        if not contract:
            continue
        rel = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            failures.append(f"{rel}: prompt template is empty")
        if contract.get("requires_text_fence") and "```text" not in text:
            failures.append(f"{rel}: missing text code fence")
        for phrase in contract["required_phrases"]:
            if phrase not in text:
                failures.append(f"{rel}: missing required phrase {phrase!r}")

    return failures


def _require_nonempty_list(
    rel: Path,
    container: dict[str, Any],
    dotted_key: str,
    label: str | None = None,
) -> list[str]:
    display_key = label or dotted_key
    value = _get_dotted(container, dotted_key)
    if not isinstance(value, list) or not value:
        return [f"{rel}: {display_key} must be a nonempty list"]
    if any(not str(item).strip() for item in value):
        return [f"{rel}: {display_key} must not contain empty items"]
    return []


def _get_dotted(container: dict[str, Any], dotted_key: str) -> Any:
    current: Any = container
    for part in dotted_key.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


if __name__ == "__main__":
    raise SystemExit(main())
