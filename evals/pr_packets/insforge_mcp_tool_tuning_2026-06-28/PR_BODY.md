Suggested title: Reject relative InsForge deployment paths before create-deployment

> [!NOTE]
> This page starts with the human summary. Detailed eval, command, and machine-readable material is preserved below.

## Value Proposition

- Prevents unsafe relative deploy requests from reaching create-deployment.
- Retains the exact baseline miss and tuned pass as replayable evidence.
- Keeps source pin, result receipt, and proposed wording together.

## Proposed Change

Clarify that create-deployment requires an absolute sourceDirectory and must be avoided for relative paths, starter-template creation, deployment status lookup, or remote prepared-deployment triggering.

## Evidence

- Finding folder: [InsForge MCP Tool Tuning finding](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/insforge)
- Matrix: [insforge_mcp_tool_selection.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/insforge_mcp_tool_selection.json)
- Result artifact: [insforge_mcp_tool_selection_2026-06-28.md](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/insforge_mcp_tool_selection_2026-06-28.md)
- Evidence JSON: [evidence.json](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/pr_packets/insforge_mcp_tool_tuning_2026-06-28/evidence.json)

<details>
<summary>LLM / Machine-readable details</summary>

## Result

- packet type: improvement
- promoted by value bar: yes
- baseline variant: readme_insforge_mcp
- candidate variant: source_tuned_insforge_mcp
- baseline score: 0.938
- candidate score: 1.000
- delta: 0.062
- minimum delta: 0.010

## Cases

- new project setup reads instructions | expected: fetch-docs | forbidden: download-template,get-backend-metadata,run-raw-sql,fetch-sdk-docs
- new app bootstrap uses template | expected: download-template | forbidden: fetch-docs,create-deployment,get-backend-metadata
- backend inventory uses metadata | expected: get-backend-metadata | forbidden: get-table-schema,run-raw-sql,list-buckets,get-anon-key
- known table details use schema | expected: get-table-schema | forbidden: get-backend-metadata,run-raw-sql
- explicit sql uses raw sql | expected: run-raw-sql | forbidden: get-table-schema,get-backend-metadata,bulk-upsert
- csv import uses bulk upsert | expected: bulk-upsert | forbidden: run-raw-sql,create-bucket
- storage inventory lists buckets | expected: list-buckets | forbidden: get-backend-metadata,create-bucket,delete-bucket
- create storage bucket uses create bucket | expected: create-bucket | forbidden: list-buckets,delete-bucket
- read function uses get function | expected: get-function | forbidden: create-function,update-function,delete-function,get-container-logs
- update function uses update function | expected: update-function | forbidden: create-function,get-function,delete-function
- function logs use container logs | expected: get-container-logs | forbidden: get-function,run-raw-sql
- sdk docs use sdk docs | expected: fetch-sdk-docs | forbidden: fetch-docs,list-buckets
- client token uses anon key | expected: get-anon-key | forbidden: fetch-docs,get-backend-metadata
- absolute source deploy uses create deployment | expected: create-deployment | forbidden: download-template,start-deployment
- prepared remote upload starts deployment | expected: start-deployment | forbidden: create-deployment,download-template
- relative deploy path avoids tool | expected:  | forbidden: create-deployment,start-deployment,download-template

## Reproduce

```bash
make optimize mcp=insforge OUT=evals/results/insforge_mcp_tool_selection_2026-06-28.md
```

</details>
