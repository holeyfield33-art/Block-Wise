# Blockwise

Blockwise is two tools built on one engine.

1. **Preset library for agents.** Tested building blocks such as "reject non-positive numbers",
   "owner or admin only" and "count by field". An agent *calls* a preset instead of writing
   boilerplate. A short call goes in, one line comes back, and the agent never reads the
   generated code.
2. **Blockwise Studio for learners.** A browser page where you build Python from blocks
   (Function, If/Else, loops, nesting) and watch the real code appear. It has guided lessons, a
   "check my work" button, and an advisor that says when to split code into a new function, file
   or folder.

The engine is a structured JSON *plan*, a code generator, and a structure checker. It is adapted
from Sonic Code Studio. An independent evaluation found that the plan, generator and checker were
the reliable parts. The music layer is optional here, and the Studio's sound toggle is off by
default.

## Quick start

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"           # add ,mcp for the agent server: pip install -e ".[dev,mcp]"
blockwise list                    # one compact line per preset
blockwise show require_role --set allowed=admin,owner
blockwise apply require_positive --into shop/checks.py --set value=qty
blockwise check                   # structure check of everything applied so far
```

**Try the Studio online: <https://holeyfield33-art.github.io/Block-Wise/>** — or open `studio/index.html`
in a browser. No server or install is needed.

## For agents: call presets, don't write boilerplate

| Command | What comes back |
|---|---|
| `blockwise list [--category validation\|auth\|data]` | `[{id, category, does, params}]` |
| `blockwise apply <id> --into <file.py> [--set k=v ...]` | `{"ok":true,"added":"file.py:name"}` plus `todo` if the preset leaves work |
| `blockwise check [--strict]` | `{"ok":true,...}` or a list of `{file, function, problem}` |

Exit codes: `0` ok, `1` the check found issues, `2` bad input.

**MCP server.** Run `pip install -e ".[mcp]"`, then add Blockwise to your agent's MCP config:

```json
{ "mcpServers": { "blockwise": { "command": "blockwise", "args": ["mcp"] } } }
```

The server provides four tools: `list_presets`, `show_preset`, `apply_preset` and `check_project`.

How it works:
- Each applied preset is recorded in `.blockwise/plan.json`.
- `check` confirms that the planned guards, call order and imports are still in place.
  **Lenient** mode (the default) ignores your other code. `--strict` also flags files and
  functions the plan doesn't mention.
- A preset with a TODO (for example `checked_operation`) returns the TODO and the calls it may
  use. The check fails until the TODO is filled.

**Why this should save money (measure it before you claim it).** In the evaluation, agents handed
a full spec and scaffold used about 45% *more* context, because they read all of it. Presets flip
that: the agent sends roughly 30 tokens and gets about 30 back, and the generated code never
enters its context. The next step is to measure this with the evaluation harness.

## For learners: Blockwise Studio

- **Blocks:** Function, Check, If/Else, Repeat for each, Set variable, Call, Return, Raise error
  and TODO. Click "+ add inside" anywhere to nest blocks. Each block in the list shows the Python
  it becomes.
- **Live Python:** the code pane shows exactly what `blockwise build` would generate. A test keeps
  the two byte-identical.
- **Run it for real:** *Try it* calls your functions, and *Run tests* runs each lesson's test
  cases. Python runs in the browser (Pyodide, downloaded from a CDN on first use, in a web worker
  with a 10-second limit so a runaway loop can't freeze the page).
- **Lessons (8):**
  1. Your first function
  2. If / Else
  3. More than two choices: elif
  4. Guard your inputs
  5. Loops: shopping cart total
  6. Build a list: keep the even numbers
  7. Find the biggest number
  8. Split code into files and folders

  Each lesson starts *Guided* (part-built, with TODOs) or *Blank* (signatures only). *Check my
  work* gives hints rather than answers. If your version passes every test but is built
  differently from the model answer, it still counts.
- **Beginner help:** a welcome guide on first visit (reopen with **?**), undo/redo (Ctrl+Z /
  Ctrl+Shift+Z), plain-language messages for invalid names and expressions, tickable lesson
  steps, a progress rail with a *Next lesson* button, and a **Words** glossary linked from each
  lesson's concept tags.
- **Advisor:** live tips on deep nesting, long functions, files with too many jobs, repeated
  conditions, a missing return, and when to use a folder.
- **Templates tab:** search and filter the preset library, preview each template's code, and insert
  it into your file with its parameters and imports.
- **Export and import:** download a `.py` file or `plan.json`, and turn a plan into a project with
  `blockwise build plan.json --out my-project`. Plans exported from Sonic Code Studio
  (`sonic-template-v1`) open too.

To add a lesson, append an entry to `studio/lessons.js`. A lesson has a goal, steps, an explanation,
`concepts` (each needs an entry in the page's glossary), `tests` (calls with an `expect`ed value or
the exception they `raise`), a `starter` plan and a `solution` plan. The tests check that every
lesson compiles, that its solution passes its tests, and that the guided starter does not.

The site is deployed to GitHub Pages by `.github/workflows/pages.yml` on every push to `main`,
after the tests pass.

## Adding presets

Presets live in `blockwise/library/*.json`. Each preset is a plan for one function with
`{{param}}` placeholders, plus `examples` that the tests execute.

Parameter kinds:
- `identifier`, `module` and `annotation`: names, module paths and type hints;
- `expression`: a Python expression;
- `string` and `string_list`: always inserted as safe Python literals;
- `number`;
- `text`: used only in TODO labels.

After editing, run `blockwise export-presets --out studio/presets.js`. A test fails if you forget.

## Tests

```bash
pytest -q          # engine, presets, CLI, MCP tools, lessons, plus a headless-browser Studio test
ruff check blockwise tests
```

The Studio browser test needs Node and the `playwright` npm package (installed globally, or point
`BLOCKWISE_NODE_PATH` at a `node_modules` folder that has it); without them it is skipped.

## Limits (by design, stated plainly)

- The check is **structural**. It confirms that the planned code is still there and in order. It
  does not prove behavior or security: code written inside a TODO can still be wrong. Always run
  real tests.
- The plan grammar covers plain functions, if/else, for-loops, assignments to names, calls,
  returns, raises and TODOs. It has no classes, `while`, `try` or `async` yet.
- The sound is decoration. It encodes only the kind of each block, never names or conditions.

## License

MIT, see [LICENSE](LICENSE). The plan grammar, compiler and checker are adapted from Sonic Code Studio, reused with the owner's permission.
