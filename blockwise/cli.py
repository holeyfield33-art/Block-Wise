"""Command line: compact JSON output so agents spend as few tokens as possible."""

import argparse
import json
import sys
from pathlib import Path

from .compiler import compile_score, write_project
from .coverage import check_source, load_coverage
from .coverage import summary as coverage_summary
from .presets import PresetError, find, get_preset, is_blueprint, load_all, load_blueprints, render, render_blueprint, summary
from .probes import ProbeError, review_record
from .project import apply_preset, check_project, function_source
from .schema import ScoreError, load_score
from .secure_apply import secure_apply


def parse_sets(pairs):
    params = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise PresetError(f"Use --set name=value (got '{pair}')")
        name, value = pair.split("=", 1)
        params[name.strip()] = value
    return params


def emit(data, pretty):
    print(json.dumps(data, indent=2 if pretty else None, separators=None if pretty else (",", ":")))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="blockwise", description="Preset code blocks for people and agents")
    parser.add_argument("--pretty", action="store_true", help="indent JSON output")
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list", help="list presets (one compact line each)")
    listing.add_argument("--category")
    finder = commands.add_parser("find", help="best 3 presets for a few words (cheaper than list)")
    finder.add_argument("words", nargs="+")
    coverage = commands.add_parser("coverage", help="which Python constructs plans can represent")
    coverage.add_argument("--status", choices=("block", "expression", "planned"))
    coverage.add_argument("--domain")
    coverage.add_argument("--file", type=Path, help="report which constructs in this .py file have no block yet")
    show = commands.add_parser("show", help="preview a preset's generated code")
    show.add_argument("preset")
    show.add_argument("--set", action="append", metavar="NAME=VALUE")
    apply = commands.add_parser("apply", help="add a preset function to a file")
    apply.add_argument("preset")
    apply.add_argument("--into", required=True, help="target file, relative to the project, e.g. app/checks.py")
    apply.add_argument("--set", action="append", metavar="NAME=VALUE")
    apply.add_argument("--project", default=".")
    check = commands.add_parser("check", help="compare the project with its plan (structure only)")
    check.add_argument("--project", default=".")
    check.add_argument("--strict", action="store_true", help="also flag files/functions the plan does not mention")
    secure = commands.add_parser("secure-apply",
                                 help="apply an approved blueprint behind the trust boundary; returns a receipt")
    secure.add_argument("blueprint")
    secure.add_argument("--project", default=".")
    secure.add_argument("--into", default=".", help="target folder, relative to the project")
    secure.add_argument("--set", action="append", metavar="NAME=VALUE")
    secure.add_argument("--probe", action="store_true",
                        help="also run a security block's probes against the written code")
    review = commands.add_parser("security-review",
                                 help="run a security block's probes and mutants; print a review record (writes nothing)")
    review.add_argument("block")
    review.add_argument("--mutants", type=Path, required=True, help="mutant suite JSON, e.g. tests/mutants/BLOCK.json")
    build = commands.add_parser("build", help="generate a project from a plan.json exported by the Studio")
    build.add_argument("plan", type=Path)
    build.add_argument("--out", type=Path, required=True)
    build.add_argument("--audio", action="store_true", help="also render plan.wav (optional extra)")
    export = commands.add_parser("export-presets", help="write the preset library as JS for the Studio page")
    export.add_argument("--out", type=Path, required=True)
    commands.add_parser("mcp", help="run the MCP server (needs: pip install 'blockwise[mcp]')")
    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            rows = [summary(p) for p in load_all().values() if not args.category or p["category"] == args.category]
            emit(rows, args.pretty)
        elif args.command == "find":
            emit(find(" ".join(args.words)), args.pretty)
        elif args.command == "coverage":
            if args.file:
                result = check_source(args.file.read_text(encoding="utf-8"))
                emit(result, args.pretty)
                return 0 if result["representable"] else 1
            if not args.status and not args.domain:
                emit(coverage_summary(), args.pretty)
            else:
                emit([{k: c[k] for k in ("id", "domain", "concept", "status")} for c in load_coverage()["concepts"]
                      if (not args.status or c["status"] == args.status) and (not args.domain or c["domain"] == args.domain)],
                     args.pretty)
        elif args.command == "show" and args.preset in load_blueprints():
            plan = render_blueprint(load_blueprints()[args.preset], parse_sets(args.set))
            for path, source in compile_score(plan).items():
                print(f"# --- {path} ---\n{source}")
        elif args.command == "show":
            preset = get_preset(args.preset)
            function, imports = render(preset, parse_sets(args.set))
            source, import_lines = function_source(function, imports)
            print("\n".join(import_lines + ([""] if import_lines else []) + [source.rstrip()]))
        elif args.command == "apply":
            emit(apply_preset(args.project, args.preset, args.into, parse_sets(args.set)), args.pretty)
        elif args.command == "check":
            result = check_project(args.project, args.strict)
            emit(result, args.pretty)
            return 0 if result["ok"] else 1
        elif args.command == "secure-apply":
            receipt = secure_apply(args.blueprint, args.project, args.into, parse_sets(args.set), probe=args.probe)
            emit(receipt, args.pretty)
            if args.probe:
                return 0 if receipt.get("security", {}).get("status") == "security-reviewed" else 1
            return 0 if receipt["status"] == "approved" else 1
        elif args.command == "security-review":
            blueprints = load_blueprints()
            if args.block not in blueprints:
                raise PresetError(f"Unknown blueprint '{args.block}'")
            result = review_record(blueprints[args.block], json.loads(args.mutants.read_text(encoding="utf-8")))
            emit(result, args.pretty)
            return 0 if result["ok"] else 1
        elif args.command == "build":
            emit(write_project(load_score(args.plan), args.out, audio=args.audio), args.pretty)
        elif args.command == "export-presets":
            data = []
            for preset in load_all().values():
                if is_blueprint(preset):
                    data.append({**preset, "kind": "blueprint", "preview": compile_score(render_blueprint(preset))})
                    continue
                function, imports = render(preset)
                data.append({**preset, "preview": function_source(function, imports)[0]})
            args.out.write_text("// Generated by `blockwise export-presets`. Do not edit by hand.\n"
                                "window.BLOCKWISE_PRESETS = " + json.dumps(data, indent=1) + ";\n", encoding="utf-8")
            emit({"ok": True, "presets": len(data), "out": str(args.out)}, args.pretty)
        elif args.command == "mcp":
            from .mcp_server import run

            run()
        return 0
    except (PresetError, ProbeError, ScoreError, OSError, SyntaxError, json.JSONDecodeError) as exc:
        emit({"ok": False, "error": str(exc)}, args.pretty)
        return 2


def entry():
    sys.exit(main())


# Kept importable for tests that compile plans without the CLI.
__all__ = ["main", "compile_score"]
