---
name: agent-audit
description: Review an agent's tool inventory, tool calls, reasoning summaries, tool outputs, final answers, and value-bar proof using this repo's trace-review harness. Use when asked to audit, test, score, or review agent traces, Claude Messages API transcripts, tool schemas, trace suites, or agent audit bundles for tool-use quality, inter-tool reasoning, recovery behavior, final answer grounding, and whether the work is adversarially-confirmed to add value.
---

# Agent Audit

Use the repo's CLI to produce deterministic trace reviews before giving judgment, then run the live
Claude judge for real semantic audits. Prefer existing JSON artifacts over reconstructing a trace
from prose. Treat "adversarially-confirmed to add value" as the pass bar.

## Decision Tree

1. If the user asks whether tool descriptions or schemas cause bad tool choice, use `optimize-tools`.
2. If the user provides a tool inventory plus traces, use `audit-agent`.
3. If the user provides Agent SDK or IDE-agent event exports, use `normalize-runtime`, then review the normalized trace.
4. If the user asks about a new model, provider, reasoning mode, `CLAUDE.md`, or skill tuning, use `model-matrix`.
5. If matrix failures repeat across a harness or provider, use `grind-harness` with target cases,
   held-out cases, a live run, a minimum improvement threshold, and a call cap.
6. If the user asks for upstream pull requests or maintainer-ready evidence, run `upstream-pr-packet`
   after the matrix result is saved.
7. If the user asks what other harness checks to run, use `harness-checks`.
8. If the user provides a regression suite, use `trace-suite`.
9. If the user provides one normalized trace, use `review-trace`.
10. If the user provides Claude Messages API content blocks, use `normalize-claude`, then review the normalized trace.
11. If the user provides raw prose or screenshots, ask for exported JSON unless a small manual trace can be built without guessing.
12. If an audit bundle lacks `value_bar`, treat it as failed until the value claim, baseline,
   candidate, threshold, and adversarial review are supplied.

## Commands

Run from the repo root.

```bash
python -m claude_agent_harness_optimization audit-agent <bundle.json> --markdown
python -m claude_agent_harness_optimization audit-agent <bundle.json> --claude-judge --markdown
python -m claude_agent_harness_optimization optimize-tools <bundle.json> --markdown
python -m claude_agent_harness_optimization optimize-tools <bundle.json> --claude-judge
python -m claude_agent_harness_optimization model-matrix <matrix.json> --markdown
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/agent_audit_skill_selection.json --env-file .env --live --require-live --providers anthropic --harnesses prompt_json --variants thin_workflow_tools --instruction-variants no_skill,agent_audit_skill --markdown
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/harness_trace_adapters.json --live --require-live --providers trace_fixture --harnesses agent_sdk_trace,cursor_trace --variants exported_trace_tools --instruction-variants exported_trace --markdown
python -m claude_agent_harness_optimization model-matrix <matrix.json> --env-file .env --live --concurrency 8 --markdown
python -m claude_agent_harness_optimization grind-harness <matrix.json> --env-file .env --live --require-live --heldout-cases "<case 1>,<case 2>" --min-improvement 0.05 --concurrency 8 --markdown
python -m claude_agent_harness_optimization trace-suite <suite.json> --markdown
python -m claude_agent_harness_optimization review-trace <trace.json>
python -m claude_agent_harness_optimization review-trace <trace.json> --claude-judge
python -m claude_agent_harness_optimization normalize-claude <messages.json>
python -m claude_agent_harness_optimization normalize-runtime <events.json>
python -m claude_agent_harness_optimization trace-judge-prompt <trace.json>
python -m claude_agent_harness_optimization harness-checks --markdown
python -m claude_agent_harness_optimization upstream-pr-packet <matrix-result.json> --matrix <matrix.json> --target-name "<project>" --baseline-variant <baseline> --candidate-variant <candidate> --out-dir /tmp/upstream-pr
```

Use JSON output when another program will consume the result. Use `--markdown` when reporting to a
human.

## Review Method

1. Run the deterministic command first.
2. Read the failed checks, grouped by `structure`, `tool_use`, `reasoning`, and `final`.
3. Inspect the trace around any failed check before proposing a fix.
4. Run `optimize-tools` when the failure involves wrong tools, missing arguments, duplicate calls, or vague tool boundaries.
5. Run `model-matrix` when the fix may vary by model, provider, harness, `CLAUDE.md`, skill, or system instruction.
6. Run `grind-harness` when a repeated matrix failure needs a candidate tool-description or harness instruction change.
   Treat it as a bounded hill-climb: target failed cases, generate a candidate, rerun live cells,
   check held-out cases, and promote only when the value bar passes.
7. Check the value bar. Do not pass an audit without baseline improvement and adversarial confirmation.
8. For real audits, run `--claude-judge` so Claude reviews visible reasoning
   summaries, tool outputs, tool descriptions, selection cases, final grounding, and value over baseline.
9. Recommend prompt or tool changes only when they map directly to a failed check or Claude judge
   finding.
10. If an upstream project should receive a pull request, generate an `upstream-pr-packet` with
   source pins, exact examples, score deltas, and reproduction commands.
11. Use `trace-judge-prompt` only when you need a portable judge prompt instead of a live Claude API
   call.

## What To Look For

- Tools: duplicate names, vague purposes, endpoint-shaped wrappers, missing `use_when` or
  `avoid_when`, missing `input_schema`, missing `output_schema`, missing `quality_checks`, missing
  context controls for large outputs, missing error guidance, overlapping search tools.
- Tool calls: wrong tool, missing required tool, forbidden tool, bad arguments, duplicate calls, over-budget calls.
- Metrics: missing runtime, token, tool-call count, or tool-error summaries from representative runs.
- Selection cases: missing verifiable outcomes, missing held-out cases, missing expected tools,
  missing forbidden tools, missing contrast between similar tools, missing rationale, exact tool
  order that overfits one valid strategy.
- Model matrix: provider-specific failures, native-tool failures, JSON-choice failures, baseline versus tuned description gaps, instruction variant regressions.
- Skills: stale decision trees, missing routing rules, instructions that only restate tool names,
  no no-skill baseline, no thin-description stress case, or no held-out cases showing the skill
  adds value beyond clear tool descriptions.
- Harness grind: repeated failures that can be turned into a candidate variant, retested live
  against the baseline, confirmed against held-out cases, and logged as kept or rejected.
- Tool outputs: missing result, result linked to no call, errors without recovery.
- Reasoning: no plan before the first tool, missing complexity, missing tool budget, missing
  evidence or stop criteria, no reflection after results, missing quality, missing verification, or
  missing continue or stop decision.
- Final answer: unsupported claims, missing uncertainty, failure to use gathered evidence.
- Value bar: missing value claim, missing baseline, weak delta, no adversarial challenge, open objections.
- Upstream PR packet: missing source pin, missing exact example, missing reproduction command,
  missing baseline or candidate score, missing delta, or no link to the full evidence.

## Reporting

Lead with the result and score. Then list the highest-impact failed checks and the concrete change
that would address each one. When the user asks for a summary, include backing data instead of only
conclusions.

Backing data should include the exact evidence available for the claim:

- matrix or bundle name
- upstream version or commit pin when present
- baseline and candidate variants
- pass counts, scores, deltas, and minimum threshold
- provider, model, harness, instruction variant, and case names for live results
- failed cases or objections that explain why a change was not promoted
- command or artifact path used to produce the result

Use this format:

```text
Result: pass/fail, score X.XXX

Backing data:
- baseline: ...
- candidate: ...
- signal: ...
- source: ...

Findings:
- [category] failed check: evidence from trace. Suggested change.

Commands run:
- ...
```

Do not claim hidden reasoning exists. Use visible thinking summaries, provider-returned thinking
blocks, or explicit decision notes. If reasoning is unavailable, say the trace is not instrumented
well enough to audit inter-tool reasoning.
