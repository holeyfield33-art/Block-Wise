"""Apply presets to a real project and check it against the accumulated plan.

The plan lives in <project>/.blockwise/plan.json. Each applied preset adds one
function to the plan and writes its generated source into the target file.
The agent never needs to read the plan: results come back as one short line.
"""

import ast
import json
from pathlib import Path

from .compiler import compile_score
from .conformance import compare_score
from .presets import PresetError, get_preset, render
from .schema import FORMAT, module_path, validate_score

PLAN_DIR = ".blockwise"
PLAN_FILE = "plan.json"
# Issue kinds ignored by the default (lenient) check: files and functions the plan does not mention.
LENIENT_IGNORED = {"unexpected_file", "unexpected_function", "unexpected_top_level", "imports_changed"}


def plan_path(project):
    return Path(project) / PLAN_DIR / PLAN_FILE


def load_plan(project):
    path = plan_path(project)
    if not path.exists():
        return {"format": FORMAT, "title": "Blockwise plan", "requirements": [], "modules": []}
    return validate_score(json.loads(path.read_text(encoding="utf-8")))


def save_plan(project, plan):
    path = plan_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")


def function_source(function, imports):
    """Compile one function (with its imports) through the full grammar and return source parts."""
    plan = validate_score({"format": FORMAT, "modules": [{"path": "m.py", "imports": imports, "functions": [function]}]})
    tree = ast.parse(compile_score(plan)["m.py"])
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef))
    return ast.unparse(node) + "\n", [ast.unparse(ast.parse(i).body[0]) for i in plan["modules"][0]["imports"]]


def insert_imports(source, imports):
    """Add missing import lines after the module docstring and existing imports."""
    tree = ast.parse(source) if source.strip() else ast.Module(body=[], type_ignores=[])
    present = {ast.unparse(n) for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))}
    missing = [i for i in imports if i not in present]
    if not missing:
        return source
    lines = source.splitlines(keepends=True)
    after = 0
    for node in tree.body:
        is_docstring = isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
        if isinstance(node, (ast.Import, ast.ImportFrom)) or (is_docstring and node is tree.body[0]):
            after = node.end_lineno
        else:
            break
    return "".join(lines[:after]) + "".join(i + "\n" for i in missing) + "".join(lines[after:])


def apply_preset(project, preset_id, into, params=None):
    """Add a preset function to file `into` (relative to project) and record it in the plan."""
    project = Path(project)
    module_path(into)
    preset = get_preset(preset_id)
    function, imports = render(preset, params)
    source_text, import_lines = function_source(function, imports)
    target = project / into
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    if existing:
        try:
            names = {n.name for n in ast.parse(existing).body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        except SyntaxError as exc:
            raise PresetError(f"{into} does not parse; fix it before applying presets ({exc.msg}, line {exc.lineno})") from None
        if function["name"] in names:
            raise PresetError(f"{into} already defines {function['name']}(); choose another function name")
    plan = load_plan(project)
    module = next((m for m in plan["modules"] if m["path"] == into), None)
    if module is None:
        module = {"path": into, "imports": [], "functions": []}
        plan["modules"].append(module)
    module["imports"] += [i for i in import_lines if i not in module["imports"]]
    module["functions"].append(function)
    plan = validate_score(plan)
    new_source = insert_imports(existing, import_lines)
    if new_source and not new_source.endswith("\n"):
        new_source += "\n"
    new_source += ("\n\n" if new_source.strip() else "") + source_text
    compile(new_source, into, "exec")  # never write a file that does not parse
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(new_source, encoding="utf-8")
    save_plan(project, plan)
    todos = [{"label": node["label"], "allowed_calls": node["allowed_calls"]}
             for node in walk(function["body"]) if node["kind"] == "hole"]
    result = {"ok": True, "added": f"{into}:{function['name']}", "preset": preset_id}
    if todos:
        result["todo"] = todos
    return result


def walk(body):
    for node in body:
        yield node
        for key in ("body", "otherwise", "handler", "finally"):
            yield from walk(node.get(key, []))


def check_project(project, strict=False):
    """Compare the project with its plan. Lenient mode only checks planned functions and imports."""
    project = Path(project)
    plan = load_plan(project)
    if not plan["modules"]:
        return {"ok": True, "checked_functions": 0, "issues": [], "note": "No plan yet; apply a preset first."}
    report = compare_score(plan, project)
    issues = report["issues"]
    if not strict:
        issues = [i for i in issues if i["kind"] not in LENIENT_IGNORED]
        for module in plan["modules"]:
            path = project / module["path"]
            if path.exists():
                try:
                    present = {ast.unparse(n) for n in ast.parse(path.read_text(encoding="utf-8")).body
                               if isinstance(n, (ast.Import, ast.ImportFrom))}
                except SyntaxError:
                    continue
                wanted = {ast.unparse(ast.parse(i).body[0]) for i in module["imports"]}
                if wanted - present:
                    issues.append({"path": module["path"], "function": None, "kind": "imports_missing",
                                   "message": "Planned imports are missing", "expected": sorted(wanted - present),
                                   "actual": sorted(present)})
    compact = [{"file": i["path"], "function": i["function"], "problem": i["kind"], "detail": i["message"]}
               for i in issues]
    return {"ok": not compact, "checked_functions": sum(len(m["functions"]) for m in plan["modules"]),
            "issues": compact, "mode": "strict" if strict else "lenient",
            "note": "Structure only: run your tests for behavior."}
