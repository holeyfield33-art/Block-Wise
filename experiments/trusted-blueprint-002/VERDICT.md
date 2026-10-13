# Verdict, Experiment 002: **PARTIAL**

## Result

When the agent trusts an approved blueprint, essentially **all** of Block-Wise's earlier overhead
disappears:
- requests fall from 6.2 to 3.0 per task;
- input tokens fall from 350k to 159k (−54.5% against C2);
- correctness stays at 100%;
- the generated program is byte-identical to the approved version in 4/4 runs.

The result **matches** conventional coding (A). It does not **beat** it convincingly.

| Per successful task (T1–T4) | A, historical | C2, historical | C3 |
|---|---|---|---|
| Success | 12/12 | 11/11 | 4/4 |
| Requests | 3.0 | 6.2 | 3.0 |
| Input tokens | 163,344 | 350,530 | 159,463 (−2.4% vs A) |
| Derived input USD, matched cache | $0.0816 | $0.1238 | **$0.0792** (−3.0% vs A) |
| Derived input USD, as measured | $0.0816 | $0.1238 | $0.1190 (2 of 4 runs started with a cold cache) |
| Output | UNMEASURED | UNMEASURED | UNMEASURED; the proxy is −75% vs A |
| Wall-clock | 18.0 s | 26.9 s | 10.2 s |

Zero-LLM reference: `blockwise apply` alone passes 4/4, with 0 model tokens and about 0.08 s of
local CPU per program.

## Why the verdict is PARTIAL and not GO

- **The input-token gap is explained by the harness, not the condition.** C3's 3.9k input-token
  advantage over A is about the size of the 1.2k-per-request drop in fixed harness context between
  experiments (3.6k over 3 requests). Adjusted for that, the input is equal.
- **The dollar result depends on prompt-cache state.** The 3% matched-cache saving goes the other
  way (+46%) when the first request misses the cache. As measured, C3 was not cheaper.
- **Too little data.** There are n = 4 C3 runs (one per task) against historical controls. That is
  too few to call a 2–3% difference real.
- **The likely real saving is small.** It is output tokens: A writes about 3.1k characters of code
  and C3 about 0.8k. That is roughly 600 tokens, about $0.006 per task at list price. Output is
  UNMEASURED, so this cannot be confirmed from billing data.

## What this changes from Experiment 001

Experiment 001's +51–59% cost came from agents verifying and editing generated code. Experiment 002
removes it entirely.

**Block-Wise is no longer more expensive when it is used as a trusted tool.** Today it is
cost-neutral, it is faster in wall-clock (−43%), and it is deterministic: the code is byte-identical
every time.

Correctness rests on trusting the approved blueprints. Here the specs were derived from those
blueprints, so in this setup a blueprint that fits is guaranteed to fit.

## Recommendation

A **narrow expanded study** is justified. Broad commercialization claims are not.

The study would run **fresh, interleaved A and C3 runs**:
- the same day, alternating, with the cache warmed identically for both;
- 3 trials × 4 tasks × 2 conditions = 24 runs;
- about **3.9M input tokens**.

It would settle whether the 2–3% difference and the output saving are real.

Separately, the only setting where trust-based execution could become clearly cheaper is one where
conventional coding needs **more than 3 requests**: larger programs, multi-file apps, or tasks where
A has to iterate. Testing that needs bigger blueprints. Those are out of scope here: no new
templates were allowed.

**Product implication:** "trusted blueprints" is a viable mode for agents. Its honest pitch is
**same cost, faster and deterministic**, not "saves money". Any savings claim should wait for the
expanded study.

## Spending

| Item | Value |
|---|---|
| Experiment 002 cap (approved) | 1.0M input tokens |
| Used | **637,850** input tokens (4 runs: 159,223 / 159,233 / 159,629 / 159,765) |
| Derived input cost | $0.476 as measured; $0.317 at matched cache |
| Not run | none |
| Failures | none; 4/4 passed the single hidden-test grading |

## Artifacts (`experiments/trusted-blueprint-002/`)

| File | Contents |
|---|---|
| `PROTOCOL.md` | the protocol |
| `FREEZE.json` | hashes taken before any model call |
| `MANIFEST.json` | approved blueprint ids, blueprint and program sha256 values, generator commit |
| `ZERO_LLM.json` | the deterministic reference |
| `TRUSTED_RESULTS.json` | all measurements, raw and matched-cache, plus the historical controls |
| `COMPARISON.md` | full tables, confounds and the 8 answers |
| `runs/pilot/<task>/C3-1/` | usage records (per-request provider usage and tool calls; the raw transcript was sanitized before publishing with `../sanitize_transcripts.py`), usage, grade, prompt and agent report |
| `run002.py` | reproduction script; imports Experiment 001's harness read-only |

Experiment 001 files are unmodified, and their hashes still match their `FREEZE.json`.
