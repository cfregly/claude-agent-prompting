# Reproduction for InsForge MCP Tool Tuning

## Source Pin

- repo: https://github.com/InsForge/insforge-mcp
- commit: dad794d445d05e7df2efcb8280dba59682b97a87
- package: @insforge/mcp
- package_version: 1.2.10
- yc: InsForge, YC P2026
- slice: backend metadata, database operations, starter templates, storage, edge functions, deployments, logs, docs, and public client tokens

## Command

```bash
make optimize mcp=insforge OUT=evals/results/insforge_mcp_tool_selection_2026-06-28.md
```

## Value Bar

- baseline: readme_insforge_mcp at 0.938
- candidate: source_tuned_insforge_mcp at 1.000
- delta: 0.062
- minimum delta: 0.010
- promote: yes

## Cases

- new project setup reads instructions | expected selection: fetch-docs | confusable alternatives checked: download-template,get-backend-metadata,run-raw-sql,fetch-sdk-docs
- new app bootstrap uses template | expected selection: download-template | confusable alternatives checked: fetch-docs,create-deployment,get-backend-metadata
- backend inventory uses metadata | expected selection: get-backend-metadata | confusable alternatives checked: get-table-schema,run-raw-sql,list-buckets,get-anon-key
- known table details use schema | expected selection: get-table-schema | confusable alternatives checked: get-backend-metadata,run-raw-sql
- explicit sql uses raw sql | expected selection: run-raw-sql | confusable alternatives checked: get-table-schema,get-backend-metadata,bulk-upsert
- csv import uses bulk upsert | expected selection: bulk-upsert | confusable alternatives checked: run-raw-sql,create-bucket
- storage inventory lists buckets | expected selection: list-buckets | confusable alternatives checked: get-backend-metadata,create-bucket,delete-bucket
- create storage bucket uses create bucket | expected selection: create-bucket | confusable alternatives checked: list-buckets,delete-bucket
- read function uses get function | expected selection: get-function | confusable alternatives checked: create-function,update-function,delete-function,get-container-logs
- update function uses update function | expected selection: update-function | confusable alternatives checked: create-function,get-function,delete-function
- function logs use container logs | expected selection: get-container-logs | confusable alternatives checked: get-function,run-raw-sql
- sdk docs use sdk docs | expected selection: fetch-sdk-docs | confusable alternatives checked: fetch-docs,list-buckets
- client token uses anon key | expected selection: get-anon-key | confusable alternatives checked: fetch-docs,get-backend-metadata
- absolute source deploy uses create deployment | expected selection: create-deployment | confusable alternatives checked: download-template,start-deployment
- prepared remote upload starts deployment | expected selection: start-deployment | confusable alternatives checked: create-deployment,download-template
- relative deploy path avoids tool | expected selection:  | confusable alternatives checked: create-deployment,start-deployment,download-template
