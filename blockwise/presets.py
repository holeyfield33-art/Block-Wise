"""Preset library: small, parameterised, pre-tested function plans.

A preset is a plan for ONE function with {{param}} placeholders. Rendering
validates every parameter by kind, substitutes it, and then runs the full plan
grammar validation, so a bad parameter can never produce unparsed code.
"""

import ast
import json
import keyword
import re
from importlib import resources

from .schema import FORMAT, ScoreError, annotation, expression, identifier, validate_score

PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")
PARAM_KINDS = ("identifier", "module", "annotation", "expression", "string", "string_list", "number", "text")


class PresetError(ValueError):
    pass


def load_presets():
    """Return {preset_id: preset} from every JSON file shipped in blockwise/library/."""
    presets = {}
    for entry in sorted(resources.files("blockwise.library").iterdir(), key=lambda e: e.name):
        if not entry.name.endswith(".json"):
            continue
        for preset in json.loads(entry.read_text(encoding="utf-8")):
            if preset["id"] in presets:
                raise PresetError(f"Duplicate preset id: {preset['id']}")
            presets[preset["id"]] = preset
    return presets


def load_blueprints():
    """Return {blueprint_id: blueprint}: whole-file templates (several functions, often a main block)."""
    blueprints = {}
    folder = resources.files("blockwise.library").joinpath("blueprints")
    for entry in sorted(folder.iterdir(), key=lambda e: e.name):
        if entry.name.endswith(".json"):
            blueprint = json.loads(entry.read_text(encoding="utf-8"))
            blueprints[blueprint["id"]] = blueprint
    return blueprints


def load_all():
    """Presets and blueprints together, for search and listing."""
    presets, blueprints = load_presets(), load_blueprints()
    clash = set(presets) & set(blueprints)
    if clash:
        raise PresetError(f"Preset and blueprint ids collide: {sorted(clash)}")
    return {**presets, **blueprints}


def is_blueprint(template):
    return "plan" in template


def get_preset(preset_id):
    presets = load_presets()
    if preset_id not in presets:
        raise PresetError(f"Unknown preset '{preset_id}'. Run 'blockwise list' to see available presets.")
    return presets[preset_id]


def render_value(name, spec, value):
    """Turn a user-supplied parameter into the exact source text placed in the plan."""
    kind = spec["kind"]
    label = f"Parameter '{name}'"
    if kind == "identifier":
        if not isinstance(value, str):
            raise PresetError(f"{label} must be a name")
        return identifier(value, label)
    if kind == "module":
        if not isinstance(value, str) or not value or not all(part.isidentifier() and not keyword.iskeyword(part)
                                                               for part in value.split(".")):
            raise PresetError(f"{label} must be a module path like checks or shop.checks")
        return value
    if kind == "annotation":
        return annotation(str(value), label)
    if kind == "expression":
        expression(str(value), label)
        return str(value)
    if kind == "string":
        return repr(str(value))
    if kind == "string_list":
        items = value.split(",") if isinstance(value, str) else value
        if not isinstance(items, list) or not items or not all(isinstance(i, str) and i.strip() for i in items):
            raise PresetError(f"{label} must be a non-empty list of text values")
        return repr(tuple(i.strip() for i in items))
    if kind == "number":
        number = value
        if isinstance(value, str):
            try:
                number = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                raise PresetError(f"{label} must be a number") from None
        if isinstance(number, bool) or not isinstance(number, (int, float)):
            raise PresetError(f"{label} must be a number")
        return repr(number)
    if kind == "text":
        text = str(value)
        if not text.strip() or len(text) > 400 or "{{" in text:
            raise PresetError(f"{label} must be short plain text")
        return text
    raise PresetError(f"Unknown parameter kind '{kind}'")


def substitute(node, values):
    if isinstance(node, str):
        return PLACEHOLDER.sub(lambda m: values[m.group(1)], node)
    if isinstance(node, list):
        return [substitute(item, values) for item in node]
    if isinstance(node, dict):
        return {key: substitute(item, values) for key, item in node.items()}
    return node


def _values(preset, params):
    params = dict(params or {})
    unknown = set(params) - set(preset["params"])
    if unknown:
        raise PresetError(f"Unknown parameter(s) {sorted(unknown)}; expected {sorted(preset['params'])}")
    values = {}
    for name, spec in preset["params"].items():
        raw = params.get(name, spec.get("default"))
        if raw is None:
            raise PresetError(f"Parameter '{name}' is required")
        try:
            values[name] = render_value(name, spec, raw)
        except ScoreError as exc:
            raise PresetError(str(exc)) from None
    return values


def render(preset, params=None):
    """Return (function_plan, imports) for a preset with the given parameter values."""
    values = _values(preset, params)
    function = substitute(preset["function"], values)
    names = [p["name"] for p in function["parameters"]] + [function["name"]]
    if len(set(names)) != len(names) or any(keyword.iskeyword(n) for n in names):
        raise PresetError("Parameter names must be distinct from each other and from the function name")
    imports = substitute(preset.get("imports", []), values)
    return function, imports


def render_blueprint(blueprint, params=None):
    """Return the validated plan (all modules) for a blueprint with the given parameter values."""
    plan = substitute(blueprint["plan"], _values(blueprint, params))
    try:
        return validate_score({"format": FORMAT, "title": blueprint["title"], **plan})
    except ScoreError as exc:
        raise PresetError(str(exc)) from None


def find(query, limit=3):
    """Best-matching presets for a few words, so an agent need not read the whole list."""
    words = set(re.findall(r"[a-z0-9]+", query.lower()))
    scored = []
    for preset in load_all().values():
        defaults = json.dumps([spec.get("default") for spec in preset["params"].values()])
        haystack = set(re.findall(r"[a-z0-9]+", " ".join((preset["id"], preset["title"], preset["summary"],
                                                           preset["category"], defaults)).lower().replace("_", " ")))
        # Prefix match lets "neg" find "negative" and "role" find "roles".
        score = sum(any(h.startswith(w) or w.startswith(h) and len(h) > 3 for h in haystack) for w in words)
        if score:
            scored.append((-score, preset["id"], preset))
    return [summary(p) for _, _, p in sorted(scored)[:limit]]


def summary(preset):
    """One compact line per preset, sized for an agent's context window."""
    params = ", ".join(f"{name}={json.dumps(spec.get('default'))}" for name, spec in preset["params"].items())
    row = {"id": preset["id"], "category": preset["category"], "does": preset["summary"], "params": params}
    if is_blueprint(preset):
        row["files"] = [m["path"] for m in render_blueprint(preset)["modules"]]
    return row
