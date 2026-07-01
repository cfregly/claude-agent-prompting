# OpenWork UI MCP Guardrail PR Packet

Share link: [OpenWork UI MCP Guardrail full PR/evidence bundle](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/openwork_ui_mcp_guardrail_2026-06-28)

## Human Summary

Send this packet when an OpenWork maintainer wants the tested UI bridge slice. It packages the matrix, retained live receipt, and reproduction command, but it does not recommend an upstream change because the baseline already passed.

## Full Bundle

Bundle folder: [openwork_ui_mcp_guardrail_2026-06-28](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/openwork_ui_mcp_guardrail_2026-06-28)

- Finding folder: [OpenWork UI MCP Guardrail finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/openwork)
- PR title: [PR_TITLE.txt](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/openwork_ui_mcp_guardrail_2026-06-28/PR_TITLE.txt)
- PR body: [PR_BODY.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/openwork_ui_mcp_guardrail_2026-06-28/PR_BODY.md)
- Reproduction doc: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/openwork_ui_mcp_guardrail_2026-06-28/REPRODUCTION.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/openwork_ui_mcp_guardrail_2026-06-28/evidence.json)
- Matrix: [openwork_ui_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/openwork_ui_mcp_tool_selection.json)
- Live result: [openwork_ui_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/openwork_ui_mcp_tool_selection_2026-06-28.md)
- Detailed note: [yc-p2026-mcp-sweep.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/yc-p2026-mcp-sweep.md)

## Result

Guardrail. No upstream change is promoted because the baseline already passed the tested slice.

The live Anthropic prompt JSON run kept both docs-level and source-tuned variants at 7/7, so the packet is guardrail evidence rather than a promoted change.

## Evidence

- Source: [OpenWork repo](https://github.com/different-ai/openwork)
- Matrix: [openwork_ui_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/openwork_ui_mcp_tool_selection.json)
- Live result: [openwork_ui_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/openwork_ui_mcp_tool_selection_2026-06-28.md)
- Detailed note: [yc-p2026-mcp-sweep.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/yc-p2026-mcp-sweep.md)
- Ledger: [Confirmed Improvements](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/confirmed-improvements.md)

## Reproduce

[REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/openwork_ui_mcp_guardrail_2026-06-28/REPRODUCTION.md) contains the exact command and pinned matrix surface.
