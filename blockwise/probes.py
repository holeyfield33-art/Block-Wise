"""Security probes: run a block's declared probes against its generated code.

A security block is a blueprint with a ``security`` section: the threats it
defends against and the probes that test each one. Probes are data only (call
arguments, the expected outcome, and files that must or must not exist); the
only code that runs is this trusted runner and the generated function itself.

Each probe gets a fresh temporary tree: ``root/`` is the authorized workspace
and ``outside/`` holds a sentinel file. The function is called in a separate,
isolated Python process with a timeout. The verdict comes from two
observations, never from the probe's own say-so:

  * the outcome - did the call return or raise what the probe declares?
  * the side effects - did anything change outside ``root/``, or does a path
    the probe declares absent exist?

Verdicts: HELD (declared outcome, no side effects), BYPASSED (any side effect
outside the workspace or on an absent path, whatever the outcome), FAILED
(clean, but not the declared outcome), ERROR (the runner could not get an
answer), NOT_RUN (this platform cannot set the probe up, e.g. no symlink
rights). Only HELD counts as a pass.
"""

import ast
import copy
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

from .compiler import compile_score
from .presets import render_blueprint
from .schema import validate_score

VERDICTS = ("HELD", "BYPASSED", "FAILED", "ERROR", "NOT_RUN")
THREAT_CLASSES = (
    # Names carried over from the Agent B threat_to_test taxonomy.
    "PATH_TRAVERSAL", "COMMAND_INJECTION", "SQL_INJECTION", "CROSS_SITE_SCRIPTING",
    "SERVER_SIDE_REQUEST_FORGERY", "XML_EXTERNAL_ENTITY", "SERVER_SIDE_TEMPLATE_INJECTION",
    "INSECURE_DIRECT_OBJECT_REFERENCE", "CROSS_SITE_REQUEST_FORGERY", "BRUTE_FORCE",
    "SESSION_HIJACKING", "PRIVILEGE_ESCALATION", "SENSITIVE_DATA_EXPOSURE",
    # Added for Block-Wise.
    "RESOURCE_EXHAUSTION", "INPUT_VALIDATION", "UNSAFE_DESERIALIZATION", "SECRET_EXPOSURE",
)
PROBE_KEYS = {"id", "threat", "function", "args", "raises", "returns", "then_files", "absent", "setup"}
OVER = re.compile(r"^\{over:(\w+)\}$")
TIMEOUT = 10
MAX_OVER = 50_000_000  # largest {over:NAME} text a probe will build

# Runs in the child process: import the generated module by path, call one
# function, and write the outcome to a result file (stdout is left to the code).
_CALL = r"""
import importlib.util, json, sys
job = json.loads(sys.stdin.read())
def finish(result):
    with open(job["result"], "w", encoding="utf-8") as handle:
        json.dump(result, handle)
try:
    spec = importlib.util.spec_from_file_location("probed_block", job["source"])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    function = getattr(module, job["function"])
except Exception as exc:
    finish({"outcome": "harness_error", "detail": f"{type(exc).__name__}: {exc}"})
    sys.exit(0)
try:
    value = function(*job["args"])
except Exception as exc:
    finish({"outcome": "raised", "type": type(exc).__name__, "detail": str(exc)})
else:
    try:
        json.dumps(value)
    except (TypeError, ValueError):
        value = repr(value)
    finish({"outcome": "returned", "value": value})
"""


class ProbeError(ValueError):
    pass


def validate_security(blueprint):
    """Check a block's security section (release gates G2 and G5); return it."""
    security = blueprint.get("security")
    if not isinstance(security, dict):
        raise ProbeError("Block has no security section")
    if not isinstance(security.get("function"), str) or not security["function"].isidentifier():
        raise ProbeError("security.function must name the probed function")
    threats = security.get("threats") or []
    ids = [t.get("id") for t in threats]
    if not threats or len(set(ids)) != len(ids):
        raise ProbeError("security.threats must be a non-empty list with unique ids")
    for threat in threats:
        if threat.get("class") not in THREAT_CLASSES:
            raise ProbeError(f"Threat {threat.get('id')}: unknown class {threat.get('class')!r}")
    probes = security.get("probes") or []
    probe_ids = [p.get("id") for p in probes]
    if len(set(probe_ids)) != len(probe_ids):
        raise ProbeError("Probe ids must be unique")
    for probe in probes:
        extra = set(probe) - PROBE_KEYS
        if extra or "id" not in probe or not isinstance(probe.get("args"), list):
            raise ProbeError(f"Probe {probe.get('id')}: needs id and args, unknown keys {sorted(extra)}")
        if probe.get("threat") is not None and probe["threat"] not in ids:
            raise ProbeError(f"Probe {probe['id']} names undeclared threat {probe['threat']!r}")
        if "function" in probe and not (isinstance(probe["function"], str) and probe["function"].isidentifier()):
            raise ProbeError(f"Probe {probe['id']}: function must be a name")
        if ("raises" in probe) == ("returns" in probe):
            raise ProbeError(f"Probe {probe['id']} must declare exactly one of raises / returns")
    if not any(p.get("threat") is None and "returns" in p for p in probes):
        raise ProbeError("At least one functional probe (threat null, returns) is required")
    unprobed = set(ids) - {p.get("threat") for p in probes}
    if unprobed:
        raise ProbeError(f"Threats without a probe: {sorted(unprobed)}")
    declared = security.get("params")
    if not isinstance(declared, dict) or set(declared) != set(blueprint.get("params", {})):
        raise ProbeError('security.params must declare every blueprint parameter as "free" or {min, max}')
    for name, bound in declared.items():
        if bound == "free":
            continue
        if not (isinstance(bound, dict) and set(bound) == {"min", "max"} and _number(bound["min"]) is not None
                and _number(bound["max"]) is not None and bound["min"] <= bound["max"]):
            raise ProbeError(f'security.params.{name} must be "free" or {{min, max}} numbers')
        if param_violations(security, {name: blueprint["params"][name].get("default")}):
            raise ProbeError(f"The default of {name} is outside its reviewed range")
    not_verified = security.get("not_verified")
    if not isinstance(not_verified, list) or not not_verified:
        raise ProbeError("security.not_verified must list what the probes do not cover")
    return security


def _number(value):
    """A parameter value as a number (CLI values arrive as text), or None."""
    if isinstance(value, str):
        try:
            value = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return None
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def param_violations(security, values):
    """Parameters whose value is outside the range the security review covered."""
    problems = []
    for name, bound in security.get("params", {}).items():
        if bound == "free" or name not in values:
            continue
        number = _number(values[name])
        if number is None or not bound["min"] <= number <= bound["max"]:
            problems.append(f"{name}={values[name]!r} is outside the reviewed range [{bound['min']}, {bound['max']}]")
    return problems


def default_params(blueprint):
    return {name: spec.get("default") for name, spec in blueprint.get("params", {}).items()}


def _snapshot(base):
    """Map every path under base, except the root/ workspace, to its content digest."""
    state = {}
    for folder, dirs, files in os.walk(base, followlinks=False):
        here = Path(folder)
        if here == base:
            dirs[:] = [d for d in dirs if d != "root"]
        for name in dirs + files:
            path = here / name
            key = path.relative_to(base).as_posix()
            if path.is_symlink():
                state[key] = "link:" + os.readlink(path)
            elif path.is_file():
                state[key] = hashlib.sha256(path.read_bytes()).hexdigest()
            else:
                state[key] = "dir"
    return state


def _fill(value, places, params):
    if isinstance(value, str):
        over = OVER.match(value)
        if over:
            # Text one character over a size parameter, e.g. {over:max_bytes}.
            size = int(_number(params[over.group(1)])) + 1
            if size > MAX_OVER:
                raise ProbeError(f"{over.group(1)} is too large to probe")
            return "x" * max(0, size)
        for name, path in places.items():
            value = value.replace("{" + name + "}", path)
        return value
    if isinstance(value, list):
        return [_fill(item, places, params) for item in value]
    return value


def _call(source, function, args, result_file, cwd, timeout):
    job = json.dumps({"source": str(source), "function": function, "args": args, "result": str(result_file)})
    env = {key: os.environ[key] for key in ("SYSTEMROOT", "PATH") if key in os.environ}
    try:
        subprocess.run([sys.executable, "-I", "-B", "-c", _CALL], input=job, cwd=cwd, env=env, text=True,
                       capture_output=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return {"outcome": "timeout"}
    try:
        return json.loads(result_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"outcome": "harness_error", "detail": "no result from the probe process"}


def _verdict(probe, outcome, root, dirty):
    absent = [p for p in probe.get("absent", []) if (root / p).exists() or (root / p).is_symlink()]
    if dirty or absent:
        return "BYPASSED", f"side effects outside the workspace: {dirty}" if dirty else f"must not exist: {absent}"
    kind = outcome.get("outcome")
    if kind not in ("raised", "returned"):
        return "ERROR", outcome.get("detail", kind)
    if "raises" in probe:
        if kind == "raised" and outcome["type"] == probe["raises"]:
            return "HELD", f"raised {outcome['type']}: {outcome['detail']}"
        got = f"raised {outcome['type']}" if kind == "raised" else f"returned {outcome['value']!r}"
        return "FAILED", f"expected {probe['raises']}, {got}"
    if kind != "returned" or outcome["value"] != probe["returns"]:
        got = f"raised {outcome['type']}: {outcome['detail']}" if kind == "raised" else f"returned {outcome['value']!r}"
        return "FAILED", f"expected return {probe['returns']!r}, {got}"
    for name, content in probe.get("then_files", {}).items():
        target = root / name
        if not target.is_file() or target.read_text(encoding="utf-8") != content:
            return "FAILED", f"expected {name} to contain {content!r}"
    return "HELD", "returned as declared"


def run_probe(source, function, probe, timeout=TIMEOUT, params=None):
    """Run one probe against the generated module at `source`; return its result.

    `params` are the values the module was generated with, for {over:NAME}.
    """
    function = probe.get("function", function)
    result = {"id": probe["id"], "threat": probe.get("threat")}
    base = Path(tempfile.mkdtemp(prefix="bw_probe_")).resolve()
    try:
        root, outside = base / "root", base / "outside"
        root.mkdir()
        outside.mkdir()
        (outside / "SENTINEL.txt").write_text("must not change", encoding="utf-8")
        setup = probe.get("setup", {})
        for folder in setup.get("dirs", []):
            (base / folder).mkdir(parents=True, exist_ok=True)
        for link, target in setup.get("symlinks", {}).items():
            try:
                os.symlink(base / target, base / link, target_is_directory=(base / target).is_dir())
            except (OSError, NotImplementedError) as exc:
                return {**result, "verdict": "NOT_RUN", "detail": f"cannot create symlink here: {exc}"}
        places = {"root": str(root), "outside": str(outside), "base": str(base)}
        before = _snapshot(base)
        scratch = Path(tempfile.mkdtemp(prefix="bw_probe_result_"))
        try:
            args = _fill(probe["args"], places, params or {})
            outcome = _call(source, function, args, scratch / "result.json", root, timeout)
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
        after = _snapshot(base)
        dirty = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        verdict, detail = _verdict(probe, outcome, root, dirty)
        return {**result, "verdict": verdict, "detail": detail}
    finally:
        shutil.rmtree(base, ignore_errors=True)


def run_probes(source, security, timeout=TIMEOUT, params=None):
    """Run every probe in a validated security section against one generated module."""
    return [run_probe(source, security["function"], probe, timeout, params) for probe in security["probes"]]


def canonical_digest(value):
    body = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()


def _mutate(plan, replace):
    """Return a copy of a rendered plan with the named functions' bodies swapped."""
    plan = copy.deepcopy(plan)
    found = set()
    for module in plan["modules"]:
        for function in module.get("functions", []):
            if function["name"] in replace:
                function["body"] = replace[function["name"]]
                found.add(function["name"])
    if found != set(replace):
        raise ProbeError(f"Mutant names unknown functions: {sorted(set(replace) - found)}")
    return validate_score(plan)


def _probe_plan(plan, security, timeout, params):
    """Compile a plan into a scratch folder and probe its first module."""
    folder = Path(tempfile.mkdtemp(prefix="bw_probe_code_"))
    try:
        sources = compile_score(plan)
        for path, source in sources.items():
            (folder / path).parent.mkdir(parents=True, exist_ok=True)
            (folder / path).write_text(source, encoding="utf-8")
        return run_probes(folder / next(iter(sources)), security, timeout, params)
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def detector_check(blueprint, suite, timeout=TIMEOUT):
    """Release gate G4: the probes must pass the real block and catch every mutant.

    A mutant is killed when at least one probe that ran says BYPASSED or FAILED
    (ERROR and NOT_RUN do not count as detection), and every probe it lists in
    ``caught_by`` that ran on this platform caught it.
    """
    security = validate_security(blueprint)
    if suite.get("block") != blueprint["id"]:
        raise ProbeError(f"Mutant suite is for {suite.get('block')!r}, not {blueprint['id']!r}")
    plan, params = render_blueprint(blueprint), default_params(blueprint)
    real = _probe_plan(plan, security, timeout, params)
    mutants = []
    for mutant in suite["mutants"]:
        results = _probe_plan(_mutate(plan, mutant["replace"]), security, timeout, params)
        verdicts = {r["id"]: r["verdict"] for r in results}
        caught = sorted(probe for probe, verdict in verdicts.items() if verdict in ("BYPASSED", "FAILED"))
        expected_missed = sorted(p for p in mutant.get("caught_by", [])
                                 if verdicts.get(p) not in ("BYPASSED", "FAILED", "NOT_RUN"))
        mutants.append({"id": mutant["id"], "weakness": mutant["weakness"], "killed": bool(caught) and not expected_missed,
                        "caught_by": caught, "expected_but_missed": expected_missed})
    killed = sum(m["killed"] for m in mutants)
    real_summary = summarize(real)
    return {"ok": real_summary["status"] != "not-held" and killed == len(mutants) and bool(mutants),
            "real_block": real_summary, "real_results": real, "mutants": mutants,
            "killed": killed, "total": len(mutants), "suite": canonical_digest(suite)}


def review_record(blueprint, suite, timeout=TIMEOUT):
    """Run the detector check and return the record a person may commit to approved.json.

    Nothing here writes the manifest: approval stays a human-reviewed commit
    (release gate G7). The record is only "ok" when every probe actually ran and
    held, so a review from a platform that skips probes is not enough.
    """
    report = detector_check(blueprint, suite, timeout)
    record = {"block_version": canonical_digest(blueprint), "real_block": report["real_block"]["status"],
              "killed": report["killed"], "total": report["total"], "mutant_suite": report["suite"],
              "params": default_params(blueprint),
              "platform": sys.platform, "python": platform.python_version(), "date": date.today().isoformat()}
    not_held = [r for r in report["real_results"] if r["verdict"] != "HELD"]
    return {"ok": report["ok"] and record["real_block"] == "held", "block": blueprint["id"], "record": record,
            "mutants": report["mutants"], "not_held": not_held}


def summarize(results):
    """Counts per verdict plus an overall probe status (fail closed: only all-HELD is 'held')."""
    counts = {verdict: sum(r["verdict"] == verdict for r in results) for verdict in VERDICTS}
    if not results or counts["BYPASSED"] or counts["FAILED"] or counts["ERROR"]:
        status = "not-held"
    elif counts["NOT_RUN"]:
        status = "held-with-gaps"
    else:
        status = "held"
    return {"status": status, **counts}
