# Comparison: C3 (trusted blueprint) vs A and C2

**Data sources.**
- **A and C2** are **historical controls** from Experiment 001 (main phase, T1–T4). They were not run
  again here.
- **C3** is 4 fresh runs, one per blueprint.
- **Zero-LLM** is a deterministic reference with no model involved.

**Measurement status.**
- Input tokens are **measured**.
- Output tokens are **UNMEASURED**: only a lower bound is available.
- USD is **derived** from list prices (Sonnet 5.5: $2.00/M uncached, $2.50/M cache write, $0.20/M
  cache read). It is not billing data.

## Summary (T1–T4, matched tasks)

| | A, historical | C2, historical | **C3** | Zero-LLM |
|---|---|---|---|---|
| Runs | 12 | 11 | **4** | 4 |
| Functional success | 12/12 | 11/11 | **4/4** | 4/4 |
| Model requests per task | 3.0 | 6.2 | **3.0** | 0 |
| Tool calls per task | 3.0 | 6.4 | **3.0** (Read, Bash, handback) | 0 |
| Mean input tokens | 163,344 | 350,530 | **159,463** | 0 |
| Repeated context (total minus 1st request) | 112,686 | 299,871 | **110,016** | 0 |
| Generated characters (output proxy) | 3,148 | 3,418 | **797** | 0 |
| Output tokens | UNMEASURED | UNMEASURED | UNMEASURED | 0 |
| Derived input USD per successful task, as measured | $0.0816 | $0.1238 | **$0.1190** | $0 |
| Same, with matched cache conditions (see confound 1) | $0.0816 | $0.1238 | **$0.0792** | $0 |
| Wall-clock per task (s) | 18.0 | 26.9 | **10.2** | 0.08 (local CPU) |
| Program identical to the approved blueprint output | n/a | 2/11 (9 edited) | **4/4** | 4/4 |

## Per task

Derived USD is shown as measured. Cache state is the state of the first request (see confound 1).

| Task | A input | C2 input | C3 input | C3 vs A | C3 vs C2 | C3 derived $ | A derived $ | C3 cache state |
|---|---|---|---|---|---|---|---|---|
| T1 csv_report | 163,782 | 280,848 | 159,629 | −2.5% | −43.2% | 0.0794 | 0.0825 | warm |
| T2 todo_cli | 163,024 | 359,841 | 159,233 | −2.3% | −55.7% | 0.1584 | 0.0810 | **cold** |
| T3 kv_store | 162,907 | 359,673 | 159,223 | −2.3% | −55.7% | 0.1584 | 0.0807 | **cold** |
| T4 log_stats | 163,663 | 427,370 | 159,765 | −2.4% | −62.6% | 0.0797 | 0.0821 | warm |

Every C3 agent obeyed the trust rules:
- exactly one `apply`;
- 0 `show`, 0 `check`, 0 self-test runs;
- 0 reads outside the workspace;
- no edits: the final program hash equals the approved generated-program hash in all 4 runs.

The hidden tests ran once per run: 9/9, 18/18, 19/19 and 9/9.

## Confounds (controlled where possible, stated where not)

1. **Prompt-cache state.**
   - In Experiment 001, all 56 runs read 35,824 tokens of the fixed agent context from cache on
     their first request.
   - In this experiment, the first two runs (t01, t02) started with a cold cache. Their first
     request was written to cache in full: 49,447 tokens at the cache-write price.
   - t03 and t04 ran within the cache window and got the normal warm split (34,601 tokens read).
   - This doubles t01 and t02's derived cost ($0.158 instead of $0.079) for reasons unrelated to the
     condition.
   - The "matched cache" row in the summary prices all four C3 runs at the warm split that t03 and
     t04 actually received. Raw figures are kept in `TRUSTED_RESULTS.json`.
2. **The harness overhead changed between experiments.**
   - The first-request context is 49,445–49,449 tokens now, against 50,658–50,669 in Experiment 001.
     That is about 1.2k fewer tokens on every request, likely because the tools attached to the
     session changed.
   - Over 3 requests, that is about 3.6k tokens. **This accounts for nearly all of C3's −3.9k
     difference from A.**
   - Adjusted for it, C3 is about 163.1k against A's 163.3k: **effectively equal**.
3. **The prompts are different.** The C3 wrapper drops the scratch/self-check instructions and has a
   tool budget of 5 instead of 30, and its prompt is about 3.5–3.9k characters against A's. The
   trust rules themselves are the treatment, so this is intended, but it is not a pure
   one-variable change.
4. **The controls are historical.** A and C2 ran on an earlier date. They were not interleaved or
   randomized with C3.
5. **n = 1 per task for C3.**

## Answers

1. **How many agent rounds did trusting the blueprint eliminate?**
   - Against C2, it eliminated **3.2 requests per task** (6.2 → 3.0) and 3.4 tool calls.
   - Against A, it eliminated none: both take 3 requests (read the task, act, report).
2. **How many input tokens did skipping code inspection avoid?**
   - Against C2, **191k per task (−54.5%)**, almost all of it repeated context: 299.9k → 110.0k.
   - Against A, about 3.9k (−2.4%), which matches the harness-overhead shift (confound 2).
3. **What did C3 cost compared with A and C2?**
   - **Per successful task, with matched cache:** $0.0792, against $0.0816 for A (−3.0%) and $0.1238
     for C2 (−36%).
   - **As measured, including the cold-cache runs:** $0.1190.
   - Output cost is UNMEASURED. The generated-characters proxy is 75% lower than A (797 vs 3,148),
     which suggests a small further output saving: roughly 600 tokens, about $0.006 per task at
     list price. This is a proxy estimate, not a measurement.
4. **Did C3 keep the same functional correctness?** Yes: 4/4 passed every hidden test, the same as A
   and C2. The four approved blueprints are byte-identical to the zero-LLM output, which also passes
   4/4.
5. **What part of the earlier cost increase came from verification and editing?**
   - C2 was 187k tokens above A per task; C3 is 3.9k below.
   - Removing verification, editing and their extra turns eliminated **essentially all (about
     100%)** of C2's excess.
   - This is not attributable to verification alone. C3 also changed the wrapper, the tool budget
     and the number of tool calls (confounds 2–3).
6. **Can a blueprint be applied in one model interaction?** The application itself took one tool call
   (`apply`). The agent still needed **3 model requests**: one to read the task file, one to run
   `apply`, and one to report. The harness's launcher points to a file, so 2 requests would be the
   floor even with inline instructions. That was not tested.
7. **Does repeated context still dominate the cost?** Yes.
   - Of C3's 159k input tokens, about 148k (93%) is the same harness context re-read on each of the
     3 requests.
   - The task-specific growth is only about 5.7k.
8. **Does trust-based execution become cheaper than conventional coding?**
   - **It reaches parity, not a demonstrated saving.**
   - Under matched conditions the difference is −0.2% to −2.5% in input, plus an unmeasured, likely
     small output saving.
   - That is within the size of the confounds.
   - The structural reason is that A also needs only 3 requests for programs of this size. C3 can
     only save the code-writing output, which is about 1k tokens.

## Reproduction

```bash
cd experiments/trusted-blueprint-002
export BW_BIN=<path>/blockwise
python run002.py manifest && python run002.py zero_llm
python run002.py prepare <ws_root> <python_with_blockwise>
# launch one fresh agent per schedule entry (Experiment 001's LAUNCHER line, model alias sonnet), then:
python run002.py finalize <run_id> <transcript.jsonl> <tokens> <tool_uses> <duration_ms>
python run002.py compare
```

Model usage records are in `runs/pilot/<task>/C3-1/usage_records.jsonl`: per-request provider usage and tool calls. The raw sub-agent transcripts held the harness's own account and session context, so `../sanitize_transcripts.py` replaced them before publishing.
Each run directory also has `usage.json` (per-request token splits), `grade.json`, `prompt.md` and
`agent_report.md`.
