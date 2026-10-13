"""Post-run analysis: derived costs, per-cell stats, drift. Writes analysis.json next to results.json."""
import hashlib, json, os, statistics, subprocess, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
BW = os.environ.get("BW_BIN", "blockwise")  # a blockwise executable from the audited commit
PRICE = {"uncached": 2.00, "cache_write": 2.50, "cache_read": 0.20, "output": 10.00}  # USD per M, list price
PROG = {"T1_csv_report": "report.py", "T2_todo_cli": "todo.py", "T3_kv_store": "store.py", "T4_log_stats": "logstats.py", "T5_inventory": "inventory.py"}
BP = {"T1_csv_report": "csv_report", "T2_todo_cli": "todo_cli", "T3_kv_store": "kv_store", "T4_log_stats": "log_stats"}

def derived(u):
    inp = (u["input_tokens_uncached"] * PRICE["uncached"] + u["cache_write_tokens"] * PRICE["cache_write"]
           + u["cache_read_tokens"] * PRICE["cache_read"]) / 1e6
    return round(inp, 5), round(u["output_tokens_lower_bound"] * PRICE["output"] / 1e6, 5)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

_TMP = Path(tempfile.mkdtemp())

def blueprint_program(task):
    """The program an unedited `blockwise apply <blueprint> --into app` writes."""
    ws = _TMP / task
    if not (ws / "app" / PROG[task]).exists():
        ws.mkdir()
        subprocess.run([BW, "apply", BP[task], "--into", "app"], cwd=ws, check=True, capture_output=True)
    return ws / "app" / PROG[task]

def drift(entry):
    ws = Path(entry["workspace"])
    if not (ws / ".blockwise/plan.json").exists():
        return {"applied": False}
    r = subprocess.run([BW, "check"], cwd=ws, capture_output=True, text=True)
    out = r.stdout.strip()
    try: data = json.loads(out)
    except ValueError: data = {"raw": out}
    task = entry["task"]; prog = ws / "app" / PROG[task]
    pristine = None
    if task in BP and prog.exists():
        pristine = sha(blueprint_program(task)) == sha(prog)
    return {"applied": True, "check_exit": r.returncode, "check_ok": data.get("ok"),
            "issues": [f"{i.get('function')}:{i.get('problem')}" for i in data.get("issues", [])] if isinstance(data.get("issues"), list) else data.get("issues"),
            "program_identical_to_blueprint": pristine}

def stats(xs):
    xs = list(xs)
    return {"n": len(xs), "mean": round(statistics.mean(xs), 4), "median": statistics.median(xs),
            "sd": round(statistics.stdev(xs), 4) if len(xs) > 1 else None, "min": min(xs), "max": max(xs)}

runs = []
for phase in ("pilot", "main"):
    sch = json.loads((HERE / "runs" / phase / "schedule.json").read_text())
    for e in sch["attempts"]:
        out = HERE / e["run_dir"]
        if not (out / "grade.json").exists():
            runs.append({"phase": phase, "run_id": e["run_id"], "task": e["task"], "cond": e["condition"], "trial": e["trial"], "executed": False}); continue
        g = json.loads((out / "grade.json").read_text()); u = json.loads((out / "usage.json").read_text())
        di, do = derived(u)
        runs.append({"phase": phase, "run_id": e["run_id"], "task": e["task"], "cond": e["condition"], "trial": e["trial"], "executed": True,
                     "success": g["all_passed"], "tests": f"{g['tests_passed']}/{g['tests_total']}", "requests": u["requests"],
                     "input": u["input_tokens_total"], "uncached": u["input_tokens_uncached"], "cache_write": u["cache_write_tokens"],
                     "cache_read": u["cache_read_tokens"], "growth": u["context_growth_tokens"], "out_lb": u["output_tokens_lower_bound"],
                     "derived_input_usd": di, "derived_output_usd_lb": do, "tool_calls": u["tool_calls"], "bw_calls": u["blockwise_calls"],
                     "show_calls": u["blockwise_show_calls"], "self_checks": u["self_check_runs"], "gen_chars": u["generated_chars"],
                     "duration_s": round(u["agent_tool_record"]["duration_ms"] / 1000, 1), "outside": len(u["outside_workspace_paths"]),
                     "models": u["model_sha256"], "drift": drift(e) if e["condition"] in ("C", "C2") else None})

main = [r for r in runs if r["phase"] == "main" and r["executed"]]
cells = {}
for t in PROG:
    for c in ("A", "B", "C", "C2"):
        rs = [r for r in main if r["task"] == t and r["cond"] == c]
        if not rs: continue
        cells[f"{t}/{c}"] = {"runs": len(rs), "successes": sum(r["success"] for r in rs), "input": stats(r["input"] for r in rs),
                             "derived_input_usd": stats(r["derived_input_usd"] for r in rs), "requests": stats(r["requests"] for r in rs),
                             "duration_s": stats(r["duration_s"] for r in rs), "repairs": stats(max(0, r["self_checks"] - 1) for r in rs)}
red = {}
for t in PROG:
    a = cells[f"{t}/A"]
    for c in ("B", "C", "C2"):
        k = f"{t}/{c}"
        if k in cells:
            red[k] = {"token_reduction_pct": round((a["input"]["mean"] - cells[k]["input"]["mean"]) / a["input"]["mean"] * 100, 1),
                      "derived_usd_reduction_pct": round((a["derived_input_usd"]["mean"] - cells[k]["derived_input_usd"]["mean"]) / a["derived_input_usd"]["mean"] * 100, 1)}
pooled = {}
for scope, tasks in (("T1-T4 (blueprint covered)", list(BP)), ("T5 (not covered)", ["T5_inventory"]), ("all", list(PROG))):
    for c in ("A", "B", "C", "C2"):
        rs = [r for r in main if r["task"] in tasks and r["cond"] == c]
        if not rs: continue
        cost = sum(r["derived_input_usd"] for r in rs); succ = sum(r["success"] for r in rs)
        pooled[f"{scope}/{c}"] = {"runs": len(rs), "success_rate": round(succ / len(rs), 3), "mean_input": round(statistics.mean(r["input"] for r in rs)),
                                  "mean_requests": round(statistics.mean(r["requests"] for r in rs), 2),
                                  "derived_input_usd_per_successful_task": round(cost / succ, 4) if succ else None,
                                  "derived_output_usd_lb_per_run": round(statistics.mean(r["derived_output_usd_lb"] for r in rs), 4)}
drift_rows = [{"run_id": r["run_id"], "task": r["task"], "cond": r["cond"], **r["drift"]} for r in main if r["drift"]]
res = {"price_basis_usd_per_M": PRICE, "note": "derived_* figures are measured tokens x list price, not billing. Output is a lower bound.",
       "cells": cells, "reduction_vs_A": red, "pooled": pooled, "drift": drift_rows, "runs": runs}
(HERE / "analysis.json").write_text(json.dumps(res, indent=1))
for k, v in pooled.items(): print(k, v)
for k, v in red.items(): print(k, v)
