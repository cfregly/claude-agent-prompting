# Autoresearch Hill Descent And Climbing

The useful idea from the autoresearch pattern is not the training domain. It is the two-part loop:

1. Descend into the failure surface until the weak boundary is measurable.
2. Climb out by testing the smallest candidate change against the same boundary.
3. Keep the candidate only if it beats the baseline and held-out cases do not regress.
4. Retain the matrix, result receipt, and packet so the next run does not repeat blind guesses.

In this repo, the editable surface is the agent harness:

- tool names and descriptions
- argument and output schemas
- provider native tool wrappers
- prompt JSON wrappers
- `CLAUDE.md` style rules
- skill instructions
- Agent SDK loop controls
- IDE-agent trace adapters

The experiment is a model matrix plus trace review. The score is not a vibe check. It is tool choice,
argument quality, reasoning-note quality, tool-output use, final grounding, runtime, token use,
tool-call count, and tool-error rate.

## Why It Matters

The hard problem is not only whether one model can call one tool. The hard problem is whether a
model, provider API, harness, tool catalog, project instruction file, and skill all cooperate under
real tasks. A tool description that works in one native tool interface may fail in a JSON wrapper.
A `CLAUDE.md` rule that helps one model generation can hurt another. A trace adapter can hide the
exact argument mistake that caused the failure.

The matrix turns that into a measurable surface. Hill descent finds the likely failure valley before
money is spent on live model calls. Hill climbing turns repeated failures into candidates. Held-out
confirmation keeps the candidate from overfitting the exact failed case.

## Two Halves

| Phase | Job | Output |
|---|---|---|
| Hill descent | Walk toward likely failures by inventorying the surface and writing adversarial boundary cases. | Matrix cases with expected tools, forbidden confusables, argument checks, `check_family`, and coverage receipts. |
| Hill climbing | Try the smallest change that explains repeated failures and test it against baseline plus held-out cells. | Promoted wording, schema, host-rule, or skill change with retained result and PR/evidence packet. |

## Hill Descent: Failure Discovery

Start wider than skills. Skills are useful because they encode workflow rules, but they are only one
input. The descent also uses:

- MCP `tools/list`, resource lists, and generated argument schemas
- upstream docs and source pins
- `CLAUDE.md` or host-rule instructions
- existing traces, support reports, and user complaints
- smoke-call output when credentials are available
- prior result receipts and no-change guardrails

For each surface, build a boundary map. A good boundary is where the first wrong tool call changes
cost, safety, correctness, or recoverability. Typical failure valleys include adjacent tools with
similar names, required arguments that are often omitted, resource-first paths versus direct tool
fallback, exact lookup versus broad search, metadata discovery versus full payload fetch, and no-tool
safety cases where any tool call is wrong.

Turn each boundary into a matrix case before tuning anything:

- name the expected tool or `NO_TOOL`
- name forbidden confusable tools
- add required argument assertions when a tool takes inputs
- label the case with a `check_family`
- link the case back to a source, trace, skill rule, schema, or support signal
- run `matrix-coverage` before any live provider run

This is the part that keeps the process from becoming prompt taste. If the descent cannot produce a
durable matrix or fixture, treat the observation as unproven and do not promote a fix.

## Hill Climb: Candidate Optimization

After the descent produces repeatable baseline failures, climb with the smallest candidate that
explains the failure cluster.

- runs the baseline target cells
- generates a candidate from observed failures
- reruns the target cells
- runs held-out confirmation when a candidate beats the baseline
- promotes only when the live improvement clears the threshold and held-out cells do not regress
- emits an experiment log with each keep or reject decision

Dry runs still help with scope and cost planning, but they do not satisfy the value bar.

## Retained Evals

Everything discovered during descent should stay around as eval coverage:

- promoted failures become upstream PR/evidence packets
- no-change slices become guardrail packets
- coverage receipts stay beside result receipts
- finding pages link to the retained packet folder
- future model, provider, harness, or skill changes rerun the same cases

That is why the repository keeps packet folders for both wins and guardrails. A no-change result is
not a failed investigation. It is a retained boundary that future regressions can trip.

## When It Adds Value

Use this loop when:

- tool-choice failures repeat
- a new model generation changes behavior
- a provider native tool API behaves differently from a prompt wrapper
- an Agent SDK or IDE harness hides useful trace data
- a skill or project instruction file changes tool selection
- a tool catalog grows and similar tools blur together

Do not climb when the descent is weak. The loop needs realistic cases, verifiable outcomes, visible
reasoning summaries or decision notes, captured tool outputs, and held-out checks. Without those,
hill climbing just optimizes noise.

<details>
<summary>LLM / Machine-readable details</summary>

## Command Contract

Run the baseline on target cases:

```bash
python -m claude_agent_harness_opt grind-harness evals/model_matrix/coding_tool_selection.json \
  --env-file .env \
  --live \
  --require-live \
  --providers anthropic,openai,gemini \
  --harnesses native_tools,prompt_json \
  --instruction-variants boundary_rules \
  --cases "investigate trace review flow,map model matrix implementation" \
  --heldout-cases "find python files,read known file" \
  --min-improvement 0.05 \
  --max-live-calls 80 \
  --concurrency 8 \
  --markdown
```

## Failure Modes

The main risks are:

- overfitting to target cases
- rewarding a cheap proxy that no longer tracks real user value
- missing hidden harness transformations
- comparing models with unequal thinking or output budgets
- treating hidden chain-of-thought as available when only visible summaries can be audited
- spending live API budget on cases that deterministic checks could have rejected first

The controls are the same ones used across the repo: small realistic evals, held-out cases, fixed
call budgets, trace contracts, Claude judge review, and manual inspection of real transcripts.

</details>
