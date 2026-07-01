# Reproduction for Supabase MCP Database Tool Tuning

## Source Pin

- repo: https://github.com/supabase/mcp
- commit: 100565f26d7eec6d314a08597ded22da63045923
- package: @supabase/mcp-server-supabase
- version: 0.8.2
- database_tools: packages/mcp-server-supabase/src/tools/database-operation-tools.ts
- server_instructions: packages/mcp-server-supabase/src/server.ts
- docs: https://supabase.com/docs/guides/ai-tools/mcp

## Command

```bash
python scripts/optimize_mcp.py supabase --env-file .env --live --require-live --markdown --providers anthropic,openai,gemini --harnesses prompt_json,native_tools --cases "ddl create table uses migration,ddl create index uses migration,rls policy uses migration" --out /tmp/supabase-ddl-boundary.md
```

## Value Bar

- baseline: terse_supabase_database_mcp at 0.222
- candidate: tuned_supabase_database_boundaries at 1.000
- delta: 0.778
- minimum delta: 0.010
- promote: yes

## Cases

- ddl create table uses migration | expected selection: apply_migration | confusable alternatives checked: execute_sql,list_tables
- ddl create index uses migration | expected selection: apply_migration | confusable alternatives checked: execute_sql,list_tables
- rls policy uses migration | expected selection: apply_migration | confusable alternatives checked: execute_sql,list_tables
