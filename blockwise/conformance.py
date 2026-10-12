"""Read-only syntactic plan conformance (adapted from Sonic Code Studio). This does not establish behavior."""

import ast
import difflib
import hashlib
import json

from .compiler import HOLE_PREFIX, compile_nodes, compile_score
from .scan import DEFAULT_EXCLUDES, scan
from .schema import call_name, validate_score


def fingerprint(node):
    return ast.dump(node, include_attributes=False) if node is not None else None


def without_docstring(body):
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        return body[1:]
    return body


def is_hole_marker(node):
    return (isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call)
            and call_name(node.exc.func) == "NotImplementedError" and len(node.exc.args) == 1
            and isinstance(node.exc.args[0], ast.Constant) and isinstance(node.exc.args[0].value, str)
            and node.exc.args[0].value.startswith(HOLE_PREFIX))


def allowed_fill(statements, allowed_calls):
    """Holes cannot redefine APIs or bypass later anchors with early control flow."""
    for statement in statements:
        if is_hole_marker(statement):
            continue
        for node in ast.walk(statement):
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
                                 ast.Return, ast.Raise, ast.Break, ast.Continue, ast.Yield, ast.YieldFrom, ast.Global,
                                 ast.Nonlocal, ast.Try, ast.With, ast.AsyncWith, ast.Await)):
                return False
            if isinstance(node, ast.Call) and call_name(node.func) not in allowed_calls:
                return False
    return True


def matches_node(expected, actual):
    kind = expected["kind"]
    if kind == "branch":
        return (isinstance(actual, ast.If) and fingerprint(actual.test) == fingerprint(ast.parse(expected["condition"], mode="eval").body)
                and matches_body(expected["body"], actual.body) and matches_body(expected["otherwise"], actual.orelse))
    if kind == "loop":
        return (isinstance(actual, ast.For) and isinstance(actual.target, ast.Name) and actual.target.id == expected["target"]
                and fingerprint(actual.iter) == fingerprint(ast.parse(expected["iterable"], mode="eval").body)
                and not actual.orelse and matches_body(expected["body"], actual.body))
    return fingerprint(compile_nodes([expected])[0]) == fingerprint(actual)


def matches_body(expected, actual):
    if not expected:
        return not actual or len(actual) == 1 and isinstance(actual[0], ast.Pass)
    # Memoized anchor matching: a hole consumes a bounded statement span.
    memo = {}
    bad_prefixes = {}
    for index, node in enumerate(expected):
        if node["kind"] == "hole":
            allowed = set(node["allowed_calls"])
            prefix = [0]
            for statement in actual:
                prefix.append(prefix[-1] + (not allowed_fill([statement], allowed)))
            bad_prefixes[index] = prefix

    def match(i, j):
        if (i, j) in memo:
            return memo[i, j]
        if i == len(expected):
            result = j == len(actual)
        elif expected[i]["kind"] == "hole":
            prefix = bad_prefixes[i]
            result = any(prefix[end] == prefix[j] and match(i + 1, end)
                         for end in range(j, len(actual) + 1))
        else:
            result = j < len(actual) and matches_node(expected[i], actual[j]) and match(i + 1, j + 1)
        memo[i, j] = result
        return result

    return match(0, 0)


def compare_score(score, repository):
    score = validate_score(score)
    expected_sources = compile_score(score)
    # Reuse the bounded, non-executing scanner; links/read errors fail the operation.
    records = scan(repository, DEFAULT_EXCLUDES)
    actual_files = {record["path"]: record for record in records}
    issues, unresolved = [], []

    def issue(path, function, kind, message, expected=None, actual=None):
        issues.append({"path": path, "function": function, "kind": kind, "message": message,
                       "expected": expected, "actual": actual})

    for path in sorted(set(actual_files) - set(expected_sources)):
        issue(path, None, "unexpected_file", "File is outside the declared template plan")
    for module in score["modules"]:
        path = module["path"]
        if path not in actual_files:
            issue(path, None, "missing_module", "Declared Python module is missing")
            continue
        try:
            source = actual_files[path]["bytes"].decode("utf-8")
            tree = ast.parse(source)
            compile(tree, path, "exec")  # Validate compilation without executing it.
        except (UnicodeError, SyntaxError, ValueError) as exc:
            issue(path, None, "invalid_python", "Cannot compile declared module", actual=str(exc))
            continue
        top = without_docstring(tree.body)
        imports = [node for node in top if isinstance(node, (ast.Import, ast.ImportFrom))]
        wanted_imports = [ast.parse(value).body[0] for value in module["imports"]]
        if [fingerprint(node) for node in imports] != [fingerprint(node) for node in wanted_imports]:
            issue(path, None, "imports_changed", "Import inventory/order differs from the plan",
                  module["imports"], [ast.unparse(node) for node in imports])
        extra_top = [node for node in top if not isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef))]
        for node in extra_top:
            issue(path, getattr(node, "name", None), "unexpected_top_level", "Unplanned top-level statement", actual=ast.unparse(node))
        functions = [node for node in top if isinstance(node, ast.FunctionDef)]
        by_name = {}
        for function in functions:
            if function.name in by_name:
                issue(path, function.name, "duplicate_function", "Function is defined more than once")
            by_name[function.name] = function
        wanted_names = {function["name"] for function in module["functions"]}
        for name in sorted(set(by_name) - wanted_names):
            issue(path, name, "unexpected_function", "Function is not in the declared plan")
        expected_tree = ast.parse(expected_sources[path])
        expected_by_name = {node.name: node for node in expected_tree.body if isinstance(node, ast.FunctionDef)}
        for function in module["functions"]:
            name = function["name"]
            actual = by_name.get(name)
            if actual is None:
                issue(path, name, "missing_function", "Declared function is missing")
                continue
            expected = expected_by_name[name]
            if (fingerprint(actual.args) != fingerprint(expected.args) or fingerprint(actual.returns) != fingerprint(expected.returns)
                    or actual.decorator_list or actual.type_comment):
                issue(path, name, "signature_changed", "Signature or decorators differ from the plan",
                      ast.unparse(expected).splitlines()[0], ast.unparse(actual).splitlines()[0])
            body = without_docstring(actual.body)
            if len(body) > 512 or sum(1 for _ in ast.walk(actual)) > 10000:
                issue(path, name, "implementation_too_large", "Function exceeds template comparison bounds")
                continue
            if not matches_body(function["body"], body):
                difference = "".join(difflib.unified_diff(ast.unparse(expected).splitlines(keepends=True),
                                                         ast.unparse(actual).splitlines(keepends=True),
                                                         fromfile="planned", tofile="observed"))[:16000]
                issue(path, name, "body_changed", "Required structure/order differs, or a hole exceeds its allowed calls/control flow",
                      ast.unparse(expected), difference)
            for node in ast.walk(actual):
                if is_hole_marker(node):
                    label = node.exc.args[0].value[len(HOLE_PREFIX):]
                    unresolved.append({"path": path, "function": name, "label": label})
                    issue(path, name, "unresolved_hole", "Implementation placeholder remains", actual=label)
    encoded = json.dumps(score, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return {"format": "blockwise-check-v1", "compliant": not issues, "issues": issues,
            "unresolved_holes": unresolved, "plan_sha256": hashlib.sha256(encoded).hexdigest(),
            "scope": {"declared_files": list(expected_sources), "excluded_directory_names": list(DEFAULT_EXCLUDES)},
            "limitations": ["This checks Python AST structure against an unsigned plan, not runtime behavior or security.",
                            "Validation/authorization labels do not prove that their called functions enforce those properties.",
                            "Holes allow only listed calls and forbid early return/raise, imports and new definitions.",
                            "Names may be rebound at runtime; matching calls are syntactic, not resolved targets.",
                            "Live scans are not atomic; use a quiescent checkout."]}
