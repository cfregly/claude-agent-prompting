# Tool Writing Best Practices

This guide maps Anthropic's tool-writing guidance into repo checks and review habits. The standard
is still adversarially-confirmed to add value: a tool change must beat a baseline on realistic
evals and survive an adversarial review with no open objections.

## Prototype First

Start with a quick tool prototype, connect it to a local agent loop, then test it yourself before
writing broad abstractions. The prototype should expose the real rough edges agents see:

- unclear tool names
- missing parameter guidance
- oversized outputs
- vague errors
- confusing overlap with nearby tools

Use `lint-tools`, `optimize-tools`, and a small trace suite before adding more tools.

## Evaluation Tasks

Evaluation prompts should be grounded in realistic workflows, not shallow sandbox commands. Strong
cases often need multiple tool calls and enough ambiguity to stress tool boundaries.

Every eval prompt needs a verifiable response or outcome:

- exact text or structured subset checks for deterministic outcomes
- numeric ranges for approximate answers
- flexible phrase groups for valid alternate wording
- regex checks for output shape
- Claude judge rubrics for semantic correctness

Avoid overly strict verifiers that fail correct answers because of harmless formatting or alternate
phrasing. Use `expected_any`, `expected_regex`, numeric ranges, and judge rubrics before reaching for
exact text.

Expected tools are useful diagnostics, but they should not overfit the strategy. Prefer
`valid_tool_paths` when several routes can solve the task. Use exact required sequences only when
the order is part of the real contract.

## Held-Out Cases

Keep separate held-out tool-selection cases. Use training cases to design a candidate tool
description, then use held-out cases to check whether the candidate generalized.

In audit bundles:

- `tool_selection_cases` are calibration cases used to explain known boundaries
- `heldout_tool_selection_cases` are cases the candidate should pass without being tailored to them
- `value_bar` records the baseline, candidate, minimum delta, and adversarial challenge

## Transcript Review

Read the raw transcripts, not only the agent's own feedback. Agents may omit the exact behavior that
matters. Review:

- visible reasoning or decision notes
- tool calls and arguments
- tool results and errors
- final answer grounding
- redundant calls
- invalid parameters
- token-heavy outputs
- runtime and tool-call counts when available

This repo captures ordered traces and checks directed reasoning before and after tool calls. Add
runtime, token, and error metrics to trace metadata when a harness can export them.

## Tool Surface

More tools can make agents worse. Prefer a few high-impact tools that match real workflows over many
thin wrappers around raw endpoints.

Good tools should:

- map to natural task subdivisions
- consolidate frequently chained operations when that saves context
- return relevant context rather than exhaustive data
- keep names and descriptions distinct
- expose strict input models with unambiguous parameter names
- state `use_when`, `avoid_when`, `quality_checks`, `output_schema`, and `error_guidance`

For large catalogs, namespace by service or resource so the agent can see boundaries in the name.
Evaluate prefix and suffix naming with the model matrix because naming effects can vary by model.

## Tool Outputs

Tool outputs should return meaningful context, not raw implementation detail. Favor names, titles,
dates, source types, snippets, and directly useful ids over opaque ids or low-level fields. When a
downstream tool needs a technical id, include a clear natural-language label next to it.

Large-output tools should provide context controls:

- `response_format` such as concise or detailed
- pagination or page size
- filtering
- range selection
- truncation with instructions for how to continue

Tool errors should be actionable. Instead of returning only a stack trace or status code, explain
what parameter failed and give the agent a valid shape to retry.

## Description Tuning

Describe tools as if onboarding a capable new teammate. Make implicit context explicit:

- domain terms
- valid query formats
- relationships between resources
- expected input and output shapes
- examples for confusing parameters
- recovery guidance for common errors

Use the model matrix and harness grind to measure description changes across providers, model
versions, reasoning settings, harnesses, `CLAUDE.md`, and skills. The grind loop should include
target cases, held-out cases, a minimum improvement threshold, and an experiment log. Promote only
when the candidate clears the value bar.

Use `harness-checks` to select the next failure class to test. The catalog includes adjacent tool
boundaries, no-tool safety, argument quality, error recovery, output budget, resource versus tool
routing, directed thinking, harness parity, and reproducibility.

## Repo Commands

```bash
python -m claude_agent_harness_optimization eval evals/examples/search_answer.json
python -m claude_agent_harness_optimization optimize-tools evals/examples/agent_audit_bundle.json --markdown
python -m claude_agent_harness_optimization audit-agent evals/examples/agent_audit_bundle.json --claude-judge
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/coding_tool_selection.json --env-file .env --live --markdown
python -m claude_agent_harness_optimization grind-harness evals/model_matrix/coding_tool_selection.json --env-file .env --live --heldout-cases "find python files,read known file" --min-improvement 0.05 --markdown
python -m claude_agent_harness_optimization harness-checks --markdown
```
