"""The coverage registry tells the truth: every status is checked against the compiler and the checker."""

import json
import sys
from pathlib import Path

import pytest

from blockwise.cli import main
from blockwise.compiler import compile_score
from blockwise.coverage import STATEMENT_GAPS, STATUSES, load_coverage, unsupported
from blockwise.presets import find, load_presets, render, summary
from blockwise.project import function_source
from blockwise.schema import FORMAT, NOTES, expression

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = load_coverage()
CONCEPTS = REGISTRY["concepts"]
IDS = {c["id"] for c in CONCEPTS}


def lesson_ids():
    text = (ROOT / "studio" / "lessons.js").read_text(encoding="utf-8")
    return {lesson["id"] for lesson in json.loads(text[text.index("= ") + 2:text.rindex(";")])}


def parses_here(concept):
    since = tuple(int(p) for p in concept.get("since", "3.0").split("."))
    return since <= sys.version_info[:2]


def by_status(status):
    return [pytest.param(c, id=c["id"]) for c in CONCEPTS if c["status"] == status]


def test_registry_shape():
    assert len(IDS) == len(CONCEPTS) >= 50
    assert set(REGISTRY["statuses"]) == set(STATUSES)
    lessons = lesson_ids()
    for concept in CONCEPTS:
        assert concept["status"] in STATUSES and concept["domain"] and concept["concept"] and concept["example"]
        assert concept["ref"].startswith(("https://docs.python.org/3/", "https://peps.python.org/"))
        assert concept.get("lesson", next(iter(lessons))) in lessons
    assert set(STATEMENT_GAPS.values()) <= IDS


@pytest.mark.parametrize("concept", by_status("block"))
def test_block_concepts_have_a_block_and_pass_the_checker(concept):
    assert concept["blockwise"] in set(NOTES) | {"import", "module"}
    assert unsupported(concept["example"]) == []


@pytest.mark.parametrize("concept", by_status("expression"))
def test_expression_concepts_compile_inside_a_block(concept):
    expression(concept["example"], concept["id"])
    plan = {"format": FORMAT, "modules": [{"path": "m.py", "imports": [], "functions": [
        {"name": "f", "parameters": [], "returns": "object", "body": [{"kind": "return", "expression": concept["example"]}]}]}]}
    assert unsupported(compile_score(plan)["m.py"]) == []


@pytest.mark.parametrize("concept", by_status("planned"))
def test_planned_concepts_are_detected_as_unsupported(concept):
    if not parses_here(concept):
        pytest.skip(f"needs Python {concept['since']}")
    assert concept["id"] in unsupported(concept["example"])


def test_everything_blockwise_generates_is_representable():
    for preset in load_presets().values():
        source, imports = function_source(*render(preset))
        assert unsupported("\n".join(imports + [source])) == [], preset["id"]
    text = (ROOT / "studio" / "lessons.js").read_text(encoding="utf-8")
    for lesson in json.loads(text[text.index("= ") + 2:text.rindex(";")]):
        for source in compile_score(lesson["solution"]).values():
            assert unsupported(source) == [], lesson["id"]


def test_find_returns_few_relevant_rows():
    assert find("reject negative number")[0]["id"] == "require_positive"
    assert find("divide by zero")[0]["id"] == "safe_divide"
    assert "require_role" in [r["id"] for r in find("only admins")]
    assert find("zzzz") == []
    everything = json.dumps([summary(p) for p in load_presets().values()])
    assert len(json.dumps(find("count by field"))) * 3 < len(everything)


def test_cli_coverage(tmp_path, capsys):
    assert main(["coverage"]) == 0
    counts = json.loads(capsys.readouterr().out)
    assert counts["block"] + counts["expression"] + counts["planned"] == counts["concepts"]
    good, bad = tmp_path / "good.py", tmp_path / "bad.py"
    good.write_text("def f(x: int) -> int:\n    return x\n")
    bad.write_text("def f(xs: list) -> int:\n    total = 0\n    for x in xs:\n        total += x\n    return total\n")
    assert main(["coverage", "--file", str(good)]) == 0
    capsys.readouterr()
    assert main(["coverage", "--file", str(bad)]) == 1
    assert json.loads(capsys.readouterr().out)["unsupported"][0]["id"] == "augmented-assign"
    assert main(["coverage", "--status", "planned", "--domain", "control flow"]) == 0
    assert {r["id"] for r in json.loads(capsys.readouterr().out)} >= {"while-loop", "match"}
