# Pilot results (approval gate)

These are 7 runs under the frozen protocol (`PROTOCOL.md`). They count as **pilot evidence only**:
1 trial per cell and 2 of the 5 tasks. Every number below is measured unless it is labeled
*derived* or *UNMEASURED*.

## Validity checks

| Check | Result |
|---|---|
| Served model | `claude-sonnet-5-5` in all 7 runs (requested and served match) |
| Isolation (tool calls touching paths outside the workspace) | 0 in all 7 runs |
| Harness validation before any model call | the 4 blueprint programs passed 100%; the program built from the T5 plan passed 37/37; a do-nothing program passed 0/9 |
| Fixed agent-harness overhead (input to the first request) | 50,656 tokens in every run, identical across conditions |

## Per run

| Task | Cond | Tests | Requests | Input tokens (total) | Cache read | Task-specific context growth | Derived input cost* | Output tokens | Generated chars | Wall-clock (s) |
|---|---|---|---|---|---|---|---|---|---|---|
| T1 csv_report | A | 9/9 | 3 | 163,589 | 106,325 | 6,604 | $0.164 | UNMEASURED | 3,533 | 19.9 |
| T1 csv_report | B | 9/9 | 3 | 168,318 | 108,895 | 8,763 | $0.170 | UNMEASURED | 2,715 | 16.1 |
| T1 csv_report | C | 9/9 | 6 | 341,136 | 281,382 | 9,088 | $0.206 | UNMEASURED | 3,631 | 28.6 |
| T1 csv_report | C2 | 9/9 | 6 | 341,223 | 281,545 | 9,012 | $0.206 | UNMEASURED | 3,827 | 28.4 |
| T5 inventory | A | 37/37 | 3 | 164,405 | 106,534 | 7,211 | $0.166 | UNMEASURED | 4,068 | 18.3 |
| T5 inventory | B | 37/37 | 3 | 173,600 | 111,003 | 11,937 | $0.179 | UNMEASURED | 4,359 | 18.1 |
| T5 inventory | C | 37/37 | 4 | 224,001 | 164,701 | 8,638 | $0.181 | UNMEASURED | 4,138 | 23.1 |

\*Derived input cost = measured uncached × $2.00, cache-write × $2.50 and cache-read × $0.20 per
million tokens (Sonnet 5.5 list prices). It is not billing data. Output cost is UNMEASURED: the
transcript logs output tokens mid-stream, so only a lower bound is available.

Input-token change against A (calculated, n = 1 per cell):

| | T1 | T5 |
|---|---|---|
| B | +2.9% tokens, +3.6% derived input $ | +5.6% tokens, +7.7% derived input $ |
| C | **+108.5% tokens, +25.1% derived input $** | +36.2% tokens, +9.2% derived input $ |
| C2 (template already known) | +108.6% tokens, +25.0% derived input $ | n/a |

## What happened, observed in the transcripts

1. **No condition beat plain coding on tokens.** The A runs finished in 3 requests. Block-Wise runs
   on the blueprint task took 6.
2. **The blueprint worked, and the agents still verified and edited it.** Both C and C2 applied
   `csv_report`, which already passed every acceptance test. Both then spent extra rounds testing,
   and both made unrequested "hardening" edits (BOM handling, `nan`/`inf`, broader exceptions). In
   the T5 run, C ran `find`, found nothing that fit, and wrote the code by hand. That cost one extra
   request and still beat C on T1.
3. **Discovery was not the cost driver.** C2, which was told the template up front, cost the same as
   C (341k vs 341k tokens). The overhead comes from verifying generated code the agent has not read,
   not from searching for it.
4. **Code-writing tokens are small next to request overhead.** Every request re-reads about 50.6k
   tokens of fixed context. One extra request costs more input than the roughly 400 output tokens a
   blueprint saves by not writing `report.py`. Generated characters did not fall either: 3,533 for A
   against 3,631 for C, because the agents still wrote test scripts.
5. **The structure check did not protect the generated code.**
   - Both C agents' edits make `blockwise check` fail now (`body_changed` on `parse_amount` and
     `main`), as re-run by the evaluator.
   - One agent reported "check reported no issues after my edits".
   - The other saw "No plan yet" because it ran `check` from a different directory.
   - Neither noticed the drift.
6. **The plan.json (B) cost a little more than plain English and helped nothing measurable.** It
   added 2.2k–4.7k tokens of context, and correctness was already at ceiling.

## Audit findings (Phase 1), repository at commit `589ca99`

- 217 tests pass and 1 is skipped (it needs Python 3.15). Ruff is clean. Every documented CLI
  command, all six MCP tools and the exit codes work as documented.
- **`benchmarks/token_cost.py` measures no model.** It counts the characters or tokens of generated
  code against a CLI call string and assumes output tokens cost 5×. The README and docs label this
  "Measured, not assumed".
  - Without `tiktoken` it silently falls back to 4 characters per token, and its output does not
    say which mode it used.
  - It omits per-request overhead.
  - It omits the `show_preset` step that `docs/agent-instructions.md` tells agents to run, which
    loads the generated code into context.
  - It omits the verification an agent does after applying a template.
- The MCP tools return pretty-printed JSON, which is larger than the CLI's compact output.
- The 640-token figure for the MCP tool definitions is an estimate (2,412 characters measured).
  MCP overhead could not be measured live, because sub-agents here cannot attach an MCP server.

## Status of claims after the pilot

| Claim | Status |
|---|---|
| Block-Wise reduces end-to-end input tokens per completed task | **Unsupported**: contradicted in 2 of 2 tasks (n = 1) |
| Block-Wise reduces output tokens | **Unsupported**: UNMEASURED, and the generated-characters proxy shows no reduction |
| Block-Wise preserves correctness | **Promising**: 100% in all runs, but every condition is at ceiling |
| Structural checking prevents costly repair | **Unsupported**: agents made unchecked edits; drift went unnoticed |
| USD savings | **Unsupported**: no billing data; derived input cost is higher for C |

## Full-run estimate (for approval)

- **Runs:** 57 (45 for A/B/C × 5 tasks × 3 trials, plus 12 for C2 × 4 blueprint tasks × 3).
- **Input tokens:** about 230k per run at the pilot mean, so about **13M**, mostly cache reads.
- **Derived list-price cost:** about $0.18 of input per run, **about $10–11 in total**, plus output
  (UNMEASURED, likely under $2).

Sub-agent runs draw on the session's Claude plan usage rather than a separately billed API key.
