"""Command line interface for the prompt kit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .adapters import claude_messages_to_trace, load_json
from .agent_audit import (
    render_agent_audit_markdown,
    review_agent_bundle,
)
from .evals import build_judge_prompt, evaluate_case, load_eval_case
from .prompt_builder import lint_tools, load_recipe, render_prompt
from .suitability import score_use_case
from .trace_suite import render_suite_markdown, run_trace_suite
from .trace_review import build_trace_judge_prompt, load_trace, review_trace


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="claude-agent-prompting")
    subparsers = parser.add_subparsers(dest="command", required=True)

    render_parser = subparsers.add_parser("render", help="render a system prompt from a recipe")
    render_parser.add_argument("recipe", type=Path)

    score_parser = subparsers.add_parser("score", help="score whether a recipe fits an agent loop")
    score_parser.add_argument("recipe", type=Path)

    lint_parser = subparsers.add_parser("lint-tools", help="lint tool names and descriptions")
    lint_parser.add_argument("recipe", type=Path)

    eval_parser = subparsers.add_parser("eval", help="run an offline eval case")
    eval_parser.add_argument("case", type=Path)

    judge_parser = subparsers.add_parser("judge-prompt", help="render an LLM judge prompt")
    judge_parser.add_argument("case", type=Path)

    trace_parser = subparsers.add_parser("review-trace", help="review an ordered agent trace")
    trace_parser.add_argument("trace", type=Path)

    trace_judge_parser = subparsers.add_parser(
        "trace-judge-prompt",
        help="render an LLM judge prompt for an ordered agent trace",
    )
    trace_judge_parser.add_argument("trace", type=Path)

    normalize_parser = subparsers.add_parser(
        "normalize-claude",
        help="normalize Claude Messages API blocks into an agent trace",
    )
    normalize_parser.add_argument("messages", type=Path)

    suite_parser = subparsers.add_parser("trace-suite", help="run a trace regression suite")
    suite_parser.add_argument("suite", type=Path)
    suite_parser.add_argument("--markdown", action="store_true", help="print a Markdown report")

    audit_parser = subparsers.add_parser(
        "audit-agent",
        help="review a tool inventory and related agent traces",
    )
    audit_parser.add_argument("bundle", type=Path)
    audit_parser.add_argument("--markdown", action="store_true", help="print a Markdown report")

    args = parser.parse_args(argv)

    if args.command == "render":
        recipe = load_recipe(args.recipe)
        sys.stdout.write(render_prompt(recipe))
        return 0

    if args.command == "score":
        recipe = load_recipe(args.recipe)
        print(json.dumps(score_use_case(recipe.get("use_case", {})), indent=2, sort_keys=True))
        return 0

    if args.command == "lint-tools":
        recipe = load_recipe(args.recipe)
        issues = lint_tools(recipe)
        print(json.dumps({"passed": not issues, "issues": issues}, indent=2, sort_keys=True))
        return 1 if issues else 0

    if args.command == "eval":
        result = evaluate_case(load_eval_case(args.case))
        print(result.to_json())
        return 0 if result.passed else 1

    if args.command == "judge-prompt":
        sys.stdout.write(build_judge_prompt(load_eval_case(args.case)))
        return 0

    if args.command == "review-trace":
        result = review_trace(load_trace(args.trace))
        print(result.to_json())
        return 0 if result.passed else 1

    if args.command == "trace-judge-prompt":
        sys.stdout.write(build_trace_judge_prompt(load_trace(args.trace)))
        return 0

    if args.command == "normalize-claude":
        trace = claude_messages_to_trace(load_json(args.messages))
        print(json.dumps(trace, indent=2, sort_keys=True))
        return 0

    if args.command == "trace-suite":
        result = run_trace_suite(args.suite)
        if args.markdown:
            sys.stdout.write(render_suite_markdown(result))
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["passed"] else 1

    if args.command == "audit-agent":
        result = review_agent_bundle(args.bundle)
        if args.markdown:
            sys.stdout.write(render_agent_audit_markdown(result))
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["passed"] else 1

    parser.error(f"unknown command: {args.command}")
    return 2
