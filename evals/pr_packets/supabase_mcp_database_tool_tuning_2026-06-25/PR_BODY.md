Suggested title: Route Supabase schema-changing SQL through migrations

> [!NOTE]
> This page starts with the human summary. Detailed eval, command, and machine-readable material is preserved below.

## Value Proposition

- Prevents schema changes from bypassing auditable migrations.
- Packages the retained DDL/RLS live cells behind the public Supabase finding.
- Keeps the reproducible matrix, result receipt, and proposed wording in one folder.

## Proposed Change

Clarify that apply_migration is required for DDL, schema changes, indexes, functions, triggers, extension enablement, and RLS policy changes. Reserve execute_sql for non-schema-changing SQL.

## Evidence

- Finding folder: [Supabase MCP Database Tool Tuning finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/supabase)
- Matrix: [supabase_mcp_database_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/supabase_mcp_database_tool_selection.json)
- Result artifact: [supabase_mcp_ddl_boundary_live_2026-06-25.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/supabase_mcp_ddl_boundary_live_2026-06-25.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/supabase_mcp_database_tool_tuning_2026-06-25/evidence.json)

<details>
<summary>LLM / Machine-readable details</summary>

## Result

- packet type: improvement
- promoted by value bar: yes
- baseline variant: terse_supabase_database_mcp
- candidate variant: tuned_supabase_database_boundaries
- baseline score: 0.222
- candidate score: 1.000
- delta: 0.778
- minimum delta: 0.010

## Cases

- ddl create table uses migration | expected: apply_migration | forbidden: execute_sql,list_tables
- ddl create index uses migration | expected: apply_migration | forbidden: execute_sql,list_tables
- rls policy uses migration | expected: apply_migration | forbidden: execute_sql,list_tables

## Reproduce

```bash
python scripts/optimize_mcp.py supabase --env-file .env --live --require-live --markdown --providers anthropic,openai,gemini --harnesses prompt_json,native_tools --cases "ddl create table uses migration,ddl create index uses migration,rls policy uses migration" --out /tmp/supabase-ddl-boundary.md
```

</details>
