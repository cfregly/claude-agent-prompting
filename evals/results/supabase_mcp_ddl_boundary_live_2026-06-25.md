# supabase mcp ddl boundary live matrix


## Optimization Gate

Passed: yes
Optimized variants: `tuned_supabase_database_boundaries`
Baseline variant: `terse_supabase_database_mcp`
Baseline score: 0.222
Optimized score: 1.000
Baseline failures: 14
Optimized failures: 0

optimized variants passed every selected cell

## Raw Matrix

Live: yes
Passed: no
Planned: 36
Passed cases: 22
Failed cases: 14
Errors: 0
Skipped: 0
Score: 0.611

## Results

| Provider | Model | Harness | Tool Variant | Instruction Variant | Case | Status | Chosen |
|---|---|---|---|---|---|---|---|
| anthropic | claude-sonnet-4-5 | native_tools | terse_supabase_database_mcp | supabase_database_host_rules | ddl create table uses migration | failed | execute_sql |
| anthropic | claude-sonnet-4-5 | native_tools | terse_supabase_database_mcp | supabase_database_host_rules | ddl create index uses migration | failed | execute_sql |
| anthropic | claude-sonnet-4-5 | native_tools | terse_supabase_database_mcp | supabase_database_host_rules | rls policy uses migration | failed | execute_sql |
| anthropic | claude-sonnet-4-5 | native_tools | tuned_supabase_database_boundaries | supabase_database_host_rules | ddl create table uses migration | passed | apply_migration |
| anthropic | claude-sonnet-4-5 | native_tools | tuned_supabase_database_boundaries | supabase_database_host_rules | ddl create index uses migration | passed | apply_migration |
| anthropic | claude-sonnet-4-5 | native_tools | tuned_supabase_database_boundaries | supabase_database_host_rules | rls policy uses migration | passed | apply_migration |
| anthropic | claude-sonnet-4-5 | prompt_json | terse_supabase_database_mcp | supabase_database_host_rules | ddl create table uses migration | failed | execute_sql |
| anthropic | claude-sonnet-4-5 | prompt_json | terse_supabase_database_mcp | supabase_database_host_rules | ddl create index uses migration | failed | execute_sql |
| anthropic | claude-sonnet-4-5 | prompt_json | terse_supabase_database_mcp | supabase_database_host_rules | rls policy uses migration | failed | execute_sql |
| anthropic | claude-sonnet-4-5 | prompt_json | tuned_supabase_database_boundaries | supabase_database_host_rules | ddl create table uses migration | passed | apply_migration |
| anthropic | claude-sonnet-4-5 | prompt_json | tuned_supabase_database_boundaries | supabase_database_host_rules | ddl create index uses migration | passed | apply_migration |
| anthropic | claude-sonnet-4-5 | prompt_json | tuned_supabase_database_boundaries | supabase_database_host_rules | rls policy uses migration | passed | apply_migration |
| openai | gpt-4.1 | native_tools | terse_supabase_database_mcp | supabase_database_host_rules | ddl create table uses migration | failed | execute_sql |
| openai | gpt-4.1 | native_tools | terse_supabase_database_mcp | supabase_database_host_rules | ddl create index uses migration | passed | apply_migration |
| openai | gpt-4.1 | native_tools | terse_supabase_database_mcp | supabase_database_host_rules | rls policy uses migration | failed | execute_sql |
| openai | gpt-4.1 | native_tools | tuned_supabase_database_boundaries | supabase_database_host_rules | ddl create table uses migration | passed | apply_migration |
| openai | gpt-4.1 | native_tools | tuned_supabase_database_boundaries | supabase_database_host_rules | ddl create index uses migration | passed | apply_migration |
| openai | gpt-4.1 | native_tools | tuned_supabase_database_boundaries | supabase_database_host_rules | rls policy uses migration | passed | apply_migration |
| openai | gpt-4.1 | prompt_json | terse_supabase_database_mcp | supabase_database_host_rules | ddl create table uses migration | passed | apply_migration |
| openai | gpt-4.1 | prompt_json | terse_supabase_database_mcp | supabase_database_host_rules | ddl create index uses migration | passed | apply_migration |
| openai | gpt-4.1 | prompt_json | terse_supabase_database_mcp | supabase_database_host_rules | rls policy uses migration | passed | apply_migration |
| openai | gpt-4.1 | prompt_json | tuned_supabase_database_boundaries | supabase_database_host_rules | ddl create table uses migration | passed | apply_migration |
| openai | gpt-4.1 | prompt_json | tuned_supabase_database_boundaries | supabase_database_host_rules | ddl create index uses migration | passed | apply_migration |
| openai | gpt-4.1 | prompt_json | tuned_supabase_database_boundaries | supabase_database_host_rules | rls policy uses migration | passed | apply_migration |
| gemini | gemini-2.5-pro | native_tools | terse_supabase_database_mcp | supabase_database_host_rules | ddl create table uses migration | failed | execute_sql |
| gemini | gemini-2.5-pro | native_tools | terse_supabase_database_mcp | supabase_database_host_rules | ddl create index uses migration | failed | execute_sql |
| gemini | gemini-2.5-pro | native_tools | terse_supabase_database_mcp | supabase_database_host_rules | rls policy uses migration | failed | execute_sql |
| gemini | gemini-2.5-pro | native_tools | tuned_supabase_database_boundaries | supabase_database_host_rules | ddl create table uses migration | passed | apply_migration |
| gemini | gemini-2.5-pro | native_tools | tuned_supabase_database_boundaries | supabase_database_host_rules | ddl create index uses migration | passed | apply_migration |
| gemini | gemini-2.5-pro | native_tools | tuned_supabase_database_boundaries | supabase_database_host_rules | rls policy uses migration | passed | apply_migration |
| gemini | gemini-2.5-pro | prompt_json | terse_supabase_database_mcp | supabase_database_host_rules | ddl create table uses migration | failed | execute_sql |
| gemini | gemini-2.5-pro | prompt_json | terse_supabase_database_mcp | supabase_database_host_rules | ddl create index uses migration | failed | execute_sql |
| gemini | gemini-2.5-pro | prompt_json | terse_supabase_database_mcp | supabase_database_host_rules | rls policy uses migration | failed | execute_sql |
| gemini | gemini-2.5-pro | prompt_json | tuned_supabase_database_boundaries | supabase_database_host_rules | ddl create table uses migration | passed | apply_migration |
| gemini | gemini-2.5-pro | prompt_json | tuned_supabase_database_boundaries | supabase_database_host_rules | ddl create index uses migration | passed | apply_migration |
| gemini | gemini-2.5-pro | prompt_json | tuned_supabase_database_boundaries | supabase_database_host_rules | rls policy uses migration | passed | apply_migration |

## Cell Summary

| Provider | Harness | Tool Variant | Instruction Variant | Passed | Failed | Errors | Score |
|---|---|---|---|---:|---:|---:|---:|
| anthropic | native_tools | terse_supabase_database_mcp | supabase_database_host_rules | 0 | 3 | 0 | 0.000 |
| anthropic | native_tools | tuned_supabase_database_boundaries | supabase_database_host_rules | 3 | 0 | 0 | 1.000 |
| anthropic | prompt_json | terse_supabase_database_mcp | supabase_database_host_rules | 0 | 3 | 0 | 0.000 |
| anthropic | prompt_json | tuned_supabase_database_boundaries | supabase_database_host_rules | 3 | 0 | 0 | 1.000 |
| gemini | native_tools | terse_supabase_database_mcp | supabase_database_host_rules | 0 | 3 | 0 | 0.000 |
| gemini | native_tools | tuned_supabase_database_boundaries | supabase_database_host_rules | 3 | 0 | 0 | 1.000 |
| gemini | prompt_json | terse_supabase_database_mcp | supabase_database_host_rules | 0 | 3 | 0 | 0.000 |
| gemini | prompt_json | tuned_supabase_database_boundaries | supabase_database_host_rules | 3 | 0 | 0 | 1.000 |
| openai | native_tools | terse_supabase_database_mcp | supabase_database_host_rules | 1 | 2 | 0 | 0.333 |
| openai | native_tools | tuned_supabase_database_boundaries | supabase_database_host_rules | 3 | 0 | 0 | 1.000 |
| openai | prompt_json | terse_supabase_database_mcp | supabase_database_host_rules | 3 | 0 | 0 | 1.000 |
| openai | prompt_json | tuned_supabase_database_boundaries | supabase_database_host_rules | 3 | 0 | 0 | 1.000 |
