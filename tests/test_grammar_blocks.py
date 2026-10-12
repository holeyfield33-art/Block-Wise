"""Grammar additions: module constants, default parameter values, try/except/finally and with."""

import copy

import pytest

from blockwise.audio import flatten_events
from blockwise.compiler import compile_score, write_project
from blockwise.conformance import compare_score
from blockwise.coverage import unsupported
from blockwise.schema import FORMAT, ScoreError, validate_score

PLAN = {"format": FORMAT, "modules": [{"path": "store.py", "imports": ["import json"],
    "constants": [{"name": "LIMIT", "value": "10"}, {"name": "ROLES", "value": "('admin', 'owner')"}],
    "functions": [{"name": "load", "parameters": [{"name": "path", "type": "str"}, {"name": "fallback", "type": "dict | None", "default": "None"}],
                   "returns": "dict | None", "body": [
        {"kind": "try", "exception": "(OSError, ValueError)", "alias": "error",
         "body": [{"kind": "with", "context": "open(path, encoding='utf-8')", "alias": "handle",
                   "body": [{"kind": "return", "expression": "json.load(handle)"}]}],
         "handler": [{"kind": "return", "expression": "fallback"}],
         "finally": [{"kind": "call", "expression": "print('done')"}]}]}]}]}

EXPECTED = '''import json
LIMIT = 10
ROLES = ('admin', 'owner')


def load(path: str, fallback: dict | None=None) -> dict | None:
    try:
        with open(path, encoding='utf-8') as handle:
            return json.load(handle)
    except (OSError, ValueError) as error:
        return fallback
    finally:
        print('done')
'''


def test_new_blocks_compile_to_expected_python():
    source = compile_score(PLAN)["store.py"]
    assert source.split("\n", 1)[1] == EXPECTED
    assert unsupported(source) == []


def test_generated_code_runs(tmp_path):
    namespace = {}
    exec(compile_score(PLAN)["store.py"], namespace)  # plan defined in this test
    good = tmp_path / "good.json"
    good.write_text('{"a": 1}', encoding="utf-8")
    assert namespace["load"](str(good)) == {"a": 1}
    assert namespace["load"](str(tmp_path / "missing.json"), {"x": 0}) == {"x": 0}


def test_optional_fields_default_and_old_plans_still_validate():
    plan = validate_score({"format": FORMAT, "modules": [{"path": "m.py", "functions": [{"name": "f", "parameters": [], "body": [
        {"kind": "try", "exception": "ValueError", "body": []}, {"kind": "with", "context": "lock", "body": []}]}]}]})
    node = plan["modules"][0]["functions"][0]["body"][0]
    assert node["alias"] == "" and node["handler"] == [] and node["finally"] == []
    assert plan["modules"][0]["constants"] == []
    source = compile_score(plan)["m.py"]
    assert "except ValueError:\n        pass" in source and "with lock:\n        pass" in source


@pytest.mark.parametrize("mutate, message", [
    (lambda f, m: f["parameters"].insert(2, {"name": "late", "type": "int"}), "needs a default"),
    (lambda f, m: f["body"][0].update(exception="ValueError()"), "Exception type"),
    (lambda f, m: f["body"][0].update(exception="()"), "Exception type"),
    (lambda f, m: f["body"][0].update(alias="1x"), "alias"),
    (lambda f, m: m["constants"].append({"name": "LIMIT", "value": "2"}), "Duplicate constant"),
    (lambda f, m: m["constants"].append({"name": "load", "value": "2"}), "Duplicate function name"),
    (lambda f, m: m["constants"].append({"name": "X", "value": "x ="}), "Invalid expression"),
    (lambda f, m: f["body"][0]["body"][0].update(context=""), "With context"),
])
def test_bad_plans_are_refused(mutate, message):
    plan = copy.deepcopy(PLAN)
    module = plan["modules"][0]
    mutate(module["functions"][0], module)
    with pytest.raises(ScoreError, match=message):
        validate_score(plan)


def built(tmp_path, plan=PLAN):
    write_project(plan, tmp_path / "out")
    return tmp_path / "out" / "repo"


def test_check_accepts_the_generated_project(tmp_path):
    report = compare_score(PLAN, built(tmp_path))
    assert report["compliant"], report["issues"]


@pytest.mark.parametrize("old, new, kind", [
    ("except (OSError, ValueError) as error:", "except OSError as error:", "body_changed"),
    ("except (OSError, ValueError) as error:", "except (OSError, ValueError):", "body_changed"),
    ("    finally:\n        print('done')\n", "", "body_changed"),
    ("as handle:", "as fh:", "body_changed"),
    ("LIMIT = 10", "LIMIT = 11", "constant_changed"),
    ("ROLES = ('admin', 'owner')\n", "", "missing_constant"),
    ("fallback: dict | None=None", "fallback: dict | None", "signature_changed"),
])
def test_check_notices_changes(tmp_path, old, new, kind):
    repo = built(tmp_path)
    target = repo / "store.py"
    text = target.read_text(encoding="utf-8")
    assert old in text
    target.write_text(text.replace(old, new), encoding="utf-8")
    assert kind in {issue["kind"] for issue in compare_score(PLAN, repo)["issues"]}


def test_holes_work_inside_try_and_with(tmp_path):
    plan = copy.deepcopy(PLAN)
    plan["modules"][0]["functions"][0]["body"][0]["handler"] = [
        {"kind": "hole", "label": "log and fall back", "allowed_calls": ["print"]}, {"kind": "return", "expression": "fallback"}]
    repo = built(tmp_path, plan)
    target = repo / "store.py"
    filled = target.read_text(encoding="utf-8").replace("raise NotImplementedError('TODO:log and fall back')", "print(error)")
    target.write_text(filled, encoding="utf-8")
    assert compare_score(plan, repo)["compliant"]
    target.write_text(filled.replace("print(error)", "import os"), encoding="utf-8")
    assert not compare_score(plan, repo)["compliant"]


def test_sound_layer_walks_new_blocks():
    kinds = [event["kind"] for event in flatten_events(PLAN)]
    assert kinds == ["function", "try", "with", "return", "return", "call"]
