"""Every preset renders, compiles and behaves as its own examples say; bad parameters are refused."""

import pytest

from blockwise.presets import PresetError, get_preset, load_presets, render
from blockwise.project import function_source

PRESETS = load_presets()


def build(preset_id, params=None):
    function, imports = render(get_preset(preset_id), params)
    source, import_lines = function_source(function, imports)
    namespace = {}
    exec(compile("\n".join(import_lines) + "\n" + source, preset_id, "exec"), namespace)  # trusted, shipped presets only
    return namespace[function["name"]]


def test_library_is_not_empty_and_ids_are_unique():
    assert len(PRESETS) >= 15
    assert {p["category"] for p in PRESETS.values()} == {"validation", "auth", "data", "files"}


@pytest.mark.parametrize("preset_id", sorted(PRESETS))
def test_preset_defaults_render_and_examples_hold(preset_id, tmp_path):
    preset = PRESETS[preset_id]
    if not preset["examples"]:
        render(preset)  # presets with TODOs still render to valid plans
        return
    function = build(preset_id)
    for number, example in enumerate(preset["examples"]):
        # File examples: "files" are written to a fresh folder, "{dir}" in text args points at it,
        # and "then_files" lists the contents expected afterwards.
        folder = tmp_path / str(number)
        folder.mkdir()
        for name, content in example.get("files", {}).items():
            (folder / name).write_text(content, encoding="utf-8")
        args = [a.replace("{dir}", str(folder)) if isinstance(a, str) else a for a in example["args"]]
        if "raises" in example:
            with pytest.raises(Exception) as caught:
                function(*args)
            assert type(caught.value).__name__ == example["raises"]
        else:
            assert function(*args) == example["returns"]
        for name, content in example.get("then_files", {}).items():
            assert (folder / name).read_text(encoding="utf-8") == content


def test_parameters_change_the_code():
    require = build("require_role", {"allowed": "admin,owner", "function": "require_staff"})
    require("owner")
    with pytest.raises(PermissionError):
        require("guest")
    keep = build("filter_items", {"condition": "item > 3", "items": "numbers"})
    assert keep([1, 5, 9]) == [5, 9]


@pytest.mark.parametrize("preset_id,params", [
    ("require_positive", {"value": "x; import os"}),
    ("require_positive", {"value": "class"}),
    ("require_positive", {"type": "__import__('os')"}),
    ("filter_items", {"condition": "item\nimport os"}),
    ("filter_items", {"condition": "(lambda: 1"}),
    ("require_range", {"low": "zero"}),
    ("require_range", {"high": True}),
    ("require_choice", {"choices": []}),
    ("require_choice", {"nope": "x"}),
    ("checked_operation", {"work": "{{function}}"}),
    ("lookup_or_error", {"mapping": "catalog", "key": "catalog"}),
])
def test_bad_parameters_are_refused(preset_id, params):
    with pytest.raises(PresetError):
        render(get_preset(preset_id), params)


def test_string_parameters_cannot_break_out_of_their_literal():
    count = build("count_by", {"field": "x') or __import__('os"})
    assert count([{"x') or __import__('os": "a"}]) == {"a": 1}


@pytest.mark.parametrize("value", [["a.test", "b.test"], "a.test,b.test", " a.test , b.test ", '["a.test", "b.test"]'])
def test_string_list_accepts_lists_json_and_commas(value):
    from blockwise.presets import render_value

    assert render_value("hosts", {"kind": "string_list"}, value) == "('a.test', 'b.test')"


@pytest.mark.parametrize("value", ['["a.test", "b.test"', '["a.test", 5]', '"a.test"', "[]", "", 'a"b', "a]b"])
def test_string_list_refuses_half_parsed_or_odd_items(value):
    # Session 1 found '["a", "b"]' rendered as ('["a"', '"b"]'): an allowlist that refused every host.
    from blockwise.presets import render_value

    with pytest.raises(PresetError):
        render_value("hosts", {"kind": "string_list"}, value)
