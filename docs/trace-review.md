# Trace Review

Use this repo to review someone else's agent by asking their harness to export an ordered trace.
The trace should capture what the agent saw and did, not private application state.

## Event Schema

Each trace has a `steps` array. The supported event types are:

- `reasoning`: a visible thinking summary, a provider-returned reasoning block, or an agent-authored
  decision note
- `tool_call`: the tool name, call id, and arguments sent to the tool
- `tool_result`: the output, error, or status returned by the tool
- `final`: the final answer or final state summary

Run:

```bash
python -m claude_agent_prompting review-trace evals/examples/agent_trace_good.json
python -m claude_agent_prompting review-trace evals/examples/agent_trace_bad.json
python -m claude_agent_prompting trace-judge-prompt evals/examples/agent_trace_good.json
python -m claude_agent_prompting normalize-claude evals/examples/claude_messages.json
python -m claude_agent_prompting trace-suite evals/suites/agent_trace_suite.json
python -m claude_agent_prompting trace-suite evals/suites/agent_trace_suite.json --markdown
python -m claude_agent_prompting audit-agent evals/examples/agent_audit_bundle.json --markdown
```

## What To Score

The deterministic reviewer checks:

- tool calls have ids, names, and matching results
- required tools were used and forbidden tools were avoided
- arguments contain expected values
- duplicate tool calls stay below the configured limit
- reasoning appears before the first tool call when required
- each tool result is followed by reasoning before the next action
- reasoning after tool results assesses evidence, relevance, or reliability
- tool errors are followed by recovery reasoning
- final answers contain required evidence or uncertainty language

Use the LLM judge prompt for judgment that cannot be checked by string or structure alone, such as
whether the agent's reflection was good enough for the domain.

## Capturing Claude Traces

For Claude API agents with thinking enabled, capture the returned content blocks in order:

- `thinking` blocks become `reasoning` events. Store summarized thinking when available.
- `redacted_thinking` or omitted thinking should be recorded as a reasoning event with an empty
  summary and a note that it was opaque.
- `tool_use` blocks become `tool_call` events.
- your `tool_result` messages become `tool_result` events.
- final `text` blocks become `final` events.

Do not rewrite provider-returned thinking blocks when continuing a Claude tool-use conversation. The
Claude docs state that thinking blocks used with tools should be passed back unchanged. For trace
review, store a separate normalized copy for evaluation.

If a provider does not expose reasoning, do not try to extract hidden reasoning. Instead, instrument
your agent to write short decision notes before and after tool calls. Those notes are often enough to
review whether the agent understood tool outputs and made sane next-step decisions.

## Minimal Harness Contract

Ask an agent owner to export one JSON file per run:

```json
{
  "task": "What the agent was asked to do",
  "rubric": {
    "required_tools": ["web_search"],
    "max_tool_calls": 6,
    "require_reasoning_after_tool_results": true
  },
  "steps": [
    {"type": "reasoning", "summary": "Why the first tool is needed"},
    {"type": "tool_call", "id": "call_1", "name": "web_search", "args": {"query": "..."}},
    {"type": "tool_result", "tool_call_id": "call_1", "ok": true, "output": "..."},
    {"type": "reasoning", "summary": "Whether the result was reliable enough"},
    {"type": "final", "text": "Final answer"}
  ]
}
```

That is enough to review most agent failures without coupling this repo to the agent runtime.

## Regression Suites

Use a trace suite when you want to keep a fixed set of agent behaviors stable. A suite can include
known-good traces that must pass and known-bad traces that must fail below a score threshold. This is
useful after prompt edits because it checks both sides of the gate.

```json
{
  "name": "agent trace regression suite",
  "cases": [
    {"name": "good trace passes", "trace": "../examples/agent_trace_good.json", "expect_passed": true},
    {"name": "bad trace fails", "trace": "../examples/agent_trace_bad.json", "expect_passed": false, "max_score": 0.75}
  ]
}
```

## Agent Audit Bundles

Use an audit bundle when someone gives you a tool inventory and representative traces. The bundle
first lints tool names and descriptions, then reviews each trace against its rubric.

```json
{
  "name": "sample research agent audit",
  "tools": [
    {
      "name": "web_search",
      "purpose": "Find candidate sources and fresh facts from the public web.",
      "use_when": "Use for unknown, current, or broad questions where source discovery is required.",
      "avoid_when": "Avoid when a known source URL should be fetched directly."
    }
  ],
  "traces": [
    {"name": "representative run", "trace": "agent_trace_good.json"}
  ]
}
```
