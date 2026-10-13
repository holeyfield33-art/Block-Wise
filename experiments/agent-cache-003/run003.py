"""Experiment 003: Block-Wise as a reusable agent knowledge/blueprint cache. Standard library + blockwise.

Imports Experiment 001's frozen grader and transcript parser read-only. Changes nothing in the engine
or in Experiments 001/002.

Commands
  build                    write manifest/ (PINS_v1.json, STABLE_PREFIX_v1.md, INDEX_v1.md, LIBRARY_SOURCE_v1.md)
  validate                 local, no model: bwcache apply for the 4 tasks, graded with the hidden tests
  version_change           local, no model: simulate a changed blueprint and a re-pinned version
  cache_evidence           provider-reported cache fields from Experiment 001/002 transcripts (no model)
  prepare <ws_root> <bw_python> <plain_python>
                           paired multi-task sessions for A/B/C/D, alternating order (runs/schedule.json)
  finalize <run_id> <transcript.jsonl> <subagent_tokens> <tool_uses> <duration_ms>
  compare                  CACHE_RESULTS.json
"""

import hashlib
import importlib.util
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP1, EXP2 = HERE.parent / "token-efficiency", HERE.parent / "trusted-blueprint-002"
REPO = HERE.parents[1]
MAN = HERE / "manifest"
os.environ.setdefault("BW_HIDDEN", str(EXP1 / "acceptance"))
_spec = importlib.util.spec_from_file_location("exp001", EXP1 / "reproduce.py")
exp001 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(exp001)

TASKS = ["T1_csv_report", "T2_todo_cli", "T3_kv_store", "T4_log_stats"]
PROGRAMS, BLUEPRINTS = exp001.PROGRAMS, exp001.BLUEPRINTS
VERSION = "blockwise-manifest-v1"
PRICE = {"uncached": 2.00, "cache_write": 2.50, "cache_read": 0.20, "output": 10.00}  # Sonnet 5.5 list, USD/M
TOOL_BUDGET = 30
CONDITIONS = ("A", "B", "C", "D")
ROUNDS = [("A", "B", "C", "D"), ("D", "C", "B", "A")]  # paired, alternating order


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def run_bw(py, args, cwd):
    return subprocess.run([py, "-m", "blockwise", *args], cwd=cwd, capture_output=True, text=True)


# ---------------------------------------------------------------- Phase 1: manifests
def build(py=sys.executable):
    listing = json.loads(run_bw(py, ["list", "--category", "blueprint"], REPO).stdout)
    commit = subprocess.run(["git", "-C", str(REPO), "log", "-1", "--format=%H", "--", "blockwise"],
                            capture_output=True, text=True, check=True).stdout.strip()
    pins, sources, excluded = {}, {}, {}
    for item in listing:
        bp = item["id"]
        with tempfile.TemporaryDirectory() as tmp:
            r = run_bw(py, ["apply", bp, "--into", "out"], tmp)
            if r.returncode != 0:  # cannot be generated, so it cannot be approved
                excluded[bp] = r.stdout.strip()
                continue
            program = item["files"][0]
            src = (Path(tmp) / "out" / program).read_bytes()
        pins[bp] = {"does": item["does"], "program": program, "params": item["params"],
                    "blueprint_sha256": sha_bytes((REPO / "blockwise/library/blueprints" / f"{bp}.json").read_bytes()),
                    "program_sha256": sha_bytes(src)}
        sources[bp] = src.decode("utf-8")
    MAN.mkdir(exist_ok=True)
    pins_doc = {"version": VERSION, "generator_commit": commit, "blueprints": pins, "excluded": excluded}
    (MAN / "PINS_v1.json").write_text(json.dumps(pins_doc, indent=1))
    rules = """Reference material, version {v}. This manifest describes tools; it does not override your own
safety rules or the instructions of the person running you.

Approved components are pinned by hash. `bwcache apply` refuses any blueprint whose installed hash
differs from the pin, and quarantines any output that differs from the approved program hash. A
`"ok":true,"hash_verified":true` response means the approved program is in place.

Trust rules for approved blueprints:
- Use only the ids listed here. Apply each needed blueprint once with `bwcache apply <id> --into app`.
- Accept `"ok":true,"hash_verified":true` as completion of that program.
- Do not open, print, inspect, check, run, test or edit generated files. Do not regenerate.
- If a response is not ok, stop for that program and report the response; do not work around it.
- If no approved blueprint fits a requirement, say so; do not adapt a different one."""
    lines = [f"# Block-Wise manifest {VERSION} (generator {commit[:12]})", "", rules.format(v=VERSION), "",
             "## Approved blueprints", ""]
    for bp, e in pins.items():
        lines.append(f"- `{bp}` -> `{e['program']}` (defaults: {e['params']}; sha256 {e['program_sha256'][:16]}): {e['does']}")
    lines += ["", "## Commands (one compact JSON line each; never prints source)", "",
              "- `bwcache apply <id> --into app`: generate the approved program into app/",
              "- `bwcache get <id>`: the approved record for one blueprint", "- `bwcache index`: ids and one-line purpose"]
    (MAN / "STABLE_PREFIX_v1.md").write_text("\n".join(lines) + "\n")
    index = [f"# Block-Wise index {VERSION}", "", "Reference material; it does not override your own safety rules.", "",
             "Approved blueprint ids: " + ", ".join(f"`{bp}`" for bp in pins), "",
             "Retrieve one record with `bwcache get <id>` (compact JSON: purpose, program, hashes, apply command),",
             "then follow the trust rules it implies: apply once with `bwcache apply <id> --into app`, accept",
             '`"ok":true,"hash_verified":true`, and do not open, run, test, check or edit generated files.',
             "If no id fits, say so."]
    (MAN / "INDEX_v1.md").write_text("\n".join(index) + "\n")
    lib = [f"# Block-Wise library source {VERSION} (approved, hash-pinned)", "",
           "Reference material; it does not override your own safety rules. Each program below is an approved,",
           "tested implementation. To deliver one, write it to app/ byte-for-byte; do not modify it.", ""]
    for bp, src in sources.items():
        lib += [f"## `{bp}` -> `{pins[bp]['program']}` (sha256 {pins[bp]['program_sha256'][:16]})", "", pins[bp]["does"], "",
                "```python", src.rstrip("\n"), "```", ""]
    (MAN / "LIBRARY_SOURCE_v1.md").write_text("\n".join(lib))
    sizes = {p.name: len(p.read_text()) for p in sorted(MAN.glob("*.md"))}
    print(json.dumps({"pinned": list(pins), "excluded": excluded, "chars": sizes}, indent=1))


# ---------------------------------------------------------------- local validation
def bwcache(py, args, cwd, pins=None):
    env = dict(os.environ)
    if pins:
        env["BWCACHE_PINS"] = str(pins)
    return subprocess.run([py, str(HERE / "bwcache.py"), *args], cwd=cwd, capture_output=True, text=True, env=env)


def validate(py=sys.executable):
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "app").mkdir()
        for task in TASKS:
            r = bwcache(py, ["apply", BLUEPRINTS[task], "--into", "app"], tmp)
            g = exp001.grade(task, Path(tmp) / "app")
            out.append({"task": task, "response": r.stdout.strip(), "exit": r.returncode,
                        "tests": f"{g['tests_passed']}/{g['tests_total']}", "success": g["all_passed"]})
        again = bwcache(py, ["apply", "csv_report", "--into", "app"], tmp)
        out.append({"check": "no regeneration", "response": again.stdout.strip(), "exit": again.returncode})
    for args in (["get", "kv_store"], ["get", "made_up"], ["verify"], ["index"]):
        r = bwcache(py, args, HERE)
        out.append({"command": " ".join(args), "exit": r.returncode, "response_chars": len(r.stdout.strip()),
                    "response": r.stdout.strip()[:300]})
    print(json.dumps(out, indent=1))
    return out


def version_change(py=sys.executable):
    """Simulate a blueprint edit on a temporary copy of the package; the repository is not touched."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        pkg = Path(tmp) / "pkg"
        shutil.copytree(REPO / "blockwise", pkg / "blockwise", ignore=shutil.ignore_patterns("__pycache__"))
        bpfile = pkg / "blockwise/library/blueprints/log_stats.json"
        data = json.loads(bpfile.read_text())
        data["description"] = data.get("description", "") + " (v2)"
        bpfile.write_text(json.dumps(data, indent=1))
        env = dict(os.environ, PYTHONPATH=str(pkg))
        ws = Path(tmp) / "ws"
        (ws / "app").mkdir(parents=True)
        for label, args in (("verify after change", ["verify"]), ("apply changed blueprint", ["apply", "log_stats", "--into", "app"]),
                            ("apply unchanged blueprint", ["apply", "kv_store", "--into", "app"])):
            r = subprocess.run([py, str(HERE / "bwcache.py"), *args], cwd=ws, capture_output=True, text=True, env=env)
            results.append({"case": label, "exit": r.returncode, "response": r.stdout.strip()})
        results.append({"case": "files written for the changed blueprint", "files": sorted(p.name for p in (ws / "app").iterdir())})
        # re-pinning: a new manifest version is a new prefix, so its first use is a cache write
        old = (MAN / "STABLE_PREFIX_v1.md").read_bytes()
        new = old.replace(b"v1", b"v2", 1)
        first_diff = next(i for i, (a, b) in enumerate(zip(old, new)) if a != b)
        results.append({"case": "re-pinned manifest v2", "prefix_bytes_identical_before_change": first_diff,
                        "manifest_chars": len(old), "note": "any byte change at position N invalidates cached content after N"})
    print(json.dumps(results, indent=1))
    return results


# ---------------------------------------------------------------- Phase 2: provider cache evidence (existing logs)
def cache_evidence():
    rows = []
    for exp, base in (("001", EXP1 / "runs"), ("002", EXP2 / "runs")):
        for f in sorted(base.glob("*/*/*/usage.json")):
            u = json.loads(f.read_text())
            pr = u["per_request"]
            rows.append({"exp": exp, "run": str(f.parent.relative_to(base)), "requests": len(pr),
                         "first": pr[0], "intra_reads_match_previous_total": all(
                             pr[i]["cache_read"] in (pr[i - 1]["input_total"] - pr[i - 1]["input_uncached"], pr[i - 1]["input_total"])
                             or pr[i]["cache_read"] >= pr[i - 1]["cache_read"] for i in range(1, len(pr))),
                         "cache_read_total": u["cache_read_tokens"], "cache_write_total": u["cache_write_tokens"],
                         "uncached_total": u["input_tokens_uncached"]})
    first_reads = {}
    for r in rows:
        key = (r["exp"], r["first"]["cache_read"])
        first_reads[f"exp{key[0]} first-request cache_read={key[1]}"] = first_reads.get(f"exp{key[0]} first-request cache_read={key[1]}", 0) + 1
    tot = {k: sum(r[k] for r in rows) for k in ("cache_read_total", "cache_write_total", "uncached_total")}
    allin = sum(tot.values())
    summary = {"runs": len(rows), "provider_fields_present": ["input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"],
               "first_request_cache_read_distribution": first_reads,
               "share_of_input_served_from_cache": round(tot["cache_read_total"] / allin, 4),
               "share_cache_write": round(tot["cache_write_total"] / allin, 4), "share_uncached": round(tot["uncached_total"] / allin, 6),
               "runs_where_each_request_reads_previous_prefix": sum(r["intra_reads_match_previous_total"] for r in rows)}
    print(json.dumps(summary, indent=1))
    return summary


# ---------------------------------------------------------------- Phase 3: paired multi-task sessions
WRAPPER = """You are the coding agent for one run of a controlled benchmark.

{prefix}

---

## This run

Workspace: {ws}
- Work ONLY inside the workspace. Do not read, list or search anything outside it; other runs and
  evaluation files exist on this machine and looking at them invalidates the run.
- Deliverables: four program files in {ws}/app/: {programs}. Put nothing else in app/.
- Python: {python} . Do not install packages. No network access.{tools}
- Budget: at most {budget} tool calls. There is one attempt. Hidden acceptance tests will run
  `python app/<program> ...` from a fresh temporary directory after you finish; you will not see them.
- {checks}
- End with a short report: files written per task, and the responses or check results that support each.

{specs}"""

PREFIX = {
    "A": "No component library is provided for this run. Write each program yourself.",
    "B": "@LIBRARY_SOURCE_v1.md",
    "C": "@STABLE_PREFIX_v1.md",
    "D": "@INDEX_v1.md",
}


def prefix_text(cond):
    p = PREFIX[cond]
    return (MAN / p[1:]).read_text().rstrip("\n") if p.startswith("@") else p


def prepare(ws_root, bw_python, plain_python):
    path = HERE / "runs" / "schedule.json"
    if path.exists():
        raise SystemExit(f"{path} exists; never overwrite a schedule")
    bwc = str(Path(bw_python).parent / "bwcache")
    attempts, n = [], 0
    specs = "\n\n".join(f"## Task {i}: app/{PROGRAMS[t]}\n\n" + (EXP1 / "tasks" / t / "spec.md").read_text(encoding="utf-8").strip()
                        for i, t in enumerate(TASKS, start=1))
    for rnd, order in enumerate(ROUNDS, start=1):
        for cond in order:
            n += 1
            run_id, ws = f"s{n:02d}", Path(ws_root) / f"s{n:02d}"
            (ws / "app").mkdir(parents=True)
            if cond in ("A", "B"):
                (ws / "scratch").mkdir()
            tools = (f"\n- Tool: `{bwc}` (written `bwcache` below); run it from {ws}." if cond in ("C", "D") else "")
            checks = ("You may write and run your own checks in scratch/." if cond in ("A", "B")
                      else "Follow the trust rules above for approved blueprints; run no checks on generated files.")
            prompt = WRAPPER.format(prefix=prefix_text(cond), ws=ws, programs=", ".join(PROGRAMS[t] for t in TASKS),
                                    python=bw_python if cond in ("C", "D") else plain_python, tools=tools, budget=TOOL_BUDGET,
                                    checks=checks, specs=specs)
            (ws / "TASK_PROMPT.md").write_text(prompt, encoding="utf-8")
            out = HERE / "runs" / f"{cond}-{rnd}"
            out.mkdir(parents=True)
            (out / "prompt.md").write_text(prompt, encoding="utf-8")
            attempts.append({"run_id": run_id, "condition": cond, "round": rnd, "order_in_round": order.index(cond) + 1,
                             "workspace": str(ws), "run_dir": str(out.relative_to(HERE)), "prompt_chars": len(prompt),
                             "prefix_chars": len(prefix_text(cond)), "prompt_sha256": sha_bytes(prompt.encode())})
    path.write_text(json.dumps({"launcher": exp001.LAUNCHER, "rounds": ROUNDS, "attempts": attempts}, indent=1))
    print(json.dumps([(a["run_id"], a["condition"], a["prompt_chars"]) for a in attempts]))


def derived(u):
    return {"input_usd": round((u["input_tokens_uncached"] * PRICE["uncached"] + u["cache_write_tokens"] * PRICE["cache_write"]
                                + u["cache_read_tokens"] * PRICE["cache_read"]) / 1e6, 5),
            "input_usd_without_cache_discount": round(u["input_tokens_total"] * PRICE["uncached"] / 1e6, 5),
            "output_usd_lower_bound": round(u["output_tokens_lower_bound"] * PRICE["output"] / 1e6, 5)}


def finalize(run_id, transcript, subagent_tokens, tool_uses, duration_ms):
    sched = json.loads((HERE / "runs" / "schedule.json").read_text())
    e = next(a for a in sched["attempts"] if a["run_id"] == run_id)
    out, ws = HERE / e["run_dir"], Path(e["workspace"])
    if (out / "grades.json").exists():
        raise SystemExit(f"{run_id} already finalized; hidden tests run exactly once")
    shutil.copytree(ws / "app", out / "app", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copy(transcript, out / "transcript.jsonl")
    m = exp001.transcript_metrics(transcript, e["workspace"])
    m["agent_tool_record"] = {"subagent_tokens": int(subagent_tokens), "tool_uses": int(tool_uses), "duration_ms": int(duration_ms)}
    m["derived"] = derived(m)
    m["cache_state"] = "cold" if m["per_request"][0]["cache_read"] == 0 else "warm"
    (out / "usage.json").write_text(json.dumps(m, indent=1))
    (out / "agent_report.md").write_text(m["final_report"] + "\n", encoding="utf-8")
    pins = json.loads((MAN / "PINS_v1.json").read_text())["blueprints"]
    grades = {}
    for t in TASKS:
        g = exp001.grade(t, ws / "app")
        prog = ws / "app" / PROGRAMS[t]
        g["matches_approved_hash"] = prog.exists() and sha_bytes(prog.read_bytes()) == pins[BLUEPRINTS[t]]["program_sha256"]
        grades[t] = g
    grades["_unexpected_files"] = sorted(p.name for p in (ws / "app").iterdir() if p.name not in PROGRAMS.values())
    (out / "grades.json").write_text(json.dumps(grades, indent=1))
    ok = sum(grades[t]["all_passed"] for t in TASKS)
    print(f"{run_id} {e['condition']}-{e['round']}: {ok}/4 tasks pass, input={m['input_tokens_total']} req={m['requests']} "
          f"tools={m['tool_calls']} cache={m['cache_state']} read={m['cache_read_tokens']} write={m['cache_write_tokens']} "
          f"usd={m['derived']['input_usd']} outside={len(m['outside_workspace_paths'])}")


def compare():
    sched = json.loads((HERE / "runs" / "schedule.json").read_text())
    runs = []
    for e in sched["attempts"]:
        out = HERE / e["run_dir"]
        if not (out / "grades.json").exists():
            runs.append({**e, "executed": False})
            continue
        u, g = json.loads((out / "usage.json").read_text()), json.loads((out / "grades.json").read_text())
        runs.append({**{k: e[k] for k in ("run_id", "condition", "round", "order_in_round", "prefix_chars", "prompt_chars")},
                     "executed": True, "tasks_passed": sum(g[t]["all_passed"] for t in TASKS),
                     "tasks_matching_approved_hash": sum(g[t]["matches_approved_hash"] for t in TASKS),
                     "per_task_tests": {t: f"{g[t]['tests_passed']}/{g[t]['tests_total']}" for t in TASKS},
                     "cache_state": u["cache_state"], "requests": u["requests"], "tool_calls": u["tool_calls"],
                     "tool_calls_by_name": u["tool_calls_by_name"], "input": u["input_tokens_total"],
                     "uncached": u["input_tokens_uncached"], "cache_write": u["cache_write_tokens"], "cache_read": u["cache_read_tokens"],
                     "first_request": u["per_request"][0], "output_lower_bound": u["output_tokens_lower_bound"],
                     "generated_chars": u["generated_chars"], "duration_s": round(u["agent_tool_record"]["duration_ms"] / 1000, 1),
                     **u["derived"], "outside": len(u["outside_workspace_paths"]), "models": u["model_sha256"],
                     "per_request": u["per_request"]})
    done = [r for r in runs if r["executed"]]
    by = {}
    for c in CONDITIONS:
        rs = [r for r in done if r["condition"] == c]
        if not rs:
            continue
        succ = sum(r["tasks_passed"] for r in rs)
        by[c] = {"sessions": len(rs), "tasks_passed": f"{succ}/{4 * len(rs)}",
                 "mean_input": round(statistics.mean(r["input"] for r in rs)), "mean_requests": statistics.mean(r["requests"] for r in rs),
                 "mean_tool_calls": statistics.mean(r["tool_calls"] for r in rs),
                 "mean_cache_read_share": round(statistics.mean(r["cache_read"] / r["input"] for r in rs), 4),
                 "input_usd_per_successful_task": round(sum(r["input_usd"] for r in rs) / succ, 5) if succ else None,
                 "input_usd_per_successful_task_without_cache_discount":
                     round(sum(r["input_usd_without_cache_discount"] for r in rs) / succ, 5) if succ else None,
                 "mean_duration_s": round(statistics.mean(r["duration_s"] for r in rs), 1),
                 "cache_states": [r["cache_state"] for r in rs]}
    res = {"note": "Measured: provider-reported input, cache-write and cache-read tokens per request. Output tokens: lower bound only "
                   "(UNMEASURED). USD: derived from Sonnet 5.5 list prices incl. cache discounts; no billing data.",
           "price_basis_usd_per_M": PRICE, "by_condition": by, "sessions": runs}
    path = HERE / "CACHE_RESULTS.json"
    existing = json.loads(path.read_text()) if path.exists() else {}
    existing["pilot"] = res
    path.write_text(json.dumps(existing, indent=1))
    print(json.dumps(by, indent=1))


def local_phase():
    """Phase 1/2/4 local results into CACHE_RESULTS.json (no model calls)."""
    path = HERE / "CACHE_RESULTS.json"
    existing = json.loads(path.read_text()) if path.exists() else {}
    existing["local"] = {"validate": validate(), "version_change": version_change(), "provider_cache_evidence": cache_evidence(),
                         "manifest_chars": {p.name: len(p.read_text()) for p in sorted(MAN.glob("*.md"))}}
    path.write_text(json.dumps(existing, indent=1))


if __name__ == "__main__":
    cmd, args = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ("", [])
    table = {"build": build, "validate": validate, "version_change": version_change, "cache_evidence": cache_evidence,
             "prepare": prepare, "finalize": finalize, "compare": compare, "local": local_phase}
    if cmd not in table:
        raise SystemExit(__doc__)
    table[cmd](*args)
