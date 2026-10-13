# Recommendations

## Verdict: NO-GO on "Block-Wise reduces LLM spend"

The benchmark ran 56 controlled runs: 5 tasks, 4 conditions, 3 trials, with 1 run withheld under the
spending cap.
- **Cost:** Block-Wise raised the cost per successful task from **$0.082 to $0.130** (derived input
  cost, +59%).
- **Correctness:** it held correctness at 100%, the same as plain coding.
- **Savings:** none in any task, trial or workflow. Repeated use (C2) still cost +51%.

A PARTIAL verdict would need savings in at least one category. No category showed any.

## One commercialization direction: developer CLI (for humans, not for token savings)

| Direction | Assessment |
|---|---|
| **Developer CLI** (recommended) | It sells the capability the benchmark confirmed: deterministic, tested programs that pass hidden acceptance tests unedited. A human who runs `blockwise apply` saves typing and review time, and no agent turn overhead applies. It needs no new infrastructure and already exists. |
| MCP tool for coding agents | Its value depends on agents saving tokens, which was contradicted: agents verified and patched generated code, adding 1–5 turns. The MCP overhead was not measured live, but it can only add cost. Not recommended until a different agent protocol shows savings (see below). |
| Hosted template-generation API | It adds hosting cost and latency on top of a benefit that was not shown. Generation runs locally in milliseconds, so hosting adds nothing technical. Not recommended. |

**Smallest product:**
- The open-source CLI plus paid **blueprint packs** (domain templates with their acceptance tests).
- The **Studio lessons** as an education offering, which never depended on the token claim.
- Position it as "correct, tested scaffolds in one command", **not** as "cut your AI bill".

## Required changes before any savings claim is made again

1. **Remove "Measured, not assumed" from the README and docs** for `benchmarks/token_cost.py`. The
   script measures no model. It ignores per-request overhead, verification turns and `show_preset`.
   Label it as an estimate, or delete it.
2. **Fix the silent tokenizer fallback.** Without `tiktoken`, the script falls back to 4 characters
   per token and does not say so. It should print which mode it used.
3. **Make `blockwise check` find the plan from any subdirectory.** At least 5 agents ran it from
   `scratch/`, got "No plan yet" with `ok: true`, and reported success. A missing plan should not
   return `ok: true`.
4. **Make MCP responses compact JSON**, to match the CLI.

## Experiments that could change the verdict (not run; each needs its own spending approval)

Each of these tests a mechanism the data points to. None is evidence of savings yet.

- **Turn-capped protocol.** Tell the agent "apply, run the provided tests once, do not edit". If the
  run takes 3 requests, which is A's count, the template might break even. The risk is lower
  correctness when the template is wrong.
- **Large programs (1,000+ lines).** Output tokens might outweigh the turn overhead. That is untested
  here.
- **A lean custom agent.** With a small system prompt, an extra turn costs less. This narrows the gap
  but cannot reverse it unless turns fall.
- **Live MCP measurement**, in a harness that can attach the server.

## For the next decision

Treat the cost-saving story as refuted for agent use in this setup. Build on correctness and teaching
value, and only revisit "agent cost savings" if one of the experiments above shows a measured
reduction in requests per task.
