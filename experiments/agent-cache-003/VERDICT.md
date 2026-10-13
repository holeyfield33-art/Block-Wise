# Verdict, Experiment 003: a lightweight knowledge layer, yes. A cost saver, not yet.

**Recommendation.** Block-Wise should become a **lightweight, versioned, hash-pinned knowledge layer
for coding agents**, in the form tested as condition C: a small stable manifest, plus a local library
the agent calls by id. It should not become another coding agent. It should not ship its library as a
large cached prompt (B) or as per-item retrieval (D).

**The honest value is determinism, speed and auditability.** Cost is at parity with conventional
coding, a few percent lower. That is not yet a selling point.

## The six questions

**1. Can Block-Wise achieve actual provider cache hits?**
Yes, within a session. No, across sessions, in this harness.
- **Within a session:** the provider reports cache reads on every request, and 63–74% of all input
  in every session was cache reads, including the manifest after its first use.
- **Across sessions:** 0 hits in 8 of 8 sessions, and in 0 of 63 runs from Experiments 001 and 002.
  - Our content comes after the harness's per-session context and the agent's first turn.
  - Even the harness prefix missed in all 8 sessions, because the tool list changed between
    sessions.
- **What cross-agent caching needs:** direct API control of cache breakpoints, with the manifest
  placed first and byte-stable. That was not testable here: there is no API key in this environment.

**2. Does caching lower the total cost per successful task?**
Yes, by about half, but **equally for every condition**.
- A falls from $0.0845 to $0.0441; C falls from $0.0837 to $0.0422.
- Caching does not favor Block-Wise. It discounts the harness context that every condition re-reads.

**3. Is loading a manifest cheaper than retrieving tools one at a time?**
Yes. C cost $0.0422 per task and D cost $0.0457.
- **Why:** D's `get` step costs a whole extra request, about 60k tokens of context re-read. That is
  far more than the roughly 2.5k characters of prompt a smaller index saves.
- **At this scale,** a 3k-character manifest loaded once beats lookups.

**4. Can agents reuse the same blueprint context across multiple tasks?**
Yes, within a session.
- C's agents applied all four blueprints in a single tool call, after reading the manifest once.
- The same per-session structure that lets A write four programs in one turn lets C apply four
  blueprints in one call. Both cost about $0.04 per task, against about $0.08 per task as single-task
  runs in Experiments 001 and 002.
- **Limit:** batching tasks into one session amortizes the fixed context for *any* agent. It is not
  a Block-Wise-specific gain.

**5. Does a local library outperform a large cached prompt?**
Yes.
- **Cost:** C cost $0.0422 per task and B $0.0514 (+22%).
- **Task-specific input:** C used 17.2k and B 43.0k.
- **Time:** C took 12 s and B 40 s.
- **Correctness:** both were 8/8, and B's agents did copy the source byte-for-byte.
- **Why B costs more:** it pays to carry the source on every request and to re-emit it as output.

**6. What happens when the blueprint version changes?**
The pin catches it. The simulation ran on a temporary copy of the package, not the repository.
- `bwcache verify` flags the changed blueprint.
- `bwcache apply` refuses it with exit 3 and "changed since it was approved; not trusted", and writes
  nothing.
- Unchanged blueprints still apply.
- **Re-pinning:** it creates manifest v2, a new prefix. Its first use pays a cache write of about
  3k characters, which is negligible (under $0.002). In this harness nothing was cached across
  sessions anyway.

## Cost against conventional coding (A)

| Per successful task | A | C | Difference |
|---|---|---|---|
| Derived input USD, with cache discounts | $0.0441 | $0.0422 | **−4.2%** (paired: −2.4%, −5.9%) |
| Derived input USD, without cache discounts | $0.0845 | $0.0837 | −1.0% |
| Task-specific input tokens | 4.7k | 4.3k | −9% |
| Output (generated characters, proxy) | 2.4k | 0.35k | −86% (UNMEASURED in tokens; about $0.005 per task at list price) |
| Wall-clock | 10.1 s | 3.1 s | −70% |
| Hidden-test success | 8/8 | 8/8 | equal |

The input difference is **small and inside the noise**: the harness context per request varied by
about 1.2k tokens between sessions. With n = 2 sessions per condition, a 2–6% cost difference is not
established.

**What is established:**
- **Faster:** −70% wall-clock.
- **Less output:** −86% generated characters.
- **Deterministic and auditable:** 8/8 programs are byte-identical to the approved hashes.

## Limitations

- **Small sample.** There are n = 2 sessions per condition, and all of them were cold-cache, so
  there is no warm-cache sample.
- **Harness limits.** The sub-agent harness controls cache placement. There is no direct API test.
- **Specs favor the blueprints.** The task specs were derived from the blueprints, and the hidden
  tests don't cover spec gaps that agents spotted (`done abc`, `nan`, JSON of the wrong type). Trust
  in a blueprint is only as good as its approval tests.
- **Small programs.** They are 60–150 lines, and a strong model writes all four in one turn.
- **Output tokens are UNMEASURED.**

## What to build next (not built here)

1. **Ship C as the default agent integration:**
   - a versioned `STABLE_PREFIX` manifest;
   - `bwcache`-style hash-pinned `apply`;
   - compact JSON responses;
   - one batch command that applies several ids at once.
2. **Fix the engine cap.** Seven blueprints in one project overflow the plan's 256-element limit.
3. **Harden blueprints and their approval tests** against the gaps agents found, so "trusted" means
   robust and not merely spec-passing.
4. **Test where Block-Wise could clearly win:**
   - larger, multi-file apps that conventional coding cannot finish in 3 requests;
   - a direct-API run with the manifest as a cached system block shared across agents.

   Each needs its own spending approval.

## Artifacts (`experiments/agent-cache-003/`)

| File | Contents |
|---|---|
| `PROTOCOL.md` | the protocol |
| `FREEZE.json` | hashes taken before any model call |
| `manifest/` | `PINS_v1.json`, `STABLE_PREFIX_v1.md`, `INDEX_v1.md` and `LIBRARY_SOURCE_v1.md` |
| `bwcache.py` | the hash-pinned retrieval and apply tool |
| `run003.py` | build, local validation, version-change test, cache evidence, prepare, finalize, compare |
| `CACHE_RESULTS.json` | local results plus all pilot measurements, per request |
| `COMPARISON.md` | the comparison |
| `runs/<cond>-<round>/` | usage records (per-request provider usage and tool calls; the raw transcript was sanitized before publishing with `../sanitize_transcripts.py`), usage, grades, prompt and agent report |

Experiments 001 and 002 are unmodified, and nothing has been pushed.
