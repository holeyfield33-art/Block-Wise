"""Python Language Coverage Registry: which Python constructs a Blockwise plan can represent.

The registry (coverage.json) maps each concept to a status (block, expression or planned), an
example, and an official reference. `unsupported()` reads source without running it and reports
which planned concepts it uses, so agents know up front whether code can become a plan.
"""

import ast
import json
from collections import Counter
from importlib import resources

STATUSES = ("block", "expression", "planned")

# Statement node -> registry id, for statements a plan has no way to express.
STATEMENT_GAPS = {
    "While": "while-loop", "Break": "break-continue", "Continue": "break-continue", "Match": "match",
    "AugAssign": "augmented-assign", "AnnAssign": "target-assign", "TryStar": "try-advanced",
    "Assert": "assert", "AsyncWith": "async", "AsyncFor": "async", "AsyncFunctionDef": "async",
    "Global": "global-nonlocal", "Nonlocal": "global-nonlocal", "Delete": "del", "ClassDef": "classes",
    "TypeAlias": "type-aliases",
}


def load_coverage():
    return json.loads(resources.files("blockwise").joinpath("coverage.json").read_text(encoding="utf-8"))


def summary(registry=None):
    """Counts per status plus the planned ids, in one short object."""
    concepts = (registry or load_coverage())["concepts"]
    counts = Counter(c["status"] for c in concepts)
    return {"python": (registry or load_coverage())["python"], "concepts": len(concepts),
            **{s: counts[s] for s in STATUSES}, "planned_ids": [c["id"] for c in concepts if c["status"] == "planned"]}


def _function_gaps(node, gaps):
    args = node.args
    if node.decorator_list:
        gaps.add("decorators")
    if args.vararg or args.kwarg or args.kwonlyargs or args.posonlyargs:
        gaps.add("star-params")
    if getattr(node, "type_params", None):
        gaps.add("type-aliases")
    _body_gaps(node.body, gaps)


def _body_gaps(statements, gaps):
    for node in statements:
        name = type(node).__name__
        if name in STATEMENT_GAPS:
            gaps.add(STATEMENT_GAPS[name])
            if isinstance(node, ast.ClassDef):
                if any("dataclass" in ast.unparse(d) for d in node.decorator_list):
                    gaps.add("dataclasses")
                if any(isinstance(n, ast.FunctionDef) and n.name.startswith("__") and n.name.endswith("__") for n in node.body):
                    gaps.add("dunder-protocols")
        elif isinstance(node, ast.FunctionDef):
            gaps.add("nested-functions")
            _function_gaps(node, gaps)
        elif isinstance(node, ast.Assign) and (len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name)):
            gaps.add("target-assign")
        elif isinstance(node, ast.Raise) and node.cause is not None:
            gaps.add("raise-from")
        elif isinstance(node, ast.Raise) and node.exc is None:
            gaps.add("try-except")
        elif isinstance(node, ast.For):
            if not isinstance(node.target, ast.Name):
                gaps.add("loop-unpacking")
            if node.orelse:
                gaps.add("for-else")
            _body_gaps(node.body, gaps)
        elif isinstance(node, ast.If):
            _body_gaps(node.body, gaps)
            _body_gaps(node.orelse, gaps)
        elif isinstance(node, ast.Try):
            if len(node.handlers) != 1 or node.handlers[0].type is None or node.orelse:
                gaps.add("try-advanced")
            for part in [node.body, node.finalbody, *(h.body for h in node.handlers)]:
                _body_gaps(part, gaps)
        elif isinstance(node, ast.With):
            if len(node.items) != 1 or not isinstance(node.items[0].optional_vars, (ast.Name, type(None))):
                gaps.add("with-advanced")
            _body_gaps(node.body, gaps)
        for child in ast.walk(node):
            if isinstance(child, (ast.Yield, ast.YieldFrom)):
                gaps.add("generators")
            elif isinstance(child, ast.Await):
                gaps.add("async")


def unsupported(source):
    """Return the sorted registry ids of constructs in `source` that a plan cannot represent.

    An empty list means every statement maps onto a block. Raises SyntaxError for invalid Python.
    """
    gaps = set()
    for node in ast.parse(source).body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Pass)):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            continue  # docstring
        if isinstance(node, ast.FunctionDef):
            _function_gaps(node, gaps)
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            _body_gaps([node], gaps)  # a module constant
        elif type(node).__name__ in STATEMENT_GAPS:
            gaps.add(STATEMENT_GAPS[type(node).__name__])
            _body_gaps([node], gaps)
        else:
            gaps.add("module-level-statements")
            _body_gaps([node], gaps)
    return sorted(gaps)


def check_source(source, registry=None):
    """Compact report for agents: can this file become a Blockwise plan, and if not, why not."""
    concepts = {c["id"]: c for c in (registry or load_coverage())["concepts"]}
    gaps = unsupported(source)
    return {"representable": not gaps,
            "unsupported": [{"id": g, "concept": concepts[g]["concept"], **({"tip": concepts[g]["note"]} if "note" in concepts[g] else {})}
                            for g in gaps]}
