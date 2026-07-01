# Humwork MCP Finding

Share link: [Humwork packet](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/humwork)

## Human Summary

Send this as a guardrail packet for Humwork. The tested consultation workflow already selected the
right tools on the retained slice, so the useful artifact is the coverage case set rather than an
upstream change request.

## Full Bundle

Bundle folder: [Humwork retained guardrail bundle](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28)

- Finding folder: [Humwork finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/humwork)
- No-change packet: [PR_BODY.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28/PR_BODY.md)
- Reproduction doc: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28/REPRODUCTION.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28/evidence.json)
- Matrix: [humwork_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/humwork_mcp_tool_selection.json)
- Receipt: [humwork_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/humwork_mcp_tool_selection_2026-06-28.md)
- Sweep: [YC P2026 MCP Sweep](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/yc-p2026-mcp-sweep.md)
- Reproduce: [Humwork reproduction doc](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28/REPRODUCTION.md)

## Result

Guardrail. No upstream change is promoted.

The README-level and skill-tuned variants both passed 7/7 on Anthropic prompt JSON. That means this
did not clear the adversarially-confirmed to add value bar as an improvement, because there was no
baseline failure to fix.

## What Was Tested

The slice covered:

- starting an expert consultation
- sending a follow-up to an active session
- reading expert replies
- closing a resolved chat
- rating a closed chat
- avoiding expert spend for a basic docs question
- avoiding external chat when secrets or customer exports would be shared

## Evidence

- Source: [Humwork MCP repo](https://github.com/humworkai/humwork-mcp)
- Matrix: [humwork_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/humwork_mcp_tool_selection.json)
- Receipt: [humwork_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/humwork_mcp_tool_selection_2026-06-28.md)
- Guardrail packet: [humwork_mcp_guardrail_2026-06-28](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/humwork_mcp_guardrail_2026-06-28)
- YC sweep: [YC P2026 MCP Sweep](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/yc-p2026-mcp-sweep.md)

## Reproduce

```bash
make optimize mcp=humwork
```
