# Supabase MCP Finding

Share link: [Supabase packet](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/supabase)

## Human Summary

Send this to Supabase MCP maintainers when discussing database tool boundaries. The confirmed fix is
to route DDL, schema changes, and RLS policy creation to `apply_migration`, while reserving
`execute_sql` for non-schema-changing SQL.

## Full Bundle

Bundle folder: [Supabase full PR/evidence bundle](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/supabase_mcp_database_tool_tuning_2026-06-25)

- Finding folder: [Supabase finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/supabase)
- PR body: [PR_BODY.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/supabase_mcp_database_tool_tuning_2026-06-25/PR_BODY.md)
- Reproduction doc: [REPRODUCTION.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/supabase_mcp_database_tool_tuning_2026-06-25/REPRODUCTION.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/supabase_mcp_database_tool_tuning_2026-06-25/evidence.json)
- Matrix: [supabase_mcp_database_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/supabase_mcp_database_tool_selection.json)
- Live result: [supabase_mcp_ddl_boundary_live_2026-06-25.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/supabase_mcp_ddl_boundary_live_2026-06-25.md)
- Detailed note: [Supabase MCP Tool Tuning](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/supabase-mcp-tool-tuning.md)
- Ledger: [Confirmed Improvements](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/confirmed-improvements.md)
- Reproduce: [Supabase reproduction doc](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/supabase_mcp_database_tool_tuning_2026-06-25/REPRODUCTION.md)

## Result

Confirmed improvement. This clears the adversarially-confirmed to add value bar.

The full Anthropic prompt JSON run moved from 6/9 to 9/9. The DDL and RLS boundary improved across
Anthropic, OpenAI, Gemini, native tools, and prompt JSON without regressing the passing cell.

## What Failed

The baseline chose `execute_sql` for schema-changing SQL:

- `CREATE TABLE`
- `CREATE INDEX`
- RLS policy creation

Those should route to `apply_migration`.

## Suggested Change

Make the migration boundary explicit:

```text
Use apply_migration for DDL and schema-changing SQL.

Use execute_sql only for regular SQL that does not change database schema.
```

## Evidence

- Source: [Supabase MCP repo](https://github.com/supabase/mcp)
- Matrix: [supabase_mcp_database_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/supabase_mcp_database_tool_selection.json)
- Live result: [supabase_mcp_ddl_boundary_live_2026-06-25.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/supabase_mcp_ddl_boundary_live_2026-06-25.md)
- PR packet: [supabase_mcp_database_tool_tuning_2026-06-25](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/supabase_mcp_database_tool_tuning_2026-06-25)
- Detailed note: [Supabase MCP Tool Tuning](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/supabase-mcp-tool-tuning.md)
- Ledger: [Confirmed Improvements](https://github.com/cfregly/claude-agent-harness-opt/blob/main/docs/confirmed-improvements.md)

## Reproduce

```bash
make optimize mcp=supabase
```
