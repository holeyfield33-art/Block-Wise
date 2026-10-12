"""Bounded plan grammar. Adapted from Sonic Code Studio; the plan JSON is authoritative."""

import ast
import copy
import json
import keyword
from pathlib import Path, PurePosixPath

FORMAT = "blockwise-plan-v1"
# Scores exported by Sonic Code Studio use the same grammar and remain accepted.
LEGACY_FORMATS = ("sonic-template-v1",)
NOTES = {"function": 60, "validate": 62, "branch": 64, "loop": 65,
         "call": 67, "raise": 69, "return": 71, "hole": 72, "assign": 74, "try": 76, "with": 77}
# Nested statement lists, by element kind.
CHILDREN = {"branch": ("body", "otherwise"), "loop": ("body",), "try": ("body", "handler", "finally"), "with": ("body",)}
MAX_NODES = 256
MAX_DEPTH = 16


class ScoreError(ValueError):
    pass


def keys(value, allowed, required, label):
    if not isinstance(value, dict):
        raise ScoreError(f"{label} must be an object")
    missing, extra = set(required) - set(value), set(value) - set(allowed)
    if missing or extra:
        raise ScoreError(f"{label}: missing {sorted(missing)}, unknown {sorted(extra)}")


def text(value, label, maximum=2000):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum or "\0" in value:
        raise ScoreError(f"{label} must be nonempty text, at most {maximum} characters")
    return value


def identifier(value, label):
    text(value, label, 128)
    if not value.isidentifier() or keyword.iskeyword(value):
        raise ScoreError(f"{label} must be a Python identifier")
    return value


def expression(value, label):
    text(value, label)
    try:
        return ast.parse(value, mode="eval").body
    except (SyntaxError, ValueError, RecursionError):
        raise ScoreError(f"Invalid expression in {label}") from None


def annotation(value, label):
    tree = expression(value, label)
    allowed = (ast.Name, ast.Attribute, ast.Subscript, ast.Tuple, ast.List,
               ast.Constant, ast.BinOp, ast.BitOr, ast.Load)
    if any(not isinstance(node, allowed) or isinstance(node, ast.BinOp) and not isinstance(node.op, ast.BitOr)
           for node in ast.walk(tree)):
        raise ScoreError(f"{label} must be a type annotation without calls or executable operations")
    return value


def string_list(value, label, maximum=64):
    if not isinstance(value, list) or len(value) > maximum:
        raise ScoreError(f"{label} must be a list of at most {maximum} strings")
    for item in value:
        text(item, label, 512)
    return value


def module_path(value):
    text(value, "Module path", 256)
    path = PurePosixPath(value)
    if (path.is_absolute() or "\\" in value or ":" in value or path.as_posix() != value
            or any(part in (".", "..") for part in path.parts) or path.suffix != ".py"):
        raise ScoreError("Module paths must be normalized relative .py paths")
    parts = list(path.parts[:-1]) + [path.stem]
    devices = {"CON", "PRN", "AUX", "NUL"} | {f"{prefix}{i}" for prefix in ("COM", "LPT") for i in range(1, 10)}
    for part in parts:
        identifier(part, "Module path component")
        if part.upper() in devices:
            raise ScoreError("Reserved device name in module path")
    return value


def validate_score(score):
    """Reject unknown fields and ambiguous constructs; return a normalized copy."""
    result = copy.deepcopy(score)
    keys(result, {"format", "title", "modules", "requirements"}, {"format", "modules"}, "Score")
    if result["format"] != FORMAT and result["format"] not in LEGACY_FORMATS:
        raise ScoreError("Unsupported template format")
    result.setdefault("title", "Blockwise plan")
    text(result["title"], "Title", 256)
    result.setdefault("requirements", [])
    string_list(result["requirements"], "Score requirements")
    modules = result["modules"]
    if not isinstance(modules, list) or not 1 <= len(modules) <= 32:
        raise ScoreError("Score requires 1 to 32 modules")
    paths, count = set(), [0]

    def nodes(body, depth=0):
        if not isinstance(body, list) or len(body) > MAX_NODES or depth > MAX_DEPTH:
            raise ScoreError("Invalid or excessively nested template body")
        for node in body:
            count[0] += 1
            if count[0] > MAX_NODES:
                raise ScoreError("Score exceeds 256 body elements")
            if (not isinstance(node, dict) or not isinstance(node.get("kind"), str)
                    or node["kind"] not in NOTES or node["kind"] == "function"):
                raise ScoreError("Unknown template element")
            kind = node["kind"]
            fields = {"kind"}
            if kind in ("validate", "call", "return", "raise"):
                fields.add("expression")
            elif kind == "assign":
                fields |= {"target", "expression"}
            elif kind == "branch":
                fields |= {"condition", "body", "otherwise"}
            elif kind == "loop":
                fields |= {"target", "iterable", "body"}
            elif kind == "hole":
                fields |= {"label", "allowed_calls"}
            elif kind == "try":
                fields |= {"body", "exception", "alias", "handler", "finally"}
            elif kind == "with":
                fields |= {"context", "alias", "body"}
            required = fields - {"otherwise", "allowed_calls", "alias", "handler", "finally"}
            keys(node, fields, required, f"{kind} element")
            if "expression" in fields:
                parsed = expression(node["expression"], kind)
                if kind in ("validate", "call") and not isinstance(parsed, ast.Call):
                    raise ScoreError(f"{kind} requires a function call expression")
            if "target" in fields:
                identifier(node["target"], f"{kind} target")
            if kind == "branch":
                expression(node["condition"], "Branch condition")
                node.setdefault("otherwise", [])
                nodes(node["body"], depth + 1)
                nodes(node["otherwise"], depth + 1)
            if kind == "loop":
                expression(node["iterable"], "Loop iterable")
                nodes(node["body"], depth + 1)
            if kind in ("try", "with"):
                node.setdefault("alias", "")
                if node["alias"] != "":
                    identifier(node["alias"], f"{kind} alias")
            if kind == "try":
                parsed = expression(node["exception"], "Exception type")
                if not isinstance(parsed, (ast.Name, ast.Attribute, ast.Tuple)) or isinstance(parsed, ast.Tuple) and (
                        not parsed.elts or not all(isinstance(e, (ast.Name, ast.Attribute)) for e in parsed.elts)):
                    raise ScoreError("Exception type must be a name like ValueError or a tuple of names")
                node.setdefault("handler", [])
                node.setdefault("finally", [])
                for key in CHILDREN["try"]:
                    nodes(node[key], depth + 1)
            if kind == "with":
                expression(node["context"], "With context")
                nodes(node["body"], depth + 1)
            if kind == "hole":
                text(node["label"], "Hole label", 512)
                node.setdefault("allowed_calls", [])
                string_list(node["allowed_calls"], "Hole allowed calls")
                for call in node["allowed_calls"]:
                    if not all(part.isidentifier() and not keyword.iskeyword(part) for part in call.split(".")):
                        raise ScoreError("Allowed calls must be dotted symbol names")

    for module in modules:
        keys(module, {"path", "imports", "constants", "functions"}, {"path", "functions"}, "Module")
        module_path(module["path"])
        if module["path"].casefold() in paths:
            raise ScoreError("Duplicate module path (including case aliases)")
        paths.add(module["path"].casefold())
        module.setdefault("imports", [])
        string_list(module["imports"], "Imports")
        for imported in module["imports"]:
            try:
                parsed = ast.parse(imported)
            except SyntaxError:
                raise ScoreError("Invalid import") from None
            if (len(parsed.body) != 1 or not isinstance(parsed.body[0], (ast.Import, ast.ImportFrom))
                    or any(alias.name == "*" for alias in parsed.body[0].names)):
                raise ScoreError("Each import must be one explicit import statement")
        module.setdefault("constants", [])
        if not isinstance(module["constants"], list) or len(module["constants"]) > 64:
            raise ScoreError("Constants must be a list of at most 64 elements")
        top_names = set()
        for constant in module["constants"]:
            keys(constant, {"name", "value"}, {"name", "value"}, "Constant")
            identifier(constant["name"], "Constant name")
            expression(constant["value"], "Constant value")
            if constant["name"] in top_names:
                raise ScoreError("Duplicate constant name")
            top_names.add(constant["name"])
        if not isinstance(module["functions"], list) or not 1 <= len(module["functions"]) <= 32:
            raise ScoreError("Each module requires 1 to 32 functions")
        names = set()
        for function in module["functions"]:
            keys(function, {"name", "parameters", "returns", "requirements", "body"},
                 {"name", "parameters", "body"}, "Function")
            identifier(function["name"], "Function name")
            if function["name"] in names or function["name"] in top_names:
                raise ScoreError("Duplicate function name (or a constant with the same name)")
            names.add(function["name"])
            parameters = function["parameters"]
            if not isinstance(parameters, list) or len(parameters) > 32:
                raise ScoreError("Parameters must be a list of at most 32 elements")
            params, seen_default = set(), False
            for parameter in parameters:
                keys(parameter, {"name", "type", "default"}, {"name", "type"}, "Parameter")
                identifier(parameter["name"], "Parameter name")
                annotation(parameter["type"], "Parameter type")
                if "default" in parameter:
                    expression(parameter["default"], "Parameter default")
                    seen_default = True
                elif seen_default:
                    raise ScoreError(f"Parameter '{parameter['name']}' needs a default: it comes after one that has a default")
                if parameter["name"] in params:
                    raise ScoreError("Duplicate parameter name")
                params.add(parameter["name"])
            function.setdefault("returns", "None")
            annotation(function["returns"], "Return type")
            function.setdefault("requirements", [])
            string_list(function["requirements"], "Function requirements")
            nodes(function["body"])
    return result


def load_score(path):
    path = Path(path)
    if path.stat().st_size > 1_000_000:
        raise ScoreError("Score exceeds 1 MB")
    def unique_pairs(pairs):
        result = {}
        for name, value in pairs:
            if name in result:
                raise ScoreError(f"Duplicate JSON field: {name}")
            result[name] = value
        return result
    try:
        return validate_score(json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs))
    except (json.JSONDecodeError, RecursionError) as exc:
        raise ScoreError(f"Invalid score JSON: {type(exc).__name__}") from None


def call_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = call_name(node.value)
        return parent + "." + node.attr if parent else None
    return None
