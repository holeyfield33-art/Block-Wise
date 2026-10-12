"""Block-Wise token-efficiency benchmark: minimal reproducible runner (standard library + blockwise).

Commands
  validate                 check the harness: every blueprint program (T1-T4) and the T5 plan build
                           must pass the frozen acceptance tests before any model is called
  prepare <ws_root> <plain_python> <bw_python> [--pilot]
                           write fresh workspaces + exact prompts for the schedule (runs/schedule.json)
  finalize <run_id> <transcript.jsonl> <subagent_tokens> <tool_uses> <duration_ms>
                           collect an attempt, extract measured usage from its transcript, grade it
  grade <task> <program_dir>
                           run the acceptance tests against a directory containing the program
  aggregate                write results.json and results.csv

Agents are launched outside this script (fresh sub-agent per run, same pinned model) with the
one-line LAUNCHER pointing at the workspace's TASK_PROMPT.md. Environment:
  BW_HIDDEN  directory holding the acceptance tests (kept outside the repo until runs are collected)
"""

import base64
import csv
import hashlib
import json
import os
import random
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASKS = HERE / "tasks"
RUNS = HERE / "runs"
HIDDEN = Path(os.environ.get("BW_HIDDEN", str(HERE / "acceptance")))
PROGRAMS = {"T1_csv_report": "report.py", "T2_todo_cli": "todo.py", "T3_kv_store": "store.py",
            "T4_log_stats": "logstats.py", "T5_inventory": "inventory.py"}
BLUEPRINTS = {"T1_csv_report": "csv_report", "T2_todo_cli": "todo_cli", "T3_kv_store": "kv_store", "T4_log_stats": "log_stats"}
CONDITIONS = ("A", "B", "C")
TRIALS = 3
SEED = 20261012
TOOL_BUDGET = 30
LAUNCHER = "Your complete instructions are in the file {ws}/TASK_PROMPT.md. Read that file first and follow it exactly."

WRAPPER = """You are the coding agent for one run of a controlled benchmark.

Workspace: {ws}
- Work ONLY inside the workspace. Do not read, list or search anything outside it; other runs and
  evaluation files exist on this machine and looking at them invalidates the run.
- Deliverable: the program file {ws}/app/{program}. Put nothing else you write in app/ except files a
  tool you were told to use creates there.
- You may write and run your own checks in {ws}/scratch/.
- Python: {python} . Do not install packages. No network access.
- Budget: at most {budget} tool calls. There is one attempt. Hidden acceptance tests will run
  `python app/{program} ...` from a fresh temporary directory after you finish.
- End with a short report: files written, whether your own checks passed, how many times you ran them.

{materials}"""

MATERIALS_A = """## Specification

{spec}"""

MATERIALS_B = """## Specification

{spec}

## Structured plan (Block-Wise plan.json)

The program must follow this plan exactly: same module, imports, constants, functions (names,
typed parameters, return types) and body structure. Element kinds: `branch` = if/else
(`otherwise` is the else part), `loop` = for, `while`, `try` (with `handler` = except), `with`,
`assign`, `call` = an expression statement, `validate` = a call that checks input, `return`,
`raise`; `entry` is the module's main block (`if __name__ == '__main__':`). Write the Python
yourself; no Block-Wise tool is available.

```json
{plan}
```"""

MATERIALS_C = """## Specification

{spec}

## Tool available: Block-Wise

Block-Wise is installed: run it as `{bw} <command>` from the workspace directory {ws}. Every command
prints one compact JSON line. Commands:
- `{bw} find <words>`: the 3 best-matching presets/blueprints for a few words
- `{bw} list [--category validation|auth|data|files|blueprint]`
- `{bw} show <id> [--set k=v ...]`: the code a preset or blueprint would write (not written to disk)
- `{bw} apply <id> --into <file.py or folder> [--set k=v ...]`: writes it (blueprints take a folder)
- `{bw} check`: structure check of everything applied
Exit codes: 0 ok, 1 check found issues, 2 bad input.

Rules for using it (adapted from the project's docs/agent-instructions.md):
1. Before writing a small, common Python function or a small command-line tool, search with `find`.
2. If a result fits, `apply` it with the right names. Don't re-type code a preset provides. Do not
   print or read generated code unless your own checks fail and you need it to fix a problem.
3. If the result lists a `todo`, fill only that part. After editing files Block-Wise wrote, run `check`.
4. Block-Wise checks structure, not behavior: still run your own behavioral checks.
If nothing fits, write the code normally. Don't force a preset that doesn't match the task."""


# ---------------------------------------------------------------- acceptance tests
def run_scenarios(task, program_dir, timeout=15):
    """Run every acceptance scenario; each step is one test. Returns per-step results."""
    tests = json.loads((HIDDEN / f"{task}.json").read_text(encoding="utf-8"))
    program = Path(program_dir).resolve() / tests["program"]
    results = []
    for scenario in tests["scenarios"]:
        with tempfile.TemporaryDirectory(prefix="accept-") as tmp:
            for name, text in scenario.get("files", {}).items():
                (Path(tmp) / name).write_text(text, encoding="utf-8", newline="")
            for name, b64 in scenario.get("files_b64", {}).items():
                (Path(tmp) / name).write_bytes(base64.b64decode(b64))
            for index, step in enumerate(scenario["steps"]):
                case = f"{scenario['name']}#{index + 1}"
                if not program.exists():
                    results.append({"case": case, "ok": False, "why": "program missing"})
                    continue
                env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
                try:
                    proc = subprocess.run([sys.executable, str(program), *step["argv"]], cwd=tmp, capture_output=True,
                                          timeout=timeout, env=env, check=False)
                    out = proc.stdout.decode("utf-8", errors="replace").replace("\r\n", "\n")
                    ok = out == step["stdout"] and proc.returncode == step["exit"]
                    why = "" if ok else f"exit {proc.returncode} (want {step['exit']}); stdout {out[:200]!r} (want {step['stdout'][:200]!r}); stderr {proc.stderr.decode(errors='replace')[-300:]!r}"
                except subprocess.TimeoutExpired:
                    ok, why = False, "timeout"
                results.append({"case": case, "ok": ok, "why": why})
    return results


def grade(task, program_dir):
    results = run_scenarios(task, program_dir)
    program = Path(program_dir) / PROGRAMS[task]
    source = program.read_text(encoding="utf-8") if program.exists() else ""
    try:
        compile(source, str(program), "exec")
        syntax_ok = bool(source)
    except SyntaxError:
        syntax_ok = False
    return {"tests_passed": sum(r["ok"] for r in results), "tests_total": len(results),
            "all_passed": bool(results) and all(r["ok"] for r in results), "syntax_ok": syntax_ok,
            "program_bytes": len(source.encode()), "program_lines": source.count("\n"),
            "failed": [r for r in results if not r["ok"]]}


# ---------------------------------------------------------------- harness validation
def validate():
    from blockwise.compiler import write_project
    from blockwise.presets import load_blueprints, render_blueprint

    ok = True
    blueprints = load_blueprints()
    for task, blueprint_id in BLUEPRINTS.items():
        with tempfile.TemporaryDirectory() as tmp:
            write_project(render_blueprint(blueprints[blueprint_id]), Path(tmp) / "b")
            g = grade(task, Path(tmp) / "b" / "repo")
        print(task, "blueprint", blueprint_id, f"{g['tests_passed']}/{g['tests_total']}", g["failed"][:2])
        ok &= g["all_passed"]
    from blockwise.schema import load_score

    with tempfile.TemporaryDirectory() as tmp:
        write_project(load_score(TASKS / "T5_inventory" / "plan.json"), Path(tmp) / "b")
        g = grade("T5_inventory", Path(tmp) / "b" / "repo")
    print("T5_inventory", "hand-written plan", f"{g['tests_passed']}/{g['tests_total']}", g["failed"][:2])
    ok &= g["all_passed"]
    with tempfile.TemporaryDirectory() as tmp:  # a program that does nothing must fail every test
        (Path(tmp) / "report.py").write_text("print('hi')\n")
        g = grade("T1_csv_report", tmp)
    print("negative control: trivial program", f"{g['tests_passed']}/{g['tests_total']}")
    ok &= g["tests_passed"] == 0
    sys.exit(0 if ok else 1)


def plan_for(task):
    from blockwise.presets import load_blueprints, render_blueprint
    if task in BLUEPRINTS:
        return render_blueprint(load_blueprints()[BLUEPRINTS[task]])
    return json.loads((TASKS / task / "plan.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------- preparation
def prepare(ws_root, plain_python, bw_python, pilot=False):
    ws_root = Path(ws_root)
    bw = str(Path(bw_python).parent / "blockwise")
    if pilot:
        plan = [("T1_csv_report", c, 1) for c in CONDITIONS] + [("T5_inventory", c, 1) for c in CONDITIONS] \
            + [("T1_csv_report", "C2", 1)]
    else:
        plan = [(t, c, k) for t in PROGRAMS for c in CONDITIONS for k in range(1, TRIALS + 1)] \
            + [(t, "C2", k) for t in BLUEPRINTS for k in range(1, TRIALS + 1)]
    random.Random(SEED).shuffle(plan)
    schedule_path = RUNS / ("pilot" if pilot else "main") / "schedule.json"
    if schedule_path.exists():
        raise SystemExit(f"{schedule_path} exists; never overwrite a schedule")
    attempts = []
    for index, (task, cond, trial) in enumerate(plan, start=1):
        run_id = f"{'p' if pilot else 'r'}{index:02d}"
        ws = ws_root / run_id
        ws.mkdir(parents=True)
        (ws / "app").mkdir()
        (ws / "scratch").mkdir()
        spec = (TASKS / task / "spec.md").read_text(encoding="utf-8").strip()
        if cond == "A":
            materials, python = MATERIALS_A.format(spec=spec), plain_python
        elif cond == "B":
            materials, python = MATERIALS_B.format(spec=spec, plan=json.dumps(plan_for(task), indent=1)), plain_python
        else:
            materials, python = MATERIALS_C.format(spec=spec, bw=bw, ws=ws), bw_python
            if cond == "C2":  # repeated-template use: the agent already knows which blueprint fits
                materials += (f"\n\nFrom earlier work you already know the right template: run "
                              f"`{bw} apply {BLUEPRINTS[task]} --into app`, then verify.")
        prompt = WRAPPER.format(ws=ws, program=PROGRAMS[task], python=python, budget=TOOL_BUDGET, materials=materials)
        (ws / "TASK_PROMPT.md").write_text(prompt, encoding="utf-8")
        out = RUNS / ("pilot" if pilot else "main") / task / f"{cond}-{trial}"
        out.mkdir(parents=True)
        (out / "prompt.md").write_text(prompt, encoding="utf-8")
        attempts.append({"run_id": run_id, "task": task, "condition": cond, "trial": trial, "workspace": str(ws),
                         "run_dir": str(out.relative_to(HERE)), "prompt_chars": len(prompt),
                         "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()})
    schedule_path.write_text(json.dumps({"seed": SEED, "pilot": pilot, "launcher": LAUNCHER, "attempts": attempts}, indent=1))
    print(f"prepared {len(attempts)} runs -> {schedule_path}")


# ---------------------------------------------------------------- transcript metrics
def transcript_metrics(path, workspace):
    """Measured usage per model request from the sub-agent transcript.

    Input fields (uncached, cache write, cache read) are recorded by the API before generation and are
    exact. output_tokens is logged mid-stream and is only a lower bound, so it is reported as such.
    """
    lines = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    requests, models, tool_calls, generated_chars, tool_result_chars, final_report = {}, set(), [], 0, 0, ""
    for entry in lines:
        message = entry.get("message") or {}
        if message.get("role") == "assistant":
            rid = entry.get("requestId") or message.get("id")
            usage = message.get("usage") or {}
            previous = requests.get(rid, {})
            requests[rid] = {**usage, "output_tokens": max(previous.get("output_tokens", 0), usage.get("output_tokens", 0))}
            if message.get("model"):
                models.add(message["model"])
            for block in message.get("content") or []:
                if block.get("type") == "text":
                    generated_chars += len(block.get("text", ""))
                elif block.get("type") == "tool_use":
                    generated_chars += len(json.dumps(block.get("input"), ensure_ascii=False))
                    tool_calls.append({"name": block.get("name"), "input": block.get("input")})
                    if block.get("name") == "SubagentHandback":
                        final_report = block["input"].get("message", "")
        elif message.get("role") == "user" and isinstance(message.get("content"), list):
            for block in message["content"]:
                if block.get("type") == "tool_result":
                    content = block.get("content")
                    text = content if isinstance(content, str) else "".join(c.get("text", "") for c in content or [])
                    tool_result_chars += len(text)
    per_request = [{"input_uncached": u.get("input_tokens", 0), "cache_write": u.get("cache_creation_input_tokens", 0),
                    "cache_read": u.get("cache_read_input_tokens", 0), "output_lower_bound": u.get("output_tokens", 0)}
                   for u in requests.values() if u]
    for r in per_request:
        r["input_total"] = r["input_uncached"] + r["cache_write"] + r["cache_read"]
    bash = [c["input"].get("command", "") for c in tool_calls if c["name"] == "Bash"]
    outside = []
    for call in tool_calls:
        if call["name"] == "SubagentHandback":
            continue
        blob = json.dumps(call["input"])
        for p in re.findall(r"/(?:tmp|root|home)[^\s\"'`;|&<>)]*", blob):
            if not (p.startswith(workspace) or workspace.startswith(p.rstrip("/")) or "venv" in p):
                outside.append(p)
    names = {}
    for call in tool_calls:
        names[call["name"]] = names.get(call["name"], 0) + 1
    return {
        "requests": len(per_request), "per_request": per_request,
        "input_tokens_total": sum(r["input_total"] for r in per_request),
        "input_tokens_uncached": sum(r["input_uncached"] for r in per_request),
        "cache_write_tokens": sum(r["cache_write"] for r in per_request),
        "cache_read_tokens": sum(r["cache_read"] for r in per_request),
        "first_request_input": per_request[0]["input_total"] if per_request else None,
        "context_growth_tokens": per_request[-1]["input_total"] - per_request[0]["input_total"] if per_request else None,
        "output_tokens_lower_bound": sum(r["output_lower_bound"] for r in per_request),
        "generated_chars": generated_chars, "tool_result_chars": tool_result_chars,
        "tool_calls": len(tool_calls), "tool_calls_by_name": names,
        "blockwise_calls": sum(1 for c in bash if "blockwise" in c),
        "blockwise_show_calls": sum(1 for c in bash if re.search(r"blockwise\S*\s+show\b", c)),
        "self_check_runs": sum(1 for c in bash if "python" in c and ("app/" in c or "scratch" in c or "pytest" in c)),
        "model_sha256": sorted(hashlib.sha256(m.encode()).hexdigest()[:16] for m in models),
        "outside_workspace_paths": sorted(set(outside)), "final_report": final_report,
    }


def finalize(run_id, transcript, subagent_tokens, tool_uses, duration_ms):
    schedule = None
    for name in ("pilot", "main"):
        path = RUNS / name / "schedule.json"
        if path.exists():
            data = json.loads(path.read_text())
            if any(a["run_id"] == run_id for a in data["attempts"]):
                schedule = data
    entry = next(a for a in schedule["attempts"] if a["run_id"] == run_id)
    out, ws = HERE / entry["run_dir"], Path(entry["workspace"])
    if (out / "grade.json").exists():
        raise SystemExit(f"{run_id} already finalized; failed runs are never replaced")
    shutil.copytree(ws / "app", out / "app", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    if (ws / "scratch").exists():
        shutil.copytree(ws / "scratch", out / "agent_scratch", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
    metrics = transcript_metrics(transcript, entry["workspace"])
    metrics.update({"agent_tool_record": {"subagent_tokens": int(subagent_tokens), "tool_uses": int(tool_uses),
                                          "duration_ms": int(duration_ms)}})
    (out / "usage.json").write_text(json.dumps(metrics, indent=1))
    (out / "agent_report.md").write_text(metrics["final_report"] + "\n", encoding="utf-8")
    g = grade(entry["task"], ws / "app")
    extra = sorted(str(p.relative_to(ws / "app")) for p in (ws / "app").rglob("*")
                   if p.is_file() and p.name != PROGRAMS[entry["task"]] and "__pycache__" not in p.parts)
    g["unexpected_files_in_app"] = extra
    (out / "grade.json").write_text(json.dumps(g, indent=1))
    print(f"{run_id} {entry['task']} {entry['condition']}-{entry['trial']}: {g['tests_passed']}/{g['tests_total']} "
          f"input={metrics['input_tokens_total']} req={metrics['requests']} tools={metrics['tool_calls']} "
          f"bw={metrics['blockwise_calls']} outside={len(metrics['outside_workspace_paths'])}")


# ---------------------------------------------------------------- aggregation
def aggregate():
    rows = []
    for schedule_path in sorted(RUNS.glob("*/schedule.json")):
        schedule = json.loads(schedule_path.read_text())
        for entry in schedule["attempts"]:
            out = HERE / entry["run_dir"]
            row = {"phase": schedule_path.parent.name, "run_id": entry["run_id"], "task": entry["task"],
                   "condition": entry["condition"], "trial": entry["trial"], "executed": (out / "grade.json").exists(),
                   "prompt_chars": entry["prompt_chars"]}
            if row["executed"]:
                g, u = json.loads((out / "grade.json").read_text()), json.loads((out / "usage.json").read_text())
                row.update({"success": int(g["all_passed"]), "tests_passed": g["tests_passed"], "tests_total": g["tests_total"],
                            "program_bytes": g["program_bytes"], "unexpected_files": len(g["unexpected_files_in_app"]),
                            "requests": u["requests"], "input_tokens_total": u["input_tokens_total"],
                            "input_tokens_uncached": u["input_tokens_uncached"], "cache_write_tokens": u["cache_write_tokens"],
                            "cache_read_tokens": u["cache_read_tokens"], "first_request_input": u["first_request_input"],
                            "context_growth_tokens": u["context_growth_tokens"],
                            "output_tokens_lower_bound": u["output_tokens_lower_bound"], "generated_chars": u["generated_chars"],
                            "tool_result_chars": u["tool_result_chars"], "tool_calls": u["tool_calls"],
                            "blockwise_calls": u["blockwise_calls"], "blockwise_show_calls": u["blockwise_show_calls"],
                            "self_check_runs": u["self_check_runs"], "repair_iterations": max(0, u["self_check_runs"] - 1),
                            "duration_s": round(u["agent_tool_record"]["duration_ms"] / 1000, 1),
                            "model": " ".join(u["model_sha256"]), "outside_workspace": len(u["outside_workspace_paths"])})
            rows.append(row)
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with open(HERE / "results.csv", "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    done = [r for r in rows if r["executed"]]
    metrics = ["input_tokens_total", "context_growth_tokens", "requests", "tool_calls", "duration_s", "generated_chars",
               "output_tokens_lower_bound", "repair_iterations", "program_bytes"]
    summary = {}
    for phase in sorted({r["phase"] for r in done}):
        for cond in sorted({r["condition"] for r in done if r["phase"] == phase}):
            rs = [r for r in done if r["phase"] == phase and r["condition"] == cond]
            summary[f"{phase}/{cond}"] = {"runs": len(rs), "success_rate": round(sum(r["success"] for r in rs) / len(rs), 3),
                                          **{m: {"mean": round(statistics.mean(r[m] for r in rs), 1),
                                                 "median": statistics.median(r[m] for r in rs)} for m in metrics}}
    paired = {}
    for phase in sorted({r["phase"] for r in done}):
        for task in sorted({r["task"] for r in done if r["phase"] == phase}):
            by = {c: [r for r in done if r["phase"] == phase and r["task"] == task and r["condition"] == c] for c in ("A", "B", "C", "C2")}
            base = statistics.mean(r["input_tokens_total"] for r in by["A"]) if by["A"] else None
            entry = {}
            for c, rs in by.items():
                if rs:
                    mean_in = statistics.mean(r["input_tokens_total"] for r in rs)
                    entry[c] = {"runs": len(rs), "successes": sum(r["success"] for r in rs), "mean_input_tokens": round(mean_in),
                                "input_token_reduction_vs_A_pct": round((base - mean_in) / base * 100, 1) if base else None}
            paired[f"{phase}/{task}"] = entry
    result = {"note": "Input tokens are measured from API usage fields. Output tokens and USD cost are UNMEASURED "
                      "(output is logged mid-stream; only a lower bound is available; no billing data).",
              "planned_runs": len(rows), "executed_runs": len(done), "by_condition": summary, "by_task": paired, "runs": rows}
    (HERE / "results.json").write_text(json.dumps(result, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    command, args = sys.argv[1], sys.argv[2:]
    if command == "validate":
        validate()
    elif command == "prepare":
        prepare(args[0], args[1], args[2], pilot="--pilot" in args)
    elif command == "finalize":
        finalize(*args)
    elif command == "grade":
        print(json.dumps(grade(args[0], args[1]), indent=1))
    elif command == "aggregate":
        aggregate()
    else:
        raise SystemExit(__doc__)
