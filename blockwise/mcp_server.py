"""MCP server exposing presets as tools, so agents call them instead of writing boilerplate.

Run with `blockwise mcp` (stdio). Requires the optional dependency: pip install "blockwise[mcp]".
Tool results are deliberately short; the agent never has to read the plan file.
"""

from .compiler import compile_score
from .coverage import check_source
from .coverage import summary as coverage_summary
from .presets import PresetError, find, get_preset, load_all, load_blueprints, render, render_blueprint, summary
from .project import apply_preset as _apply
from .project import check_project as _check
from .project import function_source
from .schema import ScoreError


def list_presets(category: str = "") -> list:
    """List presets and blueprints as {id, category, does, params[, files]}.
    Categories: validation, auth, data, files, blueprint (whole runnable files)."""
    return [summary(p) for p in load_all().values() if not category or p["category"] == category]


def find_presets(query: str) -> list:
    """Return the 3 presets that best match a few words, e.g. "reject negative number". Cheaper than list_presets."""
    return find(query)


def coverage(source: str = "") -> dict:
    """With no source: counts of Python constructs Blockwise can represent. With Python source: whether it
    can become a plan, and which constructs (e.g. while, try, class) have no block yet."""
    if not source:
        return coverage_summary()
    try:
        return check_source(source)
    except SyntaxError as exc:
        return {"ok": False, "error": f"SyntaxError: {exc.msg} (line {exc.lineno})"}


def show_preset(preset: str, params: dict | None = None) -> str:
    """Return the Python a preset would generate with the given params (defaults if omitted)."""
    try:
        if preset in load_blueprints():
            plan = render_blueprint(load_blueprints()[preset], params or {})
            return "\n".join(f"# --- {path} ---\n{source}" for path, source in compile_score(plan).items())
        function, imports = render(get_preset(preset), params or {})
        source, import_lines = function_source(function, imports)
        return "\n".join(import_lines + [source])
    except (PresetError, ScoreError) as exc:
        return f"error: {exc}"


def apply_preset(preset: str, into: str, params: dict | None = None, project: str = ".") -> dict:
    """Add the preset's function to file `into` (path relative to project). Returns a one-line result;
    if the preset has TODOs, the result lists them with the calls each TODO may use."""
    try:
        return _apply(project, preset, into, params or {})
    except (PresetError, ScoreError, OSError, SyntaxError) as exc:
        return {"ok": False, "error": str(exc)}


def check_project(project: str = ".", strict: bool = False) -> dict:
    """Check that planned functions still match their plan (structure only, not behavior)."""
    try:
        return _check(project, strict)
    except (ScoreError, OSError, ValueError) as exc:
        return {"ok": False, "error": str(exc)}


def run():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        raise SystemExit("The MCP server needs the optional dependency: pip install 'blockwise[mcp]'") from None
    server = FastMCP("blockwise")
    for tool in (find_presets, list_presets, show_preset, apply_preset, check_project, coverage):
        server.tool()(tool)
    server.run()
