Suggested title: Clarify Firecrawl scrape versus extract for one known URL

> [!NOTE]
> This page starts with the human summary. Detailed eval, command, and machine-readable material is preserved below.

## Value Proposition

- Prevents one-known-URL tasks from being routed to broader extraction workflows.
- Keeps the cross-provider single-case evidence in a retained packet folder.
- Pairs the proposed wording with exact matrix and reproduction surfaces.

## Proposed Change

Clarify that firecrawl_scrape handles one known page, including structured JSON fields. Reserve firecrawl_extract for broader multi-page structured extraction jobs.

## Evidence

- Finding folder: [Firecrawl MCP Tool Tuning finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/firecrawl)
- Matrix: [firecrawl_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/firecrawl_mcp_tool_selection.json)
- Result artifact: [firecrawl_mcp_single_page_live_2026-06-25.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/firecrawl_mcp_single_page_live_2026-06-25.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/firecrawl_mcp_tool_tuning_2026-06-25/evidence.json)

<details>
<summary>LLM / Machine-readable details</summary>

## Result

- packet type: improvement
- promoted by value bar: yes
- baseline variant: legacy_firecrawl_mcp
- candidate variant: tuned_firecrawl_mcp_boundaries
- baseline score: 0.000
- candidate score: 1.000
- delta: 1.000
- minimum delta: 0.010

## Cases

- single known page structured fields | expected: firecrawl_scrape | forbidden: firecrawl_extract,firecrawl_batch_scrape,firecrawl_interact,firecrawl_monitor_create

## Reproduce

```bash
python scripts/optimize_mcp.py firecrawl --env-file .env --live --require-live --markdown --providers anthropic,openai,gemini --harnesses prompt_json,native_tools --cases "single known page structured fields" --out /tmp/firecrawl-single-page.md
```

</details>
