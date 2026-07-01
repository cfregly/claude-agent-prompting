Suggested title: Retain OpenWork UI MCP guardrail evidence

> [!NOTE]
> This page starts with the human summary. Detailed eval, command, and machine-readable material is preserved below.

## Guardrail Value

- Shows the UI bridge workflow is already well routed on the retained slice.
- Keeps action discovery, semantic execution, status, snapshot, and no-tool coordinate-click cases together.
- Makes the guardrail reusable as future eval coverage.

## Recommendation

No upstream wording change is recommended from this slice. Keep the packet as regression coverage for status checks, snapshots, action listing, semantic action execution, and no-tool boundaries.

## Evidence

- Finding folder: [OpenWork UI MCP Guardrail finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/openwork)
- Matrix: [openwork_ui_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/openwork_ui_mcp_tool_selection.json)
- Result artifact: [openwork_ui_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/openwork_ui_mcp_tool_selection_2026-06-28.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/openwork_ui_mcp_guardrail_2026-06-28/evidence.json)

<details>
<summary>LLM / Machine-readable details</summary>

## Result

- packet type: guardrail
- promoted by value bar: no
- baseline variant: docs_openwork_ui_mcp
- candidate variant: source_tuned_openwork_ui_mcp
- baseline score: 1.000
- candidate score: 1.000
- delta: 0.000
- minimum delta: 0.010

## Cases

- bridge check uses status | expected: ui_status | forbidden: ui_snapshot,ui_list_actions,ui_execute_action
- unknown current screen uses snapshot | expected: ui_snapshot | forbidden: ui_status,ui_list_actions,ui_execute_action
- action discovery uses list actions | expected: ui_list_actions | forbidden: ui_status,ui_snapshot,ui_execute_action
- known action id executes action | expected: ui_execute_action | forbidden: ui_status,ui_snapshot,ui_list_actions
- unknown action id lists actions first | expected: ui_list_actions | forbidden: ui_status,ui_execute_action
- coordinate click avoids semantic bridge | expected:  | forbidden: ui_status,ui_snapshot,ui_list_actions,ui_execute_action
- app maybe closed checks status before action | expected: ui_status | forbidden: ui_snapshot,ui_list_actions,ui_execute_action

## Reproduce

```bash
make optimize mcp=openwork OUT=evals/results/openwork_ui_mcp_tool_selection_2026-06-28.md
```

</details>
