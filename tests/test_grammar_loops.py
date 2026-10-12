"""Grammar additions: while, break / continue, and augmented assignment (+=, //= ...)."""

import copy

import pytest

from blockwise.compiler import compile_score, write_project
from blockwise.conformance import compare_score
from blockwise.coverage import unsupported
from blockwise.schema import FORMAT, ScoreError, validate_score


def plan(body, name="f", parameters=None):
    return {"format": FORMAT, "modules": [{"path": "m.py", "functions": [
        {"name": name, "parameters": parameters or [{"name": "n", "type": "int"}], "returns": "int", "body": body}]}]}


PLAN = plan([
    {"kind": "assign", "target": "total", "expression": "0"},
    {"kind": "while", "condition": "n > 0", "body": [
        {"kind": "branch", "condition": "n % 2 == 0", "body": [
            {"kind": "assign", "target": "n", "operator": "-=", "expression": "1"},
            {"kind": "continue"}]},
        {"kind": "branch", "condition": "total > 100", "body": [{"kind": "break"}]},
        {"kind": "assign", "target": "total", "operator": "+=", "expression": "n"},
        {"kind": "assign", "target": "n", "operator": "//=", "expression": "2"}]},
    {"kind": "return", "expression": "total"}])

EXPECTED = '''def f(n: int) -> int:
    total = 0
    while n > 0:
        if n % 2 == 0:
            n -= 1
            continue
        if total > 100:
            break
        total += n
        n //= 2
    return total
'''


def test_loop_blocks_compile_and_run():
    source = compile_score(PLAN)["m.py"]
    assert source.split("\n", 1)[1].lstrip("\n") == EXPECTED
    assert unsupported(source) == []
    namespace = {}
    exec(source, namespace)  # plan defined in this test
    assert namespace["f"](10) == 9 + 3 + 1 and namespace["f"](0) == 0


def test_old_assign_nodes_default_to_equals():
    node = validate_score(plan([{"kind": "assign", "target": "x", "expression": "1"}, {"kind": "return", "expression": "x"}]))
    assert node["modules"][0]["functions"][0]["body"][0]["operator"] == "="


@pytest.mark.parametrize("body, message", [
    ([{"kind": "break"}], "inside a loop"),
    ([{"kind": "branch", "condition": "n", "body": [{"kind": "continue"}]}], "inside a loop"),
    ([{"kind": "while", "condition": "n", "body": [{"kind": "try", "exception": "ValueError", "body": [],
                                                   "finally": [{"kind": "break"}]}]}], "finally"),
    ([{"kind": "assign", "target": "n", "operator": "=+", "expression": "1"}], "operator"),
    ([{"kind": "while", "condition": "", "body": []}], "While condition"),
    ([{"kind": "break", "label": "x"}], "unknown"),
])
def test_bad_loop_plans_are_refused(body, message):
    with pytest.raises(ScoreError, match=message):
        validate_score(plan(body))


def test_break_inside_try_inside_loop_is_allowed():
    validate_score(plan([{"kind": "loop", "target": "x", "iterable": "range(n)", "body": [
        {"kind": "try", "exception": "ValueError", "body": [{"kind": "break"}], "handler": [{"kind": "continue"}]}]},
        {"kind": "return", "expression": "n"}]))


@pytest.mark.parametrize("old, new", [
    ("total += n", "total -= n"),
    ("total += n", "total = total + n"),
    ("while n > 0:", "while n >= 0:"),
    ("            continue\n", ""),
    ("            break", "            pass"),
])
def test_check_notices_loop_changes(tmp_path, old, new):
    write_project(PLAN, tmp_path / "out")
    target = tmp_path / "out" / "repo" / "m.py"
    assert compare_score(PLAN, tmp_path / "out" / "repo")["compliant"]
    text = target.read_text(encoding="utf-8")
    assert old in text
    target.write_text(text.replace(old, new, 1), encoding="utf-8")
    assert not compare_score(PLAN, tmp_path / "out" / "repo")["compliant"]


def test_checker_still_flags_what_has_no_block():
    assert unsupported("def f(xs: list) -> None:\n    xs[0] += 1") == ["target-assign"]
    assert unsupported("def f(n: int) -> None:\n    while n:\n        n -= 1\n    else:\n        pass") == ["for-else"]
    assert unsupported(copy.deepcopy(EXPECTED)) == []
