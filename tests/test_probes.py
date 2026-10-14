"""Probe runner acceptance: hand-written functions with a known correct verdict.

The runner decides verdicts from what actually happened (outcome and side
effects), so each case here pins one row of the verdict table, including a
function that writes outside the workspace and *then* raises the expected
exception, which must be BYPASSED, never HELD.
"""

import pytest

from blockwise import probes
from blockwise.probes import ProbeError, run_probe, summarize, validate_security

FIXTURES = '''
import time
from pathlib import Path

def careful(root, relative):
    raise ValueError("refused")

def leaky(root, relative):
    (Path(root) / relative).write_text("x")
    raise ValueError("refused")

def wrong_error(root, relative):
    raise TypeError("not the declared error")

def silent(root, relative):
    return None

def slow(root, relative):
    time.sleep(30)

def chatty(root, relative):
    print("noise on stdout must not confuse the runner")
    (Path(root) / relative).write_text("hi")
    return None

def unserializable(root, relative):
    return object()
'''


@pytest.fixture(scope="module")
def source(tmp_path_factory):
    path = tmp_path_factory.mktemp("fixtures") / "fixtures.py"
    path.write_text(FIXTURES, encoding="utf-8")
    return path


def verdict(source, function, timeout=probes.TIMEOUT, **probe):
    return run_probe(source, function, {"id": "P", "threat": "T", **probe}, timeout)


def test_declared_refusal_without_side_effects_is_held(source):
    assert verdict(source, "careful", args=["{root}", "../x.txt"], raises="ValueError")["verdict"] == "HELD"


def test_writing_outside_then_raising_is_bypassed(source):
    result = verdict(source, "leaky", args=["{root}", "../outside/new.txt"], raises="ValueError")
    assert result["verdict"] == "BYPASSED"
    assert "outside/new.txt" in result["detail"]


def test_overwriting_the_sentinel_is_bypassed(source):
    result = verdict(source, "leaky", args=["{root}", "../outside/SENTINEL.txt"], raises="ValueError")
    assert result["verdict"] == "BYPASSED"


def test_wrong_exception_is_failed(source):
    assert verdict(source, "wrong_error", args=["{root}", "x"], raises="ValueError")["verdict"] == "FAILED"


def test_returning_normally_when_a_refusal_is_declared_is_failed(source):
    assert verdict(source, "silent", args=["{root}", "x"], raises="ValueError")["verdict"] == "FAILED"


def test_timeout_is_error(source):
    assert verdict(source, "slow", timeout=1, args=["{root}", "x"], raises="ValueError")["verdict"] == "ERROR"


def test_missing_function_is_error(source):
    assert verdict(source, "no_such_function", args=[], raises="ValueError")["verdict"] == "ERROR"


def test_functional_probe_checks_the_return_and_the_files(source):
    ok = verdict(source, "chatty", args=["{root}", "a.txt"], returns=None, then_files={"a.txt": "hi"})
    assert ok["verdict"] == "HELD"
    wrong = verdict(source, "chatty", args=["{root}", "a.txt"], returns=None, then_files={"a.txt": "bye"})
    assert wrong["verdict"] == "FAILED"


def test_a_declared_absent_path_that_exists_is_bypassed(source):
    result = verdict(source, "chatty", args=["{root}", "big.txt"], returns=None, absent=["big.txt"])
    assert result["verdict"] == "BYPASSED"


def test_unserializable_return_value_is_compared_by_repr_and_fails(source):
    assert verdict(source, "unserializable", args=["{root}", "x"], returns=None)["verdict"] == "FAILED"


def test_symlink_setup_that_the_platform_refuses_is_not_run(source, monkeypatch):
    def refuse(*args, **kwargs):
        raise OSError("symlinks not permitted")
    monkeypatch.setattr(probes.os, "symlink", refuse)
    result = verdict(source, "careful", args=["{root}", "link/x"], raises="ValueError",
                     setup={"symlinks": {"root/link": "outside"}})
    assert result["verdict"] == "NOT_RUN"


def test_summary_fails_closed():
    held = {"verdict": "HELD"}
    assert summarize([held, held])["status"] == "held"
    assert summarize([held, {"verdict": "NOT_RUN"}])["status"] == "held-with-gaps"
    for bad in ("BYPASSED", "FAILED", "ERROR"):
        assert summarize([held, {"verdict": bad}])["status"] == "not-held"
    assert summarize([])["status"] == "not-held"


def _section(**changes):
    section = {"function": "f",
               "threats": [{"id": "T1", "class": "PATH_TRAVERSAL", "summary": "s"}],
               "probes": [{"id": "P0", "threat": None, "args": [], "returns": None},
                          {"id": "P1", "threat": "T1", "args": [], "raises": "ValueError"}],
               "params": {}, "not_verified": ["races"]}
    return {"security": {**section, **changes}}


def test_validate_security_accepts_a_complete_section():
    assert validate_security(_section())["function"] == "f"


@pytest.mark.parametrize("changes", [
    {"threats": [{"id": "T1", "class": "MADE_UP", "summary": "s"}]},
    {"probes": [{"id": "P1", "threat": "T1", "args": [], "raises": "ValueError"}]},  # no functional probe
    {"probes": [{"id": "P0", "threat": None, "args": [], "returns": None}]},  # T1 has no probe
    {"probes": [{"id": "P0", "threat": None, "args": [], "returns": None},
                {"id": "P1", "threat": "T9", "args": [], "raises": "ValueError"}]},  # undeclared threat
    {"probes": [{"id": "P0", "threat": None, "args": [], "returns": None, "code": "rm -rf /"},
                {"id": "P1", "threat": "T1", "args": [], "raises": "ValueError"}]},  # probes carry data only
    {"not_verified": []},
    {"params": {"undeclared": "free"}},  # must declare exactly the blueprint's parameters
])
def test_validate_security_rejects_incomplete_sections(changes):
    with pytest.raises(ProbeError):
        validate_security(_section(**changes))


def test_parameter_bounds_are_checked_for_text_and_numbers():
    security = {"params": {"name": "free", "limit": {"min": 1, "max": 10}}}
    assert probes.param_violations(security, {"name": "anything", "limit": 5}) == []
    assert probes.param_violations(security, {"limit": "7"}) == []  # CLI values arrive as text
    for bad in (0, 11, -5, "lots", None, True):
        assert len(probes.param_violations(security, {"limit": bad})) == 1, bad


def test_over_placeholder_is_one_character_past_the_generated_limit(source):
    probe = {"id": "P", "threat": "T", "args": ["{root}", "{over:limit}"], "raises": "ValueError"}
    assert probes._fill(probe["args"], {"root": "/r"}, {"limit": "3"}) == ["/r", "xxxx"]
