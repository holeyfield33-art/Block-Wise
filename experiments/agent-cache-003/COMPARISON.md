# Comparison: Experiment 003 pilot

**Design.** 8 fresh sessions. Each session is one agent with all four tasks (T1–T4).
- **Pairing:** two rounds, alternating order (round 1: A, B, C, D; round 2: D, C, B, A), run one at a time.
- **Same for every session:** model alias, harness, specs and hidden acceptance tests.

**Measurement status.**
- Input, cache-write and cache-read tokens are **provider-reported**.
- Output tokens are **UNMEASURED**: only a lower bound is available.
- USD is **derived** from Sonnet 5.5 list prices, including cache discounts: $2/M uncached, $2.50/M
  5-minute cache write, $0.20/M cache read. It is not billing data.

## Results by condition (2 sessions each = 8 tasks each)

| | A Conventional | B Large cached prompt | **C Stable manifest + local library** | D On-demand retrieval |
|---|---|---|---|---|
| Tasks passed (hidden tests) | 8/8 | 8/8 | **8/8** | 8/8 |
| Programs matching the approved hash | 0/8 (self-written) | 8/8 (copied byte-for-byte) | 8/8 | 8/8 |
| Requests per session | 3, 3 | 4, 3 | **3, 3** | 4, 4 |
| Tool calls per session | 3, 3 | 7, 3 | 3, 3 | 4, 4 |
| Mean input tokens per session | 168,997 | 220,312 | **167,330** | 227,552 |
| Task-specific input (total minus harness context re-read on each request) | 18,898 | 43,030 | **17,208** | 24,944 |
| Share of input served from cache | 63.3% | 67.4% | 64.8% | 73.8% |
| **Derived input USD per successful task** | $0.0441 | $0.0514 (+16%) | **$0.0422 (−4.2%)** | $0.0457 (+3.7%) |
| Same, without the cache discount | $0.0845 | $0.1102 | $0.0837 | $0.1138 |
| Generated characters per session (output proxy) | 9,788 | 11,317 | **1,392** | 1,811 |
| Wall-clock per session | 40.4 s | 39.5 s | **12.2 s** | 16.2 s |

## Per session

| Session | Cond | Round, order | Requests | Input | Cache read | Cache write | Derived $ | Request-1 context | Cache |
|---|---|---|---|---|---|---|---|---|---|
| s01 | A | 1, 1st | 3 | 167,388 | 105,872 | 61,510 | 0.1750 | 49,446 | cold |
| s02 | B | 1, 2nd | 4 | 255,296 | 184,936 | 70,352 | 0.2129 | 50,652 | cold |
| s03 | C | 1, 3rd | 3 | 169,138 | 109,634 | 59,498 | 0.1707 | 50,652 | cold |
| s04 | D | 1, 4th | 4 | 227,566 | 167,862 | 59,696 | 0.1828 | 50,652 | cold |
| s05 | D | 2, 1st | 4 | 227,539 | 167,860 | 59,671 | 0.1828 | 50,652 | cold |
| s06 | C | 2, 2nd | 3 | 165,522 | 107,188 | 58,328 | 0.1673 | 49,429 | cold |
| s07 | B | 2, 3rd | 3 | 185,328 | 115,395 | 69,927 | 0.1979 | 50,652 | cold |
| s08 | A | 2, 4th | 3 | 170,606 | 108,180 | 62,420 | 0.1777 | 50,620 | cold |

**Paired comparison, C against A:**
- **Round 1:** +1.0% tokens and −2.4% derived $.
- **Round 2:** −3.0% tokens and −5.9% derived $.
- **Task-specific input:** C is lower in both pairs, 17.2k against 18.9k (−9%).

## Cold and warm cache

**All 8 sessions were cold on request 1**, so there is no warm-cache sample to report separately.
- **Why:** the harness's own context (49,429–50,652 tokens) changed between sessions as MCP tool lists
  connected and disconnected. That broke even the shared harness prefix.
- **What was cached:** every cache read in this pilot happened *within* a session. Each request re-read
  the previous request's prefix, including the Block-Wise manifest, the library source or the index.
- **What cannot be cached across sessions:** our content comes after the harness's per-session
  context and the agent's first turn, so in this harness it can never be cached across sessions.
  Experiments 001 and 002 show the same: 0 of 63 multi-request runs read task content from another
  run.

## Observations

- **A strong model writes four small programs in one turn.** A used 3 requests for all 4 tasks.
  Block-Wise therefore has no rounds to remove. Its only savings are the code the model doesn't write
  (about 8.4k fewer generated characters per session) and time.
- **B (paste the source) works but costs the most.** The agent copied 15k characters of source
  byte-for-byte: 8/8 programs matched the approved hash. But it paid to carry and re-emit the source,
  and in one session it took an extra request.
- **D (fetch per item) costs one extra round.** `bwcache get` adds a request (about 60k tokens of
  re-read context). That cancels the roughly 2.5k characters of prompt that the smaller index saves.
- **C (manifest + local library) is the cheapest Block-Wise mode.** The agent applied all four
  blueprints in one tool call.
- **Spec gaps the hidden tests don't cover.** Agents in B noticed that the approved blueprints do not
  handle some inputs the specs arguably cover: `done abc`, a bare `done`, `nan`/`inf` amounts, and
  JSON of the wrong type. The hidden tests don't exercise these cases, so trusted blueprints pass.
  Trust is only as good as the approval tests.

## Spending

| Item | Value |
|---|---|
| Approved cap | 4.0M input tokens |
| Used | **1,568,383** |
| Derived input cost | $1.47 with cache discounts; $3.14 without |
| Sessions run | 8/8, with no failures and no reruns |
