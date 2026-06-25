#!/usr/bin/env python3
"""Run a live SDK agent smoke test and emit runtime trace JSONL.

This script is intentionally dependency-light at import time. Provider SDKs are imported only in the
selected provider path so repo tests can compile the file without installing every SDK.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.metadata as metadata
import json
import os
from typing import Any


PROMPT_TEMPLATE = (
    "Before using a tool, write DECISION_NOTE_BEFORE with complexity, tool budget, "
    "evidence needed, and stop criteria. Then call pwd_tool with command pwd. "
    "After the tool result, write DECISION_NOTE_AFTER with quality, verification, "
    "and stop decision. Then answer HARNESS_OK {marker} and the directory."
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "provider",
        choices=("claude-agent-sdk", "google-adk", "openai-agents"),
    )
    parser.add_argument("--version-only", action="store_true")
    args = parser.parse_args()

    if args.version_only:
        print(_package_version(args.provider))
        return 0

    if args.provider == "claude-agent-sdk":
        asyncio.run(_run_claude_agent_sdk())
        return 0
    if args.provider == "openai-agents":
        asyncio.run(_run_openai_agents())
        return 0
    if args.provider == "google-adk":
        asyncio.run(_run_google_adk())
        return 0
    raise AssertionError(args.provider)


def _emit(event: dict[str, Any]) -> None:
    print(json.dumps(event, sort_keys=True), flush=True)


def _package_version(package: str) -> str:
    return metadata.version(package)


async def _run_claude_agent_sdk() -> None:
    from claude_agent_sdk import ClaudeAgentOptions, create_sdk_mcp_server, query, tool

    @tool(
        "pwd_tool",
        "Return the current working directory. Use this only when command is exactly pwd.",
        {"command": str},
    )
    async def pwd_tool(args: dict[str, Any]) -> dict[str, Any]:
        return {"content": [{"type": "text", "text": os.getcwd()}]}

    marker = "claude_agent_sdk"
    server = create_sdk_mcp_server(name="aho", version="0.0.1", tools=[pwd_tool])
    options = ClaudeAgentOptions(
        allowed_tools=["mcp__aho__pwd_tool"],
        cwd=os.getcwd(),
        max_budget_usd=float(os.environ.get("CLAUDE_AGENT_SDK_MAX_BUDGET_USD", "0.50")),
        max_turns=int(os.environ.get("CLAUDE_AGENT_SDK_MAX_TURNS", "4")),
        mcp_servers={"aho": server},
        model=os.environ.get("CLAUDE_AGENT_MODEL", "claude-sonnet-4-5"),
        permission_mode="bypassPermissions",
        setting_sources=[],
        skills=[],
        tools=["mcp__aho__pwd_tool"],
    )
    _emit(
        {
            "metadata": {
                "package": "claude-agent-sdk",
                "package_version": _package_version("claude-agent-sdk"),
            },
            "type": "metadata",
        }
    )
    async for message in query(prompt=PROMPT_TEMPLATE.format(marker=marker), options=options):
        _emit_claude_message(message)


def _emit_claude_message(message: Any) -> None:
    class_name = type(message).__name__
    if class_name == "AssistantMessage":
        for block in getattr(message, "content", []):
            block_name = type(block).__name__
            if block_name == "TextBlock":
                _emit({"text": getattr(block, "text", ""), "type": "final"})
            elif block_name == "ToolUseBlock":
                _emit(
                    {
                        "arguments": getattr(block, "input", {}),
                        "id": getattr(block, "id", ""),
                        "tool_name": getattr(block, "name", ""),
                        "type": "tool_call",
                    }
                )
    elif class_name == "UserMessage":
        for block in getattr(message, "content", []):
            if type(block).__name__ == "ToolResultBlock":
                _emit(
                    {
                        "output": _stringify(getattr(block, "content", "")),
                        "tool_call_id": getattr(block, "tool_use_id", ""),
                        "type": "tool_result",
                    }
                )
    elif class_name == "ResultMessage":
        _emit(
            {
                "duration_ms": getattr(message, "duration_ms", None),
                "status": getattr(message, "subtype", ""),
                "total_cost_usd": getattr(message, "total_cost_usd", None),
                "type": "run_result",
            }
        )


async def _run_openai_agents() -> None:
    from agents import Agent, Runner, function_tool

    @function_tool(name_override="pwd_tool")
    def pwd_tool(command: str) -> str:
        return os.getcwd()

    marker = "openai_agents_sdk"
    agent = Agent(
        name="aho-sdk-smoke",
        instructions=(
            "Use pwd_tool for current-directory requests. Emit visible DECISION_NOTE_BEFORE before "
            "the tool call when possible, and DECISION_NOTE_AFTER after the result. Do not invent "
            "the directory."
        ),
        model=os.environ.get("OPENAI_AGENT_MODEL", "gpt-4.1"),
        tools=[pwd_tool],
    )
    _emit(
        {
            "metadata": {
                "package": "openai-agents",
                "package_version": _package_version("openai-agents"),
            },
            "type": "metadata",
        }
    )
    result = await Runner.run(agent, PROMPT_TEMPLATE.format(marker=marker), max_turns=4)
    for item in result.new_items:
        _emit_openai_item(item)


def _emit_openai_item(item: Any) -> None:
    item_type = type(item).__name__
    raw = getattr(item, "raw_item", None)
    if item_type == "MessageOutputItem":
        text = _openai_text(raw)
        if text:
            _emit({"text": text, "type": "final"})
    elif item_type == "ToolCallItem":
        _emit(
            {
                "arguments": _json_or_empty(getattr(raw, "arguments", "{}")),
                "id": getattr(raw, "call_id", ""),
                "tool_name": getattr(raw, "name", ""),
                "type": "tool_call",
            }
        )
    elif item_type == "ToolCallOutputItem":
        raw_item = getattr(item, "raw_item", {}) or {}
        _emit(
            {
                "output": getattr(item, "output", ""),
                "tool_call_id": raw_item.get("call_id", "") if isinstance(raw_item, dict) else "",
                "type": "tool_result",
            }
        )


async def _run_google_adk() -> None:
    if "GOOGLE_API_KEY" not in os.environ and os.environ.get("GEMINI_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

    from google.adk import Agent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    def pwd_tool(command: str) -> str:
        return os.getcwd()

    marker = "google_adk"
    agent = Agent(
        name="aho_sdk_smoke",
        instruction=(
            "Use pwd_tool for current-directory requests. Emit DECISION_NOTE_BEFORE before the tool "
            "and DECISION_NOTE_AFTER after the result. Final must include HARNESS_OK google_adk."
        ),
        model=os.environ.get("GOOGLE_ADK_MODEL", "gemini-2.5-flash"),
        tools=[pwd_tool],
    )
    _emit(
        {
            "metadata": {
                "package": "google-adk",
                "package_version": _package_version("google-adk"),
            },
            "type": "metadata",
        }
    )
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="aho", user_id="u")
    runner = Runner(app_name="aho", agent=agent, session_service=session_service)
    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=PROMPT_TEMPLATE.format(marker=marker))],
    )
    async for event in runner.run_async(
        user_id="u",
        session_id=session.id,
        new_message=content,
    ):
        _emit_google_event(event)


def _emit_google_event(event: Any) -> None:
    text = ""
    function_calls = []
    function_responses = []
    content = getattr(event, "content", None)
    for part in getattr(content, "parts", []) or []:
        if getattr(part, "text", None):
            text += part.text
        if getattr(part, "function_call", None):
            function_calls.append(part.function_call)
        if getattr(part, "function_response", None):
            function_responses.append(part.function_response)
    if text:
        _emit({"text": text, "type": "final"})
    for call in function_calls:
        _emit(
            {
                "arguments": dict(getattr(call, "args", {}) or {}),
                "id": getattr(call, "id", "") or getattr(call, "name", ""),
                "tool_name": getattr(call, "name", ""),
                "type": "tool_call",
            }
        )
    for result in function_responses:
        response = getattr(result, "response", {}) or {}
        _emit(
            {
                "output": _stringify(response),
                "tool_call_id": getattr(result, "id", "") or getattr(result, "name", ""),
                "type": "tool_result",
            }
        )


def _openai_text(raw: Any) -> str:
    parts = []
    for item in getattr(raw, "content", []) or []:
        text = getattr(item, "text", "")
        if text:
            parts.append(text)
    return "\n".join(parts)


def _json_or_empty(text: str) -> dict[str, Any]:
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return decoded if isinstance(decoded, dict) else {}


def _stringify(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True)


if __name__ == "__main__":
    raise SystemExit(main())
