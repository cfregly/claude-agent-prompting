# firecrawl mcp single-page structured extraction live matrix


## Optimization Gate

Passed: yes
Optimized variants: `tuned_firecrawl_mcp_boundaries`
Baseline variant: `legacy_firecrawl_mcp`
Baseline score: 0.000
Optimized score: 1.000
Baseline failures: 6
Optimized failures: 0

optimized variants passed every selected cell

## Raw Matrix

Live: yes
Passed: no
Planned: 12
Passed cases: 6
Failed cases: 6
Errors: 0
Skipped: 0
Score: 0.500

## Results

| Provider | Model | Harness | Tool Variant | Instruction Variant | Case | Status | Chosen |
|---|---|---|---|---|---|---|---|
| anthropic | claude-sonnet-4-5 | native_tools | legacy_firecrawl_mcp | firecrawl_host_rules | single known page structured fields | failed | firecrawl_extract |
| anthropic | claude-sonnet-4-5 | native_tools | tuned_firecrawl_mcp_boundaries | firecrawl_host_rules | single known page structured fields | passed | firecrawl_scrape |
| anthropic | claude-sonnet-4-5 | prompt_json | legacy_firecrawl_mcp | firecrawl_host_rules | single known page structured fields | failed | firecrawl_extract |
| anthropic | claude-sonnet-4-5 | prompt_json | tuned_firecrawl_mcp_boundaries | firecrawl_host_rules | single known page structured fields | passed | firecrawl_scrape |
| openai | gpt-4.1 | native_tools | legacy_firecrawl_mcp | firecrawl_host_rules | single known page structured fields | failed | firecrawl_extract |
| openai | gpt-4.1 | native_tools | tuned_firecrawl_mcp_boundaries | firecrawl_host_rules | single known page structured fields | passed | firecrawl_scrape |
| openai | gpt-4.1 | prompt_json | legacy_firecrawl_mcp | firecrawl_host_rules | single known page structured fields | failed | firecrawl_extract |
| openai | gpt-4.1 | prompt_json | tuned_firecrawl_mcp_boundaries | firecrawl_host_rules | single known page structured fields | passed | firecrawl_scrape |
| gemini | gemini-2.5-pro | native_tools | legacy_firecrawl_mcp | firecrawl_host_rules | single known page structured fields | failed | firecrawl_extract |
| gemini | gemini-2.5-pro | native_tools | tuned_firecrawl_mcp_boundaries | firecrawl_host_rules | single known page structured fields | passed | firecrawl_scrape |
| gemini | gemini-2.5-pro | prompt_json | legacy_firecrawl_mcp | firecrawl_host_rules | single known page structured fields | failed | firecrawl_extract |
| gemini | gemini-2.5-pro | prompt_json | tuned_firecrawl_mcp_boundaries | firecrawl_host_rules | single known page structured fields | passed | firecrawl_scrape |

## Cell Summary

| Provider | Harness | Tool Variant | Instruction Variant | Passed | Failed | Errors | Score |
|---|---|---|---|---:|---:|---:|---:|
| anthropic | native_tools | legacy_firecrawl_mcp | firecrawl_host_rules | 0 | 1 | 0 | 0.000 |
| anthropic | native_tools | tuned_firecrawl_mcp_boundaries | firecrawl_host_rules | 1 | 0 | 0 | 1.000 |
| anthropic | prompt_json | legacy_firecrawl_mcp | firecrawl_host_rules | 0 | 1 | 0 | 0.000 |
| anthropic | prompt_json | tuned_firecrawl_mcp_boundaries | firecrawl_host_rules | 1 | 0 | 0 | 1.000 |
| gemini | native_tools | legacy_firecrawl_mcp | firecrawl_host_rules | 0 | 1 | 0 | 0.000 |
| gemini | native_tools | tuned_firecrawl_mcp_boundaries | firecrawl_host_rules | 1 | 0 | 0 | 1.000 |
| gemini | prompt_json | legacy_firecrawl_mcp | firecrawl_host_rules | 0 | 1 | 0 | 0.000 |
| gemini | prompt_json | tuned_firecrawl_mcp_boundaries | firecrawl_host_rules | 1 | 0 | 0 | 1.000 |
| openai | native_tools | legacy_firecrawl_mcp | firecrawl_host_rules | 0 | 1 | 0 | 0.000 |
| openai | native_tools | tuned_firecrawl_mcp_boundaries | firecrawl_host_rules | 1 | 0 | 0 | 1.000 |
| openai | prompt_json | legacy_firecrawl_mcp | firecrawl_host_rules | 0 | 1 | 0 | 0.000 |
| openai | prompt_json | tuned_firecrawl_mcp_boundaries | firecrawl_host_rules | 1 | 0 | 0 | 1.000 |
