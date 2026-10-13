# Protocol: Block-Wise token-efficiency benchmark

Frozen before any model call. Hashes are in `FREEZE.json`. The repository was audited at commit
`589ca99c6ff00fa967085c0f6b88fe59e3beb006`; see `BENCHMARK_REPORT.md` §1.

## Hypothesis to falsify

> Reusable, locally generated code can reduce LLM inference expenditure while preserving or
> improving functional correctness.

## Tasks (`tasks/`)

| Task | Program | Block-Wise coverage |
|---|---|---|
| T1_csv_report | `report.py` | exact blueprint `csv_report` |
| T2_todo_cli | `todo.py` | exact blueprint `todo_cli` |
| T3_kv_store | `store.py` | exact blueprint `kv_store` |
| T4_log_stats | `logstats.py` | exact blueprint `log_stats` |
| T5_inventory | `inventory.py` | **new**. No blueprint covers it; `kv_store` and the validation presets cover only part of it. |

Each `spec.md` is a neutral plain-English specification of the observable behavior: commands, exact
output text, exit codes and edge cases. It contains no solution code.
- For T1–T4, the spec was derived from the blueprint's behavior. Three wording details were then
  corrected so the spec matches what the blueprint actually does.
- T5's spec was written new.

## Acceptance tests

There are 92 command steps in 30 scenarios. Each step is one test:
- it runs `python app/<program> ARGS` in a fresh temporary directory, in order, so saved files carry
  over between steps;
- it compares stdout and the exit code exactly.

The tests are identical for all conditions. They stay outside the repository and are never shown to
agents until every run is collected; their SHA-256 hashes are in `FREEZE.json`.

Harness validation (`python reproduce.py validate`) must pass before any model call:
- every T1–T4 blueprint program passes 100%;
- the program built from the T5 hand-written `plan.json` passes 100%;
- a do-nothing program passes 0%.

A run is a **success** only if every behavioral test passes. Structural validity alone never counts.

## Conditions

| | Gets | Python available |
|---|---|---|
| **A** Conventional | spec | plain interpreter, no Block-Wise |
| **B** Structured plan | spec + the Block-Wise `plan.json` inline (T1–T4: the blueprint's rendered plan; T5: a hand-written plan) and a 10-line key to the plan format; must write the Python itself | plain interpreter, no Block-Wise |
| **C** Block-Wise tools | spec + Block-Wise CLI with the command list and usage rules adapted from `docs/agent-instructions.md`; discovers templates itself; told not to read generated code unless a fix needs it | interpreter with Block-Wise |
| **C2** Repeated use (T1–T4 only) | as C, plus "you already know the template: `apply <blueprint> --into app`" | interpreter with Block-Wise |

C2 isolates discovery cost. The difference C − C2 is the cold-start overhead, and it gives the
break-even number of uses.

**Common to all conditions:**
- the same wrapper text (workspace rules, the deliverable path, a 30-tool-call budget, one attempt,
  the final report);
- the same one-line launcher;
- a fresh sub-agent context and a fresh workspace per run;
- the same pinned model (`sonnet` alias). Sampling settings, including temperature, are not
  controllable through this interface; that is a limitation.

**Deviations from the repository's own agent docs (deliberate):**
- C uses the CLI, not MCP. Sub-agents in this environment cannot attach an MCP server.
- The docs' step "show_preset to read what it writes" is replaced by "don't read generated code
  unless a fix needs it", as the brief requires. MCP overhead is assessed statically (tool
  definition size) and labeled unmeasured in live use.

**Setup costs, recorded separately from per-task cost:**
- installing Block-Wise;
- authoring the T5 `plan.json` by hand. This took evaluator time; LLM tokens for it are not
  measured.

## Measurements (per run, `runs/<phase>/<task>/<cond>-<trial>/usage.json`)

| Field | Source | Status |
|---|---|---|
| Input tokens per request (uncached, cache-write, cache-read) | API `usage` fields in the sub-agent transcript | **MEASURED** |
| Number of LLM requests | distinct request ids in the transcript | **MEASURED** |
| Output tokens | transcript `output_tokens`, logged mid-stream | **UNMEASURED** (lower bound only) |
| Generated characters (text plus tool-call inputs) | transcript | measured, as a proxy only |
| Tool calls, Block-Wise calls, `show` calls, self-check runs | transcript | MEASURED |
| Returned tool-result size | transcript, in characters | measured, as characters |
| Wall-clock time | agent completion record | MEASURED (includes queueing, since runs are concurrent) |
| Tests passed, success, program size, unexpected files | acceptance harness | MEASURED |
| Billed USD | none available | **UNMEASURED** |

Cost savings in USD are therefore **not** claimed. Token reductions are reported from measured
input tokens:

`Reduction % = (A − X) / A × 100`

Any USD figure in the report is labeled *derived* (measured input tokens × list price) and kept
separate from billing.

Every input-token total includes a fixed agent-harness overhead (the system prompt and tool
definitions), which is the same in every condition. It is reported separately as
`first_request_input`.

## Schedule

- **Pilot** (this approval gate): 7 runs. T1 × {A, B, C, C2} and T5 × {A, B, C}, 1 trial each. The
  order is shuffled with seed 20261012 and run concurrently.
- **Full** (only after spending approval): 5 tasks × {A, B, C} × 3 trials = 45 runs, plus T1–T4 × C2
  × 3 = 12 runs, for 57 runs in total.

Failed runs are kept and never replaced. Nothing in tasks, tests or prompts changes after the freeze.
Any change to the harness is recorded in `BENCHMARK_REPORT.md`.

## Contamination controls

- No agent sees another run's output.
- A and B have no Block-Wise installation in their interpreter.
- No agent sees the acceptance tests or a generated solution file. Exception: condition B receives the
  plan, which is by design a structural description of the program.
- Every tool call in every transcript is scanned for paths outside the run's workspace.
