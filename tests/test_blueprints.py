"""Blueprints: whole-file templates. The to-do app is generated, run as a real program, and checked."""

import contextlib
import functools
import http.server
import json
import os
import subprocess
import sys
import threading

import pytest

from blockwise.cli import main
from blockwise.compiler import compile_score
from blockwise.coverage import unsupported
from blockwise.presets import PresetError, find, load_blueprints, render_blueprint
from blockwise.project import apply_preset, check_project

BLUEPRINTS = load_blueprints()


def run(folder, script, argv):
    # Local test servers only: never route 127.0.0.1 through a proxy from the environment.
    env = {**os.environ, "NO_PROXY": "127.0.0.1,localhost", "no_proxy": "127.0.0.1,localhost", "PYTHONIOENCODING": "utf-8"}
    return subprocess.run([sys.executable, script, *argv], cwd=folder, capture_output=True, text=True, timeout=30,
                          check=False, env=env)


@contextlib.contextmanager
def local_server(folder):
    """Serve `folder` over HTTP on 127.0.0.1 for examples that use {server}; no internet needed."""
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(folder)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.parametrize("blueprint_id", sorted(BLUEPRINTS))
def test_blueprint_examples_run_as_real_programs(blueprint_id, tmp_path):
    blueprint = BLUEPRINTS[blueprint_id]
    sources = compile_score(render_blueprint(blueprint))
    for path, source in sources.items():
        assert unsupported(source) == [], path
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding="utf-8")
    script = next(iter(sources))
    assert blueprint["examples"], "blueprints need runnable examples"
    with local_server(tmp_path) as server:
        for example in blueprint["examples"]:  # examples run in order, sharing the folder (and any saved data)
            for name, content in example.get("files", {}).items():  # input files the example needs
                (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
                (tmp_path / name).write_text(content, encoding="utf-8", newline="")
            argv = [arg.replace("{server}", server) for arg in example["argv"]]
            result = run(tmp_path, script, argv)
            assert (result.stdout, result.returncode) == (example["stdout"], example["exit"]), (argv, result.stderr)


def test_parameters_rename_file_and_store(tmp_path):
    sources = compile_score(render_blueprint(BLUEPRINTS["todo_cli"], {"file": "tasks", "store": "my tasks.json"}))
    assert list(sources) == ["tasks.py"]
    (tmp_path / "tasks.py").write_text(sources["tasks.py"], encoding="utf-8")
    assert run(tmp_path, "tasks.py", ["add", "x"]).stdout == "Added.\n"
    assert json.loads((tmp_path / "my tasks.json").read_text(encoding="utf-8")) == [{"text": "x", "done": False}]
    assert "usage: tasks.py" in run(tmp_path, "tasks.py", ["?"]).stdout
    with pytest.raises(PresetError):
        render_blueprint(BLUEPRINTS["todo_cli"], {"file": "bad name"})


def test_apply_writes_files_records_plan_and_checks(tmp_path):
    result = apply_preset(tmp_path, "todo_cli", "tools")
    assert result == {"ok": True, "added": ["tools/todo.py"], "blueprint": "todo_cli", "try": "python tools/todo.py add buy milk"}
    assert check_project(tmp_path)["ok"]
    with pytest.raises(PresetError, match="already exists"):
        apply_preset(tmp_path, "todo_cli", "tools")
    target = tmp_path / "tools" / "todo.py"
    target.write_text(target.read_text(encoding="utf-8").replace("sys.exit(main(sys.argv[1:]))", "main(sys.argv[1:])"), encoding="utf-8")
    report = check_project(tmp_path)
    assert not report["ok"] and report["issues"][0]["problem"] == "entry_changed"


def test_agents_find_and_list_blueprints(capsys):
    assert find("todo list command line app")[0]["id"] == "todo_cli"
    assert main(["list", "--category", "blueprint"]) == 0
    rows = {row["id"]: row for row in json.loads(capsys.readouterr().out)}
    assert rows["todo_cli"]["files"] == ["todo.py"] and set(rows) == set(BLUEPRINTS)
    for query, expected in [("csv report group total", "csv_report"), ("key value store settings", "kv_store"),
                            ("log file errors summary", "log_stats"), ("organize files into folders", "file_organizer"),
                            ("sort downloads by type", "file_organizer"), ("validate csv emails", "data_validator"),
                            ("fetch json from url", "fetch_json"), ("password strength", "password_problems")]:
        assert find(query)[0]["id"] == expected, query
    assert main(["show", "todo_cli", "--set", "file=tasks"]) == 0
    assert "# --- tasks.py ---" in capsys.readouterr().out


def test_studio_harness_runs_a_file_with_arguments_and_keeps_its_data(tmp_path):
    from test_studio import HARNESS

    files = {p: s for p, s in compile_score(render_blueprint(BLUEPRINTS["todo_cli"])).items()}

    def go(argv, **extra):
        scope = {"REQ": json.dumps({"files": files, "run": "todo.py", "argv": argv, "root": str(tmp_path), **extra})}
        exec(compile(HARNESS, "pyHarness", "exec"), scope)
        return json.loads(scope["RESULT"])

    assert (go(["add", "milk"])["output"], go(["list"])["output"]) == ("Added.\n", "1. [ ] milk\n")
    assert go(["fly"])["exit"] == 2
    assert go(["list"], reset=True)["output"] == "Nothing to do.\n"


def test_main_block_grammar(tmp_path):
    from blockwise.schema import FORMAT, ScoreError, validate_score

    def plan(entry, functions=None):
        module = {"path": "app.py", "imports": ["import sys"], "functions": functions or [], "entry": entry}
        return {"format": FORMAT, "modules": [module]}

    only_entry = compile_score(plan([{"kind": "call", "expression": "print('hi')"}]))["app.py"]
    assert only_entry.endswith("import sys\n\n\nif __name__ == '__main__':\n    print('hi')\n")
    assert compile_score(plan([]))["app.py"].endswith("if __name__ == '__main__':\n    pass\n")
    with pytest.raises(ScoreError, match="return only works inside a function"):
        validate_score(plan([{"kind": "branch", "condition": "x", "body": [{"kind": "return", "expression": "1"}]}]))
    with pytest.raises(ScoreError, match="functions"):
        validate_score({"format": FORMAT, "modules": [{"path": "a.py", "functions": []}]})
    assert unsupported(only_entry) == [] and unsupported("if __name__ == '__main__':\n    main()\nelse:\n    pass") != []


def test_mcp_show_and_apply_blueprint(tmp_path):
    from blockwise import mcp_server

    assert "# --- todo.py ---" in mcp_server.show_preset("todo_cli")
    assert mcp_server.apply_preset("todo_cli", ".", {"file": "tasks"}, str(tmp_path))["added"] == ["tasks.py"]
    assert mcp_server.check_project(str(tmp_path))["ok"] is True


def test_every_blueprint_fits_in_one_project(tmp_path):
    # Experiment 003 hit "Score exceeds 256 body elements" on the 7th blueprint: the cap
    # was per plan. It is per module now, so a project can hold all of them.
    from blockwise.project import apply_blueprint

    for blueprint_id in sorted(BLUEPRINTS):
        assert apply_blueprint(tmp_path, blueprint_id)["ok"], blueprint_id
    assert check_project(tmp_path)["ok"]


def test_one_module_is_still_capped():
    from blockwise.schema import MAX_NODES, ScoreError, validate_score

    calls = [{"kind": "call", "expression": "print(1)"}] * (MAX_NODES + 1)
    plan = {"format": "blockwise-plan-v1", "modules": [{"path": "m.py", "functions": [
        {"name": "f", "parameters": [], "returns": "None", "body": calls}]}]}
    with pytest.raises(ScoreError):
        validate_score(plan)
