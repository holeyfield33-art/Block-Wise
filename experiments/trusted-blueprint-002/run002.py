"""Experiment 002: trusted blueprint execution (condition C3). Standard library + blockwise.

Reuses Experiment 001's frozen acceptance tests, grader and transcript parser by importing
../token-efficiency/reproduce.py read-only. Nothing in Experiment 001 is modified.

Commands
  manifest                 record the approved blueprints: ids, blueprint JSON hashes, generated-program
                           hashes, generator commit; writes MANIFEST.json
  zero_llm                 deterministic reference: `blockwise apply` with no LLM, graded once per task
  prepare <ws_root> <bw_python>
                           write fresh C3 workspaces + prompts (runs/schedule.json); never overwrites
  finalize <run_id> <transcript.jsonl> <subagent_tokens> <tool_uses> <duration_ms>
                           grade an attempt ONCE with the hidden tests; never re-run or repaired
  compare                  TRUSTED_RESULTS.json: C3 against Experiment 001 A and C2 (historical controls)
Environment:
  BW_BIN     blockwise executable (default: blockwise)
  BW_HIDDEN  acceptance-test directory (default: ../token-efficiency/acceptance)
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
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP1 = HERE.parent / "token-efficiency"
REPO = HERE.parents[1]
os.environ.setdefault("BW_HIDDEN", str(EXP1 / "acceptance"))
_spec = importlib.util.spec_from_file_location("exp001", EXP1 / "reproduce.py")
exp001 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(exp001)

BW = os.environ.get("BW_BIN", "blockwise")
RUNS = HERE / "runs"
TASKS = ["T1_csv_report", "T2_todo_cli", "T3_kv_store", "T4_log_stats"]
PROGRAMS, BLUEPRINTS = exp001.PROGRAMS, exp001.BLUEPRINTS
SEED = 20261013
TOOL_BUDGET = 5
# Same list prices as Experiment 001 (USD per million tokens); derived, not billing.
PRICE = {"uncached": 2.00, "cache_write": 2.50, "cache_read": 0.20, "output": 10.00}

WRAPPER_C3 = """You are the coding agent for one run of a controlled benchmark.

Workspace: {ws}
- Work ONLY inside the workspace. Do not read, list or search anything outside it; other runs and
  evaluation files exist on this machine and looking at them invalidates the run.
- Deliverable: the program file {ws}/app/{program}. Put nothing else in app/.
- Python: {python} . Do not install packages. No network access.
- Budget: at most {budget} tool calls. There is one attempt. Hidden acceptance tests will run
  `python app/{program} ...` from a fresh temporary directory after you finish; you will not see them.
- End with a short completion record: files written and the generation response.

{materials}"""

MATERIALS_C3 = """## Specification

{spec}

## Approved component: Block-Wise blueprint `{bp}`

This specification is implemented by the approved, previously tested Block-Wise blueprint `{bp}`
(blueprint file sha256 {bp_sha}). Delegate the implementation to it:

    cd {ws} && {bw} apply {bp} --into app

Trust rules for this run:
1. The blueprint is an approved component that already passes its acceptance tests.
2. Run the command above once. A response with `"ok":true` means the task is complete.
3. Do not open, read, print or inspect any generated file.
4. Do not rewrite, improve or extend the generated code.
5. Do not run `{bw} check`.
6. Do not run the program, tests or any debugging.
7. Do not run `apply` again after a successful response.
8. Do not write documentation or any other file.
9. If the response is not `"ok":true`, stop and report the response; do not try to fix it.
10. Finish with the file path(s) from the response and the response line itself."""


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def blueprint_file(bp):
    return REPO / "blockwise" / "library" / "blueprints" / f"{bp}.json"


def generator_commit():
    out = subprocess.run(["git", "-C", str(REPO), "log", "-1", "--format=%H", "--", "blockwise"],
                         capture_output=True, text=True, check=True)
    return out.stdout.strip()


def apply_blueprint(bp, into_dir, extra=()):
    start = time.perf_counter()
    r = subprocess.run([BW, "apply", bp, "--into", "app", *extra], cwd=into_dir, capture_output=True, text=True)
    return r, round(time.perf_counter() - start, 3)


# ---------------------------------------------------------------- manifest + zero-LLM reference
def manifest():
    entries = {}
    for task in TASKS:
        bp = BLUEPRINTS[task]
        with tempfile.TemporaryDirectory() as tmp:
            r, _ = apply_blueprint(bp, tmp)
            if r.returncode != 0:
                raise SystemExit(f"{bp}: apply failed: {r.stdout}{r.stderr}")
            program = Path(tmp) / "app" / PROGRAMS[task]
            entries[bp] = {"task": task, "blueprint_file": str(blueprint_file(bp).relative_to(REPO)),
                           "blueprint_sha256": sha_file(blueprint_file(bp)), "program": PROGRAMS[task],
                           "generated_program_sha256": sha_file(program), "configuration": "default (no --set)",
                           "apply_response": r.stdout.strip()}
    data = {"generator_commit": generator_commit(), "approved_blueprints": entries,
            "trust_scope": "Only these blueprint ids, at these hashes, in the default configuration."}
    (HERE / "MANIFEST.json").write_text(json.dumps(data, indent=1))
    print(json.dumps(data, indent=1))


def zero_llm():
    rows = []
    for task in TASKS:
        bp = BLUEPRINTS[task]
        with tempfile.TemporaryDirectory() as tmp:
            r, seconds = apply_blueprint(bp, tmp)
            g = exp001.grade(task, Path(tmp) / "app")
            rows.append({"task": task, "blueprint": bp, "apply_exit": r.returncode, "apply_seconds": seconds,
                         "response_chars": len(r.stdout.strip()), "tests": f"{g['tests_passed']}/{g['tests_total']}",
                         "success": g["all_passed"], "llm_tokens": 0, "llm_requests": 0,
                         "generated_program_sha256": sha_file(Path(tmp) / "app" / PROGRAMS[task])})
            print(rows[-1])
    (HERE / "ZERO_LLM.json").write_text(json.dumps({"note": "Deterministic generation with no model involved. "
                                                    "Local CPU time only; not an AI coding condition.", "runs": rows}, indent=1))


# ---------------------------------------------------------------- C3 runs
def prepare(ws_root, bw_python):
    schedule_path = RUNS / "pilot" / "schedule.json"
    if schedule_path.exists():
        raise SystemExit(f"{schedule_path} exists; never overwrite a schedule")
    man = json.loads((HERE / "MANIFEST.json").read_text())["approved_blueprints"]
    bw = str(Path(bw_python).parent / "blockwise")
    import random
    order = list(TASKS)
    random.Random(SEED).shuffle(order)
    attempts = []
    for index, task in enumerate(order, start=1):
        bp, run_id = BLUEPRINTS[task], f"t{index:02d}"
        if sha_file(blueprint_file(bp)) != man[bp]["blueprint_sha256"]:
            raise SystemExit(f"{bp} changed since MANIFEST.json; it is no longer the approved version")
        ws = Path(ws_root) / run_id
        (ws / "app").mkdir(parents=True)
        spec = (EXP1 / "tasks" / task / "spec.md").read_text(encoding="utf-8").strip()
        materials = MATERIALS_C3.format(spec=spec, bp=bp, bp_sha=man[bp]["blueprint_sha256"], bw=bw, ws=ws)
        prompt = WRAPPER_C3.format(ws=ws, program=PROGRAMS[task], python=bw_python, budget=TOOL_BUDGET, materials=materials)
        (ws / "TASK_PROMPT.md").write_text(prompt, encoding="utf-8")
        out = RUNS / "pilot" / task / "C3-1"
        out.mkdir(parents=True)
        (out / "prompt.md").write_text(prompt, encoding="utf-8")
        attempts.append({"run_id": run_id, "task": task, "condition": "C3", "trial": 1, "blueprint": bp,
                         "workspace": str(ws), "run_dir": str(out.relative_to(HERE)), "prompt_chars": len(prompt),
                         "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()})
    schedule_path.write_text(json.dumps({"seed": SEED, "launcher": exp001.LAUNCHER, "attempts": attempts}, indent=1))
    print(f"prepared {len(attempts)} runs -> {schedule_path}")


def derived_usd(u):
    inp = (u["input_tokens_uncached"] * PRICE["uncached"] + u["cache_write_tokens"] * PRICE["cache_write"]
           + u["cache_read_tokens"] * PRICE["cache_read"]) / 1e6
    return round(inp, 5)


def finalize(run_id, transcript, subagent_tokens, tool_uses, duration_ms):
    schedule = json.loads((RUNS / "pilot" / "schedule.json").read_text())
    entry = next(a for a in schedule["attempts"] if a["run_id"] == run_id)
    out, ws = HERE / entry["run_dir"], Path(entry["workspace"])
    if (out / "grade.json").exists():
        raise SystemExit(f"{run_id} already finalized; the hidden tests run exactly once")
    shutil.copytree(ws / "app", out / "app", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copy(transcript, out / "transcript.jsonl")  # raw model usage record
    m = exp001.transcript_metrics(transcript, entry["workspace"])
    m["agent_tool_record"] = {"subagent_tokens": int(subagent_tokens), "tool_uses": int(tool_uses), "duration_ms": int(duration_ms)}
    m["derived_input_usd"] = derived_usd(m)
    (out / "usage.json").write_text(json.dumps(m, indent=1))
    (out / "agent_report.md").write_text(m["final_report"] + "\n", encoding="utf-8")
    program = ws / "app" / PROGRAMS[entry["task"]]
    g = exp001.grade(entry["task"], ws / "app")  # once; no repair, no regeneration
    man = json.loads((HERE / "MANIFEST.json").read_text())["approved_blueprints"][entry["blueprint"]]
    g["unexpected_files_in_app"] = sorted(str(p.relative_to(ws / "app")) for p in (ws / "app").rglob("*")
                                          if p.is_file() and p.name != PROGRAMS[entry["task"]] and "__pycache__" not in p.parts)
    g["program_matches_approved_hash"] = program.exists() and sha_file(program) == man["generated_program_sha256"]
    (out / "grade.json").write_text(json.dumps(g, indent=1))
    print(f"{run_id} {entry['task']} C3: {g['tests_passed']}/{g['tests_total']} input={m['input_tokens_total']} "
          f"req={m['requests']} tools={m['tool_calls']} bw={m['blockwise_calls']} show={m['blockwise_show_calls']} "
          f"selfcheck={m['self_check_runs']} pristine={g['program_matches_approved_hash']} "
          f"outside={len(m['outside_workspace_paths'])} usd={m['derived_input_usd']}")


# ---------------------------------------------------------------- comparison
def compare():
    hist = [r for r in json.loads((EXP1 / "analysis.json").read_text())["runs"]
            if r["phase"] == "main" and r["executed"] and r["task"] in TASKS and r["cond"] in ("A", "C2")]
    c3 = []
    sched = json.loads((RUNS / "pilot" / "schedule.json").read_text())
    for e in sched["attempts"]:
        out = HERE / e["run_dir"]
        if not (out / "grade.json").exists():
            c3.append({"run_id": e["run_id"], "task": e["task"], "cond": "C3", "executed": False})
            continue
        u, g = json.loads((out / "usage.json").read_text()), json.loads((out / "grade.json").read_text())
        c3.append({"run_id": e["run_id"], "task": e["task"], "cond": "C3", "executed": True, "success": g["all_passed"],
                   "tests": f"{g['tests_passed']}/{g['tests_total']}", "requests": u["requests"], "input": u["input_tokens_total"],
                   "uncached": u["input_tokens_uncached"], "cache_write": u["cache_write_tokens"], "cache_read": u["cache_read_tokens"],
                   "first_request_input": u["first_request_input"], "growth": u["context_growth_tokens"],
                   "repeated_context_tokens": u["input_tokens_total"] - u["first_request_input"],
                   "out_lb": u["output_tokens_lower_bound"], "derived_input_usd": u["derived_input_usd"],
                   "tool_calls": u["tool_calls"], "tool_calls_by_name": u["tool_calls_by_name"], "bw_calls": u["blockwise_calls"],
                   "show_calls": u["blockwise_show_calls"], "self_checks": u["self_check_runs"],
                   "duration_s": round(u["agent_tool_record"]["duration_ms"] / 1000, 1),
                   "pristine": g["program_matches_approved_hash"], "outside": len(u["outside_workspace_paths"]),
                   "models": u["model_sha256"], "per_request": u["per_request"]})
    done = [r for r in c3 if r["executed"]]

    def cell(rows):
        if not rows:
            return None
        succ = sum(bool(r["success"]) for r in rows)
        mean = lambda k: round(statistics.mean(r[k] for r in rows), 1)
        return {"runs": len(rows), "successes": succ, "mean_input": mean("input"), "mean_requests": mean("requests"),
                "mean_tool_calls": mean("tool_calls"), "mean_duration_s": mean("duration_s"),
                "mean_derived_input_usd": round(statistics.mean(r["derived_input_usd"] for r in rows), 5),
                "derived_input_usd_per_success": round(sum(r["derived_input_usd"] for r in rows) / succ, 5) if succ else None,
                "mean_output_lower_bound": mean("out_lb")}

    tasks_done = sorted({r["task"] for r in done})
    by_task = {}
    for t in TASKS:
        a = [r for r in hist if r["task"] == t and r["cond"] == "A"]
        c2 = [r for r in hist if r["task"] == t and r["cond"] == "C2"]
        c = [r for r in done if r["task"] == t]
        by_task[t] = {"A_historical": cell(a), "C2_historical": cell(c2), "C3": cell(c)}
    matched = {k: cell([r for r in rows if r["task"] in tasks_done]) for k, rows in
               (("A_historical", [r for r in hist if r["cond"] == "A"]), ("C2_historical", [r for r in hist if r["cond"] == "C2"]),
                ("C3", done))}
    zero = json.loads((HERE / "ZERO_LLM.json").read_text()) if (HERE / "ZERO_LLM.json").exists() else None
    result = {"note": "A and C2 are HISTORICAL CONTROLS from Experiment 001 (main phase), not fresh randomized trials. "
                      "Input tokens are measured from API usage fields; output tokens are a lower bound only (UNMEASURED); "
                      "USD is derived from list prices, not billing.",
              "price_basis_usd_per_M": PRICE, "matched_tasks": tasks_done, "matched": matched, "by_task": by_task,
              "zero_llm_reference": zero, "c3_runs": c3}
    (HERE / "TRUSTED_RESULTS.json").write_text(json.dumps(result, indent=1))
    print(json.dumps({"matched": matched, "by_task": by_task}, indent=1))


if __name__ == "__main__":
    command, args = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ("", [])
    commands = {"manifest": manifest, "zero_llm": zero_llm, "prepare": prepare, "finalize": finalize, "compare": compare}
    if command not in commands:
        raise SystemExit(__doc__)
    commands[command](*args)
