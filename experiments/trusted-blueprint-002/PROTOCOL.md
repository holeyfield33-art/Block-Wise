# Protocol: Experiment 002, trusted blueprint execution (C3)

This protocol was frozen before any model call. Hashes are in `FREEZE.json`. Experiment 001
(`../token-efficiency/`) is used read-only and is not modified.

## Hypothesis

> A coding agent using an already validated blueprint can complete the same application task at
> lower cost by delegating implementation to Block-Wise and accepting the generated result without
> redundant LLM-driven verification.

## What is reused from Experiment 001, unchanged

- **Task specifications.** T1–T4 `spec.md`, the same files whose hashes are recorded in Experiment
  001's `FREEZE.json`.
- **Hidden acceptance tests.** They live in `../token-efficiency/acceptance/` and their hashes are
  verified against Experiment 001's `FREEZE.json`. They stay outside every agent workspace.
- **Grader, transcript parser and launcher.** `grade()`, `transcript_metrics()` and the one-line
  `LAUNCHER`, imported from `../token-efficiency/reproduce.py` (frozen hash `3cd8b58d…995e`).
- **Model, environment and pricing.** The same `sonnet` alias, the same sub-agent harness, the same
  Block-Wise installation (generator commit `b01d956`, unchanged since the audited commit
  `589ca99`) and the same list-price basis.

## Approved components (`MANIFEST.json`)

Trust covers **only** these four blueprints, at their recorded `blueprint_sha256`, in the default
configuration (`apply <id> --into app`, with no `--set`). The generated program hash is recorded
for each one. `prepare` refuses to run if any blueprint file has changed.

| Task | Blueprint | Program |
|---|---|---|
| T1 | `csv_report` | report.py |
| T2 | `todo_cli` | todo.py |
| T3 | `kv_store` | store.py |
| T4 | `log_stats` | logstats.py |

## Condition C3: Trusted blueprint

The agent receives the spec, the exact blueprint id and hash, and the single command to run. It must
follow the ten trust rules in `run002.py` (`MATERIALS_C3`):
- run `apply` once;
- accept `"ok":true` as completion;
- not read, inspect or edit generated code;
- not run `check`, the program, tests or any debugging;
- not regenerate;
- not write extra files;
- report the file path and the response line.

**Differences from Experiment 001's prompt, by design:**
- **Wrapper.** The C3 wrapper drops "you may write and run your own checks in scratch/" and asks
  for a completion record instead of a check report. There is no `scratch/` folder.
- **Tool budget.** It is 5 instead of 30. A compliant run needs 2 or 3 calls.
- **Compact output.** `apply` prints one compact JSON line of 98–115 characters. It never prints
  source code.

## Evaluation (separate from generation)

1. After the agent finishes, `finalize` copies `app/` and the raw transcript.
2. It runs the hidden acceptance suite **exactly once**.
3. A failure is recorded as unsuccessful. There is no repair and no regeneration; a second
   `finalize` call is refused.
4. The agent never sees the tests, the test output or the program.

`finalize` also records whether the final program's hash equals the approved generated-program hash.
An agent that edited the code despite the rules would therefore be detected.

## Controls

| Condition | Source | Status |
|---|---|---|
| A: LLM writes the program from plain English | Experiment 001 main phase, 3 trials per task | **historical control** |
| C2: known blueprint, agent allowed to inspect and edit | Experiment 001 main phase, 3 trials (T4: 2) | **historical control** |
| C3: known blueprint, agent trusts it | this experiment | fresh |
| Zero-LLM: `blockwise apply` run directly | this experiment (`ZERO_LLM.json`) | deterministic reference, not an AI condition |

The historical controls are not fresh randomized trials. They were run earlier on the same model
alias, harness, specs and tests.

## Measurements

These are the same fields and the same status labels as Experiment 001:

| Measure | Status |
|---|---|
| Input tokens per request (uncached, cache write, cache read) | **MEASURED** |
| Number of requests | **MEASURED** |
| Repeated context tokens (total input minus the first request's input) | **MEASURED** |
| Output tokens | **UNMEASURED** (lower bound only) |
| Tool calls | **MEASURED** |
| Wall-clock time | **MEASURED** (includes queueing) |
| Test success | **MEASURED** |
| USD | **derived** from list prices; billing is **UNMEASURED** |

The cost per successful completed application is the derived input USD divided by the number of
successes.

No 5:1 output weighting is used anywhere.

## Pilot schedule (`runs/pilot/schedule.json`)

- **Runs.** One C3 run per blueprint: 4 runs, shuffled with seed 20261013.
- **Budget.** The remaining approved allowance is about 496k input tokens, out of 15M with 14.50M
  used.
- **Estimate.** A compliant run needs 3 requests. That is the same count as condition A, which used
  about 163k tokens per run. The pilot is therefore estimated at about 620k tokens, and up to about
  1.3M if agents ignore the rules and use all 5 tool calls.
- **Approval.** The estimate exceeds the remaining allowance, so **no model call is made until an
  additional spending authorization is given.**

## Decision criteria

| Verdict | Condition |
|---|---|
| **GO** | C3 is cheaper than A, with equivalent functional success, on the completed matched tasks |
| **PARTIAL** | C3 removes most of C2's overhead but still costs more than A, or the evidence is too limited |
| **NO-GO** | C3 still costs more, with no compensating measurable benefit |

A four-task pilot cannot support broad claims.

## Reproduction

```bash
export BW_BIN=<path>/blockwise
python run002.py manifest     # MANIFEST.json
python run002.py zero_llm     # ZERO_LLM.json, no model
python run002.py prepare <ws_root> <python_with_blockwise>
# one fresh agent per schedule entry, launched with exp001's LAUNCHER line; then for each:
python run002.py finalize <run_id> <transcript.jsonl> <tokens> <tool_uses> <duration_ms>
python run002.py compare      # TRUSTED_RESULTS.json
```
