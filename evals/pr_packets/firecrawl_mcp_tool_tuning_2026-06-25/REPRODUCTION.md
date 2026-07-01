# Reproduction for Firecrawl MCP Tool Tuning

## Source Pin

- repo: https://github.com/firecrawl/firecrawl-mcp-server
- commit: e744bba494c0e77086d66af838d7a64fab52f138
- package: firecrawl-mcp
- version: 3.22.0
- legacy_descriptions: src/legacy/index.md
- current_descriptions: src/index.ts
- docs: README.md#how-to-choose-a-tool

## Command

```bash
python scripts/optimize_mcp.py firecrawl --env-file .env --live --require-live --markdown --providers anthropic,openai,gemini --harnesses prompt_json,native_tools --cases "single known page structured fields" --out /tmp/firecrawl-single-page.md
```

## Value Bar

- baseline: legacy_firecrawl_mcp at 0.000
- candidate: tuned_firecrawl_mcp_boundaries at 1.000
- delta: 1.000
- minimum delta: 0.010
- promote: yes

## Cases

- single known page structured fields | expected selection: firecrawl_scrape | confusable alternatives checked: firecrawl_extract,firecrawl_batch_scrape,firecrawl_interact,firecrawl_monitor_create
