"""f-strings render the same on every supported Python, and always as Python 3.11 syntax.

CPython 3.12.0-3.12.8 and 3.13.0-3.13.2 unparse f'{d["k"]}' as f'{d['k']}', which
Python 3.11 cannot parse, so generated code (and approved output) depended on the
exact interpreter. These outputs are pinned: any interpreter must produce them.
"""

import ast

import pytest

from blockwise.compiler import unparse
from blockwise.schema import ScoreError

CASES = {
    "f\"skipped {summary['skipped']} unreadable line(s)\"": "f\"skipped {summary['skipped']} unreadable line(s)\"",
    "f'a {d[\"k\"]} b'": "f\"a {d['k']} b\"",
    "f'{x!r:>{width}} {y:.2f}'": "f'{x!r:>{width}} {y:.2f}'",
    "f\"it's {name}\"": "f\"it's {name}\"",
    "f'{a}\\n{b}'": "f'{a}\\n{b}'",
    "f'{ {1: 2}[1]}'": "f'{ {1: 2}[1]}'",
    "f'{{literal}} {x}'": "f'{{literal}} {x}'",
    "f'outer {f\"inner {x}\"} done'": "f\"outer {f'inner {x}'} done\"",
    "print(f\"{len(items)} item(s): {', '.join(items)}\")": "print(f\"{len(items)} item(s): {', '.join(items)}\")",
    "f\"{a['x']} and \\\"{b}\\\"\"": "f'''{a['x']} and \"{b}\"'''",
}


@pytest.mark.parametrize("source", sorted(CASES))
def test_fstring_rendering_is_pinned_and_round_trips(source):
    rendered = unparse(ast.parse(source, mode="eval").body)
    assert rendered == CASES[source]
    assert ast.dump(ast.parse(rendered, mode="eval")) == ast.dump(ast.parse(source, mode="eval"))


def test_no_replacement_field_reuses_its_enclosing_quote():
    # The 3.11 rule, checked directly so it holds even where the grammar is looser.
    for rendered in CASES.values():
        quote = rendered[rendered.index("f") + 1]
        for field in rendered.split("{")[1:]:
            assert quote not in field.split("}")[0] or rendered.endswith(quote * 3), rendered


def test_backslash_inside_a_field_is_refused():
    # Built as a tree: Python 3.11 cannot even parse such source.
    node = ast.parse("f'{x}'", mode="eval").body
    node.values[0].value = ast.Call(func=ast.Attribute(value=ast.Constant("\n"), attr="join", ctx=ast.Load()),
                                    args=[ast.Name(id="items", ctx=ast.Load())], keywords=[])
    with pytest.raises(ScoreError):
        unparse(node)
