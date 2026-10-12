"""Applying presets to a project, the accumulated plan, and the structure check."""

import json

import pytest

from blockwise import mcp_server
from blockwise.cli import main
from blockwise.presets import PresetError
from blockwise.project import apply_preset, check_project, load_plan


def test_apply_creates_file_plan_and_passes_check(tmp_path):
    result = apply_preset(tmp_path, "require_positive", "app/checks.py", {"value": "qty"})
    assert result == {"ok": True, "added": "app/checks.py:require_positive", "preset": "require_positive"}
    source = (tmp_path / "app" / "checks.py").read_text()
    assert "if qty <= 0:" in source
    assert load_plan(tmp_path)["modules"][0]["functions"][0]["name"] == "require_positive"
    assert check_project(tmp_path)["ok"] is True


def test_existing_code_is_kept_and_duplicates_refused(tmp_path):
    target = tmp_path / "orders.py"
    target.write_text('"""Orders."""\nimport math\n\n\ndef helper():\n    return math.pi\n')
    apply_preset(tmp_path, "require_role", "orders.py")
    apply_preset(tmp_path, "sum_field", "orders.py")
    text = target.read_text()
    assert text.startswith('"""Orders."""\nimport math\n') and "def helper" in text
    assert "def require_admin" in text and "def total_price" in text
    with pytest.raises(PresetError, match="already defines"):
        apply_preset(tmp_path, "require_role", "orders.py")
    assert check_project(tmp_path)["ok"] is True
    strict = check_project(tmp_path, strict=True)
    assert not strict["ok"] and {i["problem"] for i in strict["issues"]} >= {"unexpected_function"}


def test_unparseable_target_is_never_overwritten(tmp_path):
    (tmp_path / "broken.py").write_text("def nope(:\n")
    with pytest.raises(PresetError, match="does not parse"):
        apply_preset(tmp_path, "clamp", "broken.py")
    assert (tmp_path / "broken.py").read_text() == "def nope(:\n"


@pytest.mark.parametrize("old,new,problem", [
    ("if amount <= 0:", "if amount < 0:", "body_changed"),
    ("    require_admin(role)\n", "", "body_changed"),
])
def test_check_flags_changes_to_planned_structure(tmp_path, old, new, problem):
    apply_preset(tmp_path, "require_positive", "checks.py")
    apply_preset(tmp_path, "require_role", "checks.py")
    apply_preset(tmp_path, "checked_operation", "ops.py")
    ops = tmp_path / "ops.py"
    ops.write_text(ops.read_text().replace("    raise NotImplementedError('TODO:Set result from the validated value')\n",
                                           "    result = amount * 2\n"))
    for path in (tmp_path / "checks.py", ops):
        path.write_text(path.read_text().replace(old, new))
    result = check_project(tmp_path)
    assert not result["ok"] and problem in {i["problem"] for i in result["issues"]}


def test_todo_preset_reports_todo_until_filled_with_allowed_code(tmp_path):
    result = apply_preset(tmp_path, "checked_operation", "ops.py", {"work": "Double the amount into result"})
    assert result["todo"] == [{"label": "Double the amount into result", "allowed_calls": []}]
    assert {i["problem"] for i in check_project(tmp_path)["issues"]} == {"unresolved_hole"}
    ops = tmp_path / "ops.py"
    marker = "    raise NotImplementedError('TODO:Double the amount into result')\n"
    ops.write_text(ops.read_text().replace(marker, "    result = amount * 2\n"))
    assert check_project(tmp_path)["ok"] is True
    ops.write_text(ops.read_text().replace("    result = amount * 2\n", "    result = eval('amount')\n"))
    assert not check_project(tmp_path)["ok"]


def test_cli_is_compact_and_uses_exit_codes(tmp_path, capsys):
    assert main(["apply", "require_keys", "--into", "api.py", "--project", str(tmp_path), "--set", "keys=user,pass"]) == 0
    line = capsys.readouterr().out.strip()
    assert "\n" not in line and json.loads(line)["ok"] is True
    assert main(["check", "--project", str(tmp_path)]) == 0
    (tmp_path / "api.py").write_text((tmp_path / "api.py").read_text().replace("key not in payload", "False"))
    assert main(["check", "--project", str(tmp_path)]) == 1
    capsys.readouterr()
    assert main(["apply", "nope", "--into", "x.py", "--project", str(tmp_path)]) == 2
    assert "Unknown preset" in capsys.readouterr().out


def test_build_accepts_studio_and_legacy_sonic_plans(tmp_path):
    for fmt in ("blockwise-plan-v1", "sonic-template-v1"):
        plan = tmp_path / f"{fmt}.json"
        plan.write_text(json.dumps({"format": fmt, "modules": [{"path": "m.py", "functions": [
            {"name": "f", "parameters": [], "body": [{"kind": "return", "expression": "1"}]}]}]}))
        assert main(["build", str(plan), "--out", str(tmp_path / fmt)]) == 0
        assert "def f() -> None:" in (tmp_path / fmt / "repo" / "m.py").read_text()


def test_mcp_tools_return_short_results(tmp_path):
    rows = mcp_server.list_presets("auth")
    assert rows and all(set(r) == {"id", "category", "does", "params"} for r in rows)
    assert "def require_active" in mcp_server.show_preset("require_active_user")
    assert mcp_server.apply_preset("clamp", "util.py", {"high": 5}, str(tmp_path))["ok"] is True
    assert mcp_server.check_project(str(tmp_path))["ok"] is True
    assert mcp_server.apply_preset("clamp", "../escape.py", {}, str(tmp_path))["ok"] is False
    assert mcp_server.find_presets("reject negative number")[0]["id"] == "require_positive"
    assert mcp_server.coverage("while x:\n    pass")["unsupported"][0]["id"] == "while-loop"
    assert mcp_server.coverage("def (")["ok"] is False and mcp_server.coverage()["planned"] > 0


def test_checked_operation_imports_its_checks_and_runs(tmp_path):
    apply_preset(tmp_path, "require_positive", "shop/checks.py")
    apply_preset(tmp_path, "require_role", "shop/checks.py")
    apply_preset(tmp_path, "checked_operation", "shop/orders.py", {"module": "shop.checks"})
    orders = tmp_path / "shop" / "orders.py"
    assert orders.read_text().startswith("from shop.checks import require_positive, require_admin\n")
    orders.write_text(orders.read_text().replace(
        "    raise NotImplementedError('TODO:Set result from the validated value')\n", "    result = amount * 100\n"))
    assert check_project(tmp_path)["ok"] is True
    (tmp_path / "shop" / "__init__.py").write_text("")
    import subprocess
    import sys
    run = subprocess.run([sys.executable, "-c", "from shop.orders import process; print(process(3, 'admin'))"],
                         cwd=tmp_path, capture_output=True, text=True, check=False)
    assert run.stdout.strip() == "300", run.stderr
    with pytest.raises(PresetError, match="module path"):
        apply_preset(tmp_path, "checked_operation", "x.py", {"module": "shop..checks"})
