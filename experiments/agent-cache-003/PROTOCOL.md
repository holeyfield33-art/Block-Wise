# Protocol: Experiment 003, Block-Wise as a reusable agent knowledge and blueprint cache

This protocol was frozen before any model call (`FREEZE.json`).
- The Block-Wise engine is unchanged.
- Experiments 001 and 002 are used read-only. Their tests, specs, grader and transcript parser are
  imported, not copied or edited.

## Question

Should Block-Wise become a lightweight, reusable knowledge layer for coding agents? Specifically:
1. Is versioned, hash-pinned blueprint knowledge cheaper to deliver as a cached prompt prefix, as a
   compact manifest, or by on-demand retrieval?
2. Does any of these beat conventional coding?

## Phase 1: cache architecture (prototype; no database, vector store or server)

All files live in `manifest/`. `run003.py build` generates them from the installed library.

| Artifact | Size (chars) | Role |
|---|---|---|
| `PINS_v1.json` | n/a | Approved blueprints, each with a blueprint-file sha256, a generated-program sha256, its parameters and its purpose. Generator commit `b01d956`. |
| `STABLE_PREFIX_v1.md` | 3,047 | **Stable prompt prefix**: an immutable versioned manifest with ids, capabilities, defaults, hashes, trust rules and commands. It carries no source code. |
| `INDEX_v1.md` | 545 | **On-demand retrieval**: a tiny index of ids plus how to fetch one record. |
| `LIBRARY_SOURCE_v1.md` | 15,134 | **Large cached prompt**: the full approved source of all 7 blueprints, for comparison. |

`bwcache.py` is a thin wrapper over the unchanged CLI. Every command prints one compact JSON line
and never prints source code.
- `index`: lists the approved blueprints.
- `get <id>`: returns one approved record (485 characters for `kv_store`).
- `apply <id> --into app`:
  1. checks the installed blueprint's hash against the pin, and refuses a mismatch (exit 3);
  2. generates the program;
  3. checks the program's hash, and quarantines a mismatch;
  4. refuses to regenerate a program that already exists.
- `verify`: re-checks every pin against the installed library.

**Safety and validity rules (Phase 4):**
- Every manifest says it is reference material that does not override the agent's own safety rules
  or the operator's instructions.
- Only pinned blueprints can be applied without inspecting their source.
- The acceptance tests run outside the agent's conversation, once per program, after the session
  ends.

## Phase 2: verifying cache support (from existing logs; no new calls)

The provider (Claude API, through the sub-agent harness) reports `input_tokens`,
`cache_creation_input_tokens` and `cache_read_input_tokens` on every request. `run003.py
cache_evidence` reads them from the 67 transcripts of Experiments 001 and 002:
- **88.8%** of all input tokens were cache reads, 11.2% cache writes and under 0.01% uncached.
- **Within a session**, every request read the previous request's prefix (67 of 67 runs).
- **Across sessions**, only the harness's own context was reused: 35,824 tokens in Experiment 001 and
  34,601 in Experiment 002.
  - The first request of a run was a cache miss (0 tokens read) in 9 runs: the 7 pilot runs, plus
    the first 2 runs of Experiment 002, which started after a gap of more than 5 minutes.
  - In **0 of 63** multi-request runs did request 2 read anything beyond the run's own request 1. Task
    prompts with identical text in different runs were never shared.

**Why: the harness controls placement.** There is no direct API key in this environment, so cache
breakpoints are placed by the harness, not by us.
- Our content arrives after the harness's per-session context, and after the agent's first turn,
  which includes a unique tool-use id.
- Caching is an exact byte-prefix match, so nothing after that point can match another session.
- **Consequence:** in this harness, a Block-Wise prefix can be cached *within* one agent session,
  never across sessions. The pilot therefore uses **multi-task sessions** to measure reuse.

## Phase 3: controlled pilot

Each session is one fresh agent given **all four tasks** (T1–T4: the same specs and hidden tests as
Experiments 001 and 002) and four deliverables in `app/`.

| Cond | What follows the common wrapper header | Tooling | Checks |
|---|---|---|---|
| **A** Conventional | "No component library is provided." | plain Python, no Block-Wise | may self-check in scratch/ |
| **B** Large cached prompt | `LIBRARY_SOURCE_v1.md` (all approved source); the agent writes the files | plain Python, no Block-Wise | may self-check in scratch/ |
| **C** Stable manifest prefix | `STABLE_PREFIX_v1.md`; the agent applies by id | Python with Block-Wise, plus `bwcache` | trust rules; no checks |
| **D** On-demand retrieval | `INDEX_v1.md`; the agent fetches records with `bwcache get` | Python with Block-Wise, plus `bwcache` | trust rules; no checks |

**Prompt layout.** The stable content comes first: the condition's prefix, which is byte-identical
across rounds and contains no paths. The run-specific workspace, rules and the four specs follow.

**Common to all conditions:**
- the same wrapper;
- a budget of 30 tool calls;
- one attempt;
- the same model alias (`sonnet`), harness and one-line launcher.

**Order.** Two paired rounds in alternating order: round 1 is A, B, C, D and round 2 is D, C, B, A.
That gives 8 sessions (`s01`–`s08`).
- Sessions run **one at a time**, so each one's harness context is cache-warm from the previous one.
- Each session is classified as cold or warm from its own first-request `cache_read`, and cold and
  warm results are reported separately.

**Measured per session:**
- requests and tool calls;
- per-request uncached, cache-write and cache-read tokens;
- derived input USD **with** cache discounts and **without** (all input at the uncached price);
- an output lower bound (output tokens are **UNMEASURED**);
- wall-clock time;
- per-task acceptance results and whether each program matches its approved hash.

**Derived cost.** Sonnet 5.5 list prices: $2/M input, $2.50/M 5-minute cache write, $0.20/M cache
read, $10/M output. These are derived figures, not billing data.

## Local results already obtained (no model calls; `CACHE_RESULTS.json` → `local`)

- **Hidden tests.** `bwcache apply` for T1–T4 passes 9/9, 18/18, 19/19 and 9/9 when graded with the
  hidden tests.
- **Version change.** It was simulated on a temporary copy of the package (the repository was not
  touched):
  - `verify` flags `log_stats`;
  - `apply log_stats` is refused with "changed since it was approved; not trusted", and nothing is
    written;
  - unchanged blueprints still apply.

  Re-pinning produces manifest v2. Its first byte difference is at position 42, so a v2 prefix
  starts a new cache entry, and every cached token after that point must be written again.
- **Plan-size cap (an engine finding, not fixed).** Applying all 7 blueprints into one project fails
  on the 7th with `"Score exceeds 256 body elements"`. Four fit.

## Budget proposal (requires approval before any model call)

| Session | Expected requests | Expected input tokens |
|---|---|---|
| A (writes 4 programs and tests them) | 5–8 | 300k–470k |
| B (copies from about 5k tokens of source) | 5–7 | 310k–430k |
| C (manifest; 4 applies, possibly in one command) | 3–6 | 160k–320k |
| D (index, then gets and applies) | 4–10 | 210k–550k |
| **Per round** | | **about 1.0M–1.8M** |
| **Pilot, 2 rounds, 8 sessions** | | **about 2.0M–3.6M; expected about 2.4M** |

- **Derived cost:** about $1.5–2.5 of input at list price, plus output (UNMEASURED; likely under $0.10).
- **Proposed cap: 4.0M input tokens.** Sessions run sequentially, and none starts unless at least
  600k tokens remain.

## Decision questions (answered in VERDICT.md)

1. Can Block-Wise achieve actual provider cache hits?
2. Does caching lower the total cost per successful task?
3. Is loading a manifest cheaper than retrieving tools one at a time?
4. Can agents reuse the same blueprint context across multiple tasks?
5. Does a local library outperform a large cached prompt?
6. What happens when the blueprint version changes?

## Reproduction

```bash
cd experiments/agent-cache-003
python run003.py build && python run003.py local          # manifests + local validation, version change, cache evidence
python run003.py prepare <ws_root> <python_with_blockwise> <plain_python>
# one fresh agent per session (Experiment 001's LAUNCHER line, model alias sonnet), sequentially, then:
python run003.py finalize <run_id> <transcript.jsonl> <tokens> <tool_uses> <duration_ms>
python run003.py compare                                  # CACHE_RESULTS.json -> pilot
```
