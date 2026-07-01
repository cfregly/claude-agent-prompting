Suggested title: Route exact Screenpipe phrase lookup to keyword-search

> [!NOTE]
> This page starts with the human summary. Detailed eval, command, and machine-readable material is preserved below.

## Value Proposition

- Prevents literal keyword tasks from using a broader retrieval path.
- Retains the exact baseline miss and tuned pass as replayable evidence.
- Keeps source pin, result receipt, and proposed wording together.

## Proposed Change

Clarify that keyword-search is for literal terms and exact phrases. Reserve search-content for transcript lines, screen text, speaker or window filters, tags, memories, and broader content search.

## Evidence

- Finding folder: [Screenpipe MCP Tool Tuning finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/screenpipe)
- Matrix: [screenpipe_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/screenpipe_mcp_tool_selection.json)
- Result artifact: [screenpipe_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/screenpipe_mcp_tool_selection_2026-06-28.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/screenpipe_mcp_tool_tuning_2026-06-28/evidence.json)

<details>
<summary>LLM / Machine-readable details</summary>

## Result

- packet type: improvement
- promoted by value bar: yes
- baseline variant: readme_screenpipe_mcp
- candidate variant: source_tuned_screenpipe_mcp
- baseline score: 0.857
- candidate score: 1.000
- delta: 0.143
- minimum delta: 0.010

## Cases

- broad morning recap starts summary | expected: activity-summary | forbidden: search-content,keyword-search,search-elements,export-video,list-meetings
- exact keyword uses keyword search | expected: keyword-search | forbidden: activity-summary,search-elements,export-video,list-meetings
- speaker transcript uses content search | expected: search-content | forbidden: activity-summary,keyword-search,search-elements,export-video,list-meetings
- ui button lookup uses elements | expected: search-elements | forbidden: search-content,activity-summary,keyword-search,frame-context,export-video
- known frame detail uses frame context | expected: frame-context | forbidden: search-content,get-frame-elements,activity-summary,export-video,list-meetings
- create recurring automation uses pipe | expected: create-pipe | forbidden: run-pipe,pipe-logs,activity-summary
- verify pipe output uses logs | expected: pipe-logs | forbidden: create-pipe,run-pipe,activity-summary

## Reproduce

```bash
make optimize mcp=screenpipe OUT=evals/results/screenpipe_mcp_tool_selection_2026-06-28.md
```

</details>
