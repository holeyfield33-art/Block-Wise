# Block-Wise token-efficiency benchmark: report

**Verdict: NO-GO** for the cost-saving claim. On every task, Block-Wise made a completed task more
expensive, not cheaper. Correctness was the same, 100% in every condition.

| Condition | Runs | Success | Mean input tokens | Derived input cost per successful task* |
|---|---|---|---|---|
| **A** Plain spec | 15 | 15/15 | 163,549 | **$0.082** |
| **B** Spec + plan.json | 15 | 15/15 | 170,106 | **$0.091** (+11%) |
| **C** Block-Wise CLI, cold start | 15 | 15/15 | 376,248 | **$0.130** (+59%) |
| **C2** Block-Wise CLI, template known | 11 | 11/11 | 350,529 | **$0.124** (+51%) |

\*Derived cost is measured input tokens multiplied by Sonnet 5.5 list prices: $2.00/M uncached,
$2.50/M cache write, $0.20/M cache read. It is **not billing data**.
- Output cost is **UNMEASURED**. The transcript logs only a lower bound, which comes to about $0.001
  per run in every condition.
- The generated-characters proxy shows Block-Wise runs produced *more* text, not less (see §4).

The hypothesis, «Reusable, locally generated code can reduce LLM inference expenditure while
preserving or improving functional correctness», is **falsified for this setup**:
- Correctness was preserved.
- Expenditure went up, from +36% to +194% in input tokens depending on the task.

---

## 1. Repository audit (Phase 1, commit `589ca99`)

- **Tests and docs.** 217 tests pass and 1 is skipped (it needs Python 3.15). Ruff is clean. Every
  documented CLI command, all six MCP tools and the exit codes behave as documented.
- **Blueprints.** Unedited, all four blueprints pass 100% of the frozen acceptance tests: csv_report
  9/9, todo_cli 18/18, kv_store 19/19 and log_stats 9/9.
- **`benchmarks/token_cost.py` measures no model.** It compares the size of generated code with the
  size of a CLI call string and assumes output tokens cost 5×. The README and docs label this
  "Measured, not assumed". It also has these gaps:
  - without `tiktoken` it silently falls back to 4 characters per token, and its output doesn't say
    which mode it used;
  - it omits per-request overhead;
  - it omits the `show_preset` step the docs tell agents to run;
  - it omits the verification turns an agent spends after applying a template.

  This benchmark replaces that estimate with transcript-measured usage.
- **MCP.** The tools return pretty-printed JSON, which is larger than the CLI's compact output. The
  640-token figure for the tool definitions is an estimate; the definitions measure 2,412
  characters.

## 2. Protocol and validity

The full protocol is in `PROTOCOL.md`. Hashes in `FREEZE.json` were re-verified after the runs, and
the tests, tasks, `reproduce.py` and `PROTOCOL.md` all match.

| Check | Result |
|---|---|
| Harness validation, before and after the runs | 4/4 blueprints pass 100%; the T5 plan build passes 37/37; the negative control passes 0/9 |
| Served model | the same model in all 63 runs (main and pilot) |
| Isolation | 0 tool calls touched a path outside the run's workspace |
| Generated-code reads (`show`) | 0 in all C/C2 runs, as instructed |
| Fixed harness overhead | 50,656 input tokens on the first request of every run, in every condition |
| Failed runs | none; nothing was replaced |

**Deviations from the frozen schedule:**

1. **56 of 57 runs.**
   - Run `r53` (T4 log_stats, C2, trial 2) was **not executed**: the approved cap was 15M input
     tokens, and 14.50M had been used by then.
   - T4 Block-Wise runs used up to 646k tokens each, so the remaining 496k could not safely cover
     one more.
   - T4/C2 therefore has n = 2. The run is listed as not executed in `results.csv`.
2. **Batched launches.** Runs were launched in batches (15, 15, 15, 9, then 1, 1) so spending could
   be checked against the cap. The schedule order did not change.
3. **Analysis script added after the runs.** `harness/analyze.py` was added for derived costs, per-cell
   statistics and drift checks. It reads the frozen outputs. `reproduce.py` is unchanged.
4. **Pilot kept separate.** The 7 pilot runs are reported in `PILOT_RESULTS.md` and agree with the
   main results.

## 3. Results per task (main phase, measured)

Columns:
- **Input**: mean input tokens per run (sd).
- **Δ vs A**: input-token reduction against condition A, `(A − X) / A`. Negative means Block-Wise cost more.
- **Derived $**: the derived input cost per run.
- **Repairs**: the number of times the agent re-ran its own checks after the first.

| Task | Cond | n | Success | Input (sd) | Δ tokens vs A | Derived $ | Δ $ vs A | Requests | Repairs | Wall-clock (s) |
|---|---|---|---|---|---|---|---|---|---|---|
| T1 csv_report | A | 3 | 3/3 | 163,782 (69) | — | 0.083 | — | 3.0 | 0 | 22.1 |
| | B | 3 | 3/3 | 168,326 (55) | −2.8% | 0.088 | −6.5% | 3.0 | 0 | 19.5 |
| | C | 3 | 3/3 | 379,487 (35,226) | **−131.7%** | 0.131 | −58.2% | 6.7 | 1.7 | 30.5 |
| | C2 | 3 | 3/3 | 280,848 (101,671) | −71.5% | 0.108 | −30.8% | 5.0 | 0.7 | 21.9 |
| T2 todo_cli | A | 3 | 3/3 | 163,024 (100) | — | 0.081 | — | 3.0 | 0 | 16.8 |
| | B | 3 | 3/3 | 169,499 (186) | −4.0% | 0.090 | −10.7% | 3.0 | 0 | 15.6 |
| | C | 3 | 3/3 | 398,961 (1,562) | **−144.7%** | 0.136 | −67.7% | 7.0 | 1.0 | 29.1 |
| | C2 | 3 | 3/3 | 359,841 (35,954) | −120.7% | 0.127 | −56.8% | 6.3 | 1.3 | 28.0 |
| T3 kv_store | A | 3 | 3/3 | 162,907 (188) | — | 0.081 | — | 3.0 | 0 | 15.7 |
| | B | 3 | 3/3 | 170,060 (16) | −4.4% | 0.091 | −12.3% | 3.0 | 0 | 15.3 |
| | C | 3 | 3/3 | 398,237 (59,944) | **−144.5%** | 0.134 | −65.9% | 7.0 | 1.3 | 29.7 |
| | C2 | 3 | 3/3 | 359,673 (35,533) | −120.8% | 0.126 | −55.8% | 6.3 | 1.0 | 27.1 |
| T4 log_stats | A | 3 | 3/3 | 163,663 (110) | — | 0.082 | — | 3.0 | 0 | 17.4 |
| | B | 3 | 3/3 | 169,282 (104) | −3.4% | 0.090 | −9.0% | 3.0 | 0 | 16.5 |
| | C | 3 | 3/3 | 480,555 (154,747) | **−193.6%** | 0.153 | −85.7% | 8.3 | 2.7 | 36.7 |
| | C2 | 2 | 2/2 | 427,370 (42,407) | −161.1% | 0.140 | −70.5% | 7.5 | 2.5 | 32.7 |
| T5 inventory (no blueprint) | A | 3 | 3/3 | 164,369 (136) | — | 0.083 | — | 3.0 | 0 | 18.4 |
| | B | 3 | 3/3 | 173,365 (72) | −5.5% | 0.096 | −14.7% | 3.0 | 0 | 18.5 |
| | C | 3 | 3/3 | 224,002 (169) | −36.3% | 0.099 | −18.5% | 4.0 | 0 | 21.9 |

**Notes on the measurements:**
- Wall-clock includes queueing, because runs were concurrent.
- Per-run data is in `results.csv`, `results.json` and `analysis.json`. Raw attempts are in
  `runs/main/<task>/<cond>-<trial>/`: the program, the agent's scratch files, `usage.json`,
  `grade.json` and the agent's report.

## 4. Why Block-Wise cost more

1. **Each request re-reads the whole context.** A run's cost is set mainly by its number of LLM
   requests:
   - Every request re-reads about 50.6k tokens of fixed agent context plus everything so far.
   - A finished in 3 requests every time: read the task, write and test, report.
   - C on a blueprint task took 6–11, and C2 took 4–8.
   - One extra request costs more input than the roughly 1k output tokens a blueprint saves by not
     writing a 100-line program.
2. **The agents did not trust code they hadn't read.** They had been told not to read the generated
   code, so they tested it, and then they changed it:
   - **20 of 23** applied-blueprint runs edited the generated program, adding BOM handling,
     `nan`/`inf` handling, non-list or non-dict JSON handling and trailing-blank rules.
   - **None of these edits was needed.** The unedited blueprints pass every acceptance test.
   - Each edit led to a re-test, and each re-test was another request.
3. **Writing did not go down.** Mean generated characters (text plus tool inputs) on T1–T4 were
   3,148 for A, 3,978 for C and 3,418 for C2. Instead of writing the program, the agents wrote test
   scripts and patches.
4. **Even the best case lost.** Only 3 runs left the generated code untouched:
   - r30 and r42 (T1, C2) used 222k tokens each;
   - r49 (T4, C) used 339k.

   r30 and r42 had zero discovery and zero edits, and still used **+36%** input tokens against A
   (163,782), because they took 4 requests instead of 3.
5. **The structured plan (B) adds context and saves nothing.** B received the plan inline (2–5k
   tokens). Its cost was 3–6% higher in tokens and 7–15% higher in derived cost than A, and
   correctness was already at ceiling.

## 5. Status of claims

| Claim | Status | Evidence |
|---|---|---|
| Block-Wise reduces input tokens per completed task | **Unsupported (contradicted)** | Higher in 5/5 tasks and in 26/26 C/C2 runs vs every A mean; n = 3 per cell, low A variance (sd < 200) |
| Block-Wise reduces output tokens | **Unsupported** | UNMEASURED; the generated-characters proxy rose by 9–26% |
| Block-Wise reduces USD per completed task | **Unsupported** | Billing UNMEASURED; derived input cost up 51–59% |
| Block-Wise preserves correctness | **Confirmed** (at ceiling) | 56/56 runs passed every test, in all conditions; blueprints pass 100% unedited |
| Structural checking prevents costly repair cycles | **Unsupported (contradicted)** | Below |
| Agents can use templates without reading generated code | **Confirmed** (in letter only) | 0 `show` calls; but agents re-derived behavior by testing and patching |
| A structured plan (plan.json) lowers cost | **Unsupported (contradicted)** | B costs more than A in 5/5 tasks |
| Discovery is the main overhead | **Unsupported** | Discovery (C − C2) is 39k–99k tokens; the remaining overhead persists in C2 |

Evidence on structural checking:
- C runs averaged 1.0–2.7 repair runs, against 0 for A.
- `blockwise check` fails on 19 of 23 final programs.
- 1 agent restructured its edit until the check passed, which hides the drift from the check.
- At least 5 agents ran `check` from the wrong directory, got "No plan yet", and reported success.

## 6. Answers to the product questions

1. **Does Block-Wise save meaningful money per completed application?** No.
   - The derived cost per successful task rose from $0.082 (A) to $0.130 (C) and $0.124 (C2).
   - Block-Wise was never cheaper than plain coding, in any of the 26 runs.
2. **Are the savings concentrated in whole-program blueprints or in smaller presets?** There are no
   savings in either.
   - Whole-program blueprints cost the most: +72% to +194% input tokens.
   - On the task with no blueprint (T5), C agents ran `find`, found nothing usable, applied no
     preset and wrote the code by hand. That cost +36%.
   - Smaller presets were never chosen, so they are not separately measured.
3. **Does loading structured JSON consume more tokens than it saves?** Yes.
   - Inline plan.json (B) cost +2.8% to +5.5% tokens with no correctness gain.
   - The CLI's compact JSON responses are small, so they are not the problem.
4. **Does MCP invocation add significant overhead?** It was not measured live: sub-agents here cannot
   attach an MCP server.
   - **Static estimate:** the tool definitions (about 2.4k characters, roughly 600 tokens) would be
     re-sent on each request, about 2–5k tokens per task, and responses are pretty-printed.
   - **That is small next to the dominant cost**, the extra agent turns. MCP would not remove those,
     and could add one per tool call.
   - **Status:** UNMEASURED.
5. **Does structural checking prevent costly repair cycles?** No. Agents edited working generated
   code anyway. The check then reported drift that agents ignored, worked around, or never saw
   because they ran it from the wrong directory.
6. **Can specialized agents use Block-Wise without reading generated code?** Mechanically, yes: there
   were zero `show` calls. In practice, not reading the code made the agents verify it by
   behavioral testing, which cost more turns than writing it.
7. **Where does template discovery become more expensive than direct coding?** In this setup, it
   always is.
   - Discovery alone (C − C2) costs 39k–99k tokens, about 1–2 extra requests.
   - Even with discovery removed (C2) and no edits, the runs cost +36% or more.
   - For programs of about 100 lines, writing the code costs roughly 1k output tokens (about $0.01),
     which is less than one extra agent turn (about 50–60k context tokens).
   - **Break-even:** none. The per-use saving is negative, so no number of reuses repays the
     discovery cost.
8. **What is the smallest profitable product built around the proven capability?** The capability
   that held up is deterministic generation of correct, tested code: every blueprint passed every
   hidden test unedited. The cost-saving claim did not hold.
   - The smallest product that does not depend on that claim is a **developer CLI for humans**:
     `blockwise apply` as a scaffolding tool, with blueprint packs and the Studio lessons as the paid
     layer.
   - **No product should be marketed as reducing LLM spend** on the basis of this evidence.

## 7. Limitations

- **One model and one agent harness.** The Claude Code sub-agent has about 50k tokens of fixed
  context per request, which makes extra turns expensive. In a lean custom agent with a small system
  prompt, a turn would cost less and the gap would shrink. It would still not reverse unless the
  template removes turns.
- **Small programs.** The programs are 60–150 lines. For programs of thousands of lines, output tokens
  could dominate and the result could differ. That is untested.
- **The specs favor Block-Wise.** The T1–T4 specs were derived from blueprint behavior. Block-Wise
  still lost.
- **No measure of the cost of failure.** Correctness was at ceiling, so the benchmark cannot show
  whether templates reduce costly failures.
- **Not measured or controlled:**
  - output tokens and USD billing are UNMEASURED;
  - temperature and sampling settings are not controllable;
  - wall-clock includes queueing from concurrent runs.
- **Missing run.** T4/C2 has n = 2, because one run was not executed under the spending cap.

## 8. Reproduction

```bash
python reproduce.py validate                        # harness check, no model calls
python reproduce.py prepare <ws_root> <plain_python> <bw_python>
# launch one fresh agent per schedule entry with the LAUNCHER line, then for each:
python reproduce.py finalize <run_id> <transcript.jsonl> <tokens> <tool_uses> <duration_ms>
python reproduce.py aggregate                       # results.csv, results.json
BW_BIN=blockwise python harness/analyze.py          # analysis.json: derived cost, per-cell stats, drift
```

The acceptance tests are in `acceptance/`. They were withheld from agents until every run had been
collected, and their hashes match `FREEZE.json`.
