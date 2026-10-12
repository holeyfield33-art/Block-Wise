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
| `blockwise find <words>` | the 3 best-matching presets, e.g. `blockwise find reject negative number` |
| `blockwise list [--category validation\|auth\|data\|files]` | `[{id, category, does, params}]` |
| `blockwise apply <id> --into <file.py> [--set k=v ...]` | `{"ok":true,"added":"file.py:name"}` plus `todo` if the preset leaves work |
| `blockwise check [--strict]` | `{"ok":true,...}` or a list of `{file, function, problem}` |
| `blockwise coverage [--file f.py]` | what Blockwise can represent; with `--file`, which constructs in that file have no block yet |

Exit codes: `0` ok, `1` the check found issues, `2` bad input.

**MCP server.** Run `pip install -e ".[mcp]"`, then add Blockwise to your agent's MCP config:

```json
{ "mcpServers": { "blockwise": { "command": "blockwise", "args": ["mcp"] } } }
```

The server provides six tools: `find_presets`, `list_presets`, `show_preset`, `apply_preset`, `check_project`
and `coverage`.

How it works:
- Each applied preset is recorded in `.blockwise/plan.json`.
- `check` confirms that the planned guards, call order and imports are still in place.
  **Lenient** mode (the default) ignores your other code. `--strict` also flags files and
  functions the plan doesn't mention.
- A preset with a TODO (for example `checked_operation`) returns the TODO and the calls it may
  use. The check fails until the TODO is filled.

**Does it save tokens? Measured, not assumed** (`python benchmarks/token_cost.py`):

| | tokens |
|---|---|
| Agent writes one preset-sized function itself (output) | ~42 |
| Agent calls the preset instead (output + reply read back) | ~10 + ~20 |
| Saved per use, counting output at 5× input price | ~137 input-equivalent |
| Discovery, one time: `list` (all 26) / `find` (top 3) | ~1,340 / ~148 |
| **Blueprints** (4 whole programs, 5–8 functions + main block): write vs call | ~410–550 vs ~8 + ~27 |
| Saved per blueprint use | **~2,000–2,700 input-equivalent** |

So with `find`, a preset pays for itself on its first use. With `list`, it takes about 8 uses.
Single-function presets save little, because a model writes a 3–14 line function cheaply anyway.
Blueprints are where it pays: one call replaces a whole runnable program (about 18× the saving of
a single preset). The larger gains are reliability: the code is tested, `check` notices when it
drifts from the plan, and every agent writes the same thing the same way. Token savings will grow
with bigger templates (patterns and app blueprints), and `blockwise coverage` shows which Python
constructs those templates still need.

## Blueprints: whole programs from one call

A blueprint is a template for whole files: several functions, constants and a main block. Apply it
like a preset, with a folder instead of a file:

```bash
blockwise find to-do list command line          # -> todo_cli (category "blueprint")
blockwise apply todo_cli --into tools --set file=tasks
# {"ok":true,"added":["tools/tasks.py"],"blueprint":"todo_cli","try":"python tools/tasks.py add buy milk"}
python tools/tasks.py add buy milk && python tools/tasks.py list
blockwise check                                  # the files stay under the same structure check
```

| Blueprint | What it is | Try it |
|---|---|---|
| `todo_cli` | to-do list saved to JSON: list, add, done | `python todo.py add buy milk` |
| `kv_store` | key-value store saved to JSON: set, get, delete, list | `python store.py set name Ana` |
| `csv_report` | group a CSV by one column and total another | `python report.py sales.csv region amount` |
| `log_stats` | count log lines per level and list the top errors | `python logstats.py app.log` |

Blueprints live in `blockwise/library/blueprints/`. Their `examples` are real command lines: the
tests generate the program, run it as a subprocess with each example's arguments in order (so saved
data carries over; `files` creates input files first), and compare stdout and the exit code. They
must also get no Advisor tips, so they stay examples of good structure.

## Python coverage registry

`blockwise/coverage.json` maps 58 Python concepts across 16 domains to what Blockwise can do with them:

- **block (22):** has its own block (functions with default values, a main block, if/elif/else, for, while,
  break/continue, try/except/finally, with, assignment including `+=`, calls, return, raise, module
  constants, imports, packages);
- **expression (15):** works inside any block's fields (comprehensions, f-strings, lambda, `:=`, ...);
- **planned (21):** cannot be represented yet (several except clauses, loop `else`, unpacking in
  `for`, classes, async, decorators, `if __name__ == '__main__'`, ...).

Each entry has an example and a link to the official Python reference. The tests hold the registry
to the code: every *block* and *expression* example compiles through the plan grammar, every
*planned* example is caught by the checker, and everything Blockwise generates passes the checker.
`blockwise coverage` prints the counts, `--status planned` lists the gaps, and `--file app.py` says
whether a file could become a plan.

## For learners: Blockwise Studio

- **Blocks:** Function, Check, If/Else, Repeat for each, Repeat while, Stop loop (`break`), Skip to
  next (`continue`), Set variable (with `=`, `+=`, `-=`, `//=` and the rest), Call, Return, Raise
  error, Try / Except (with an optional finally), Use resource (`with`) and TODO. Function inputs take
  default values (`fallback: int=0`), and each file can hold constants (`MAX_ITEMS = 10`). Click "+ add inside" anywhere to nest blocks. Each block in the list shows the Python
  it becomes.
- **Live Python:** the code pane shows exactly what `blockwise build` would generate. A test keeps
  the two byte-identical.
- **Run it for real:** *Try it* calls your functions, and *Run tests* runs each lesson's test
  cases. Python runs in the browser (Pyodide, downloaded from a CDN on first use, in a web worker
  with a 10-second limit so a runaway loop can't freeze the page).
- **Lessons (12):**
  1. Your first function
  2. If / Else
  3. More than two choices: elif
  4. Guard your inputs
  5. Loops: shopping cart total
  6. Build a list: keep the even numbers
  7. Find the biggest number
  8. Split code into files and folders
  9. Handle mistakes with try / except
  10. Repeat while: add up the digits
  11. Stop early with break
  12. Make it runnable: the main block

  Each lesson starts *Guided* (part-built, with TODOs) or *Blank* (signatures only). *Check my
  work* gives hints rather than answers. If your version passes every test but is built
  differently from the model answer, it still counts.
- **Beginner help:** a welcome guide on first visit (reopen with **?**), undo/redo (Ctrl+Z /
  Ctrl+Shift+Z), plain-language messages for invalid names and expressions, tickable lesson
  steps, a progress rail with a *Next lesson* button, and a **Words** glossary linked from each
  lesson's concept tags.
- **Runnable files:** *+ main block* adds `if __name__ == '__main__':` to a file. The Python tab then
  shows **Run file**, which runs it like a terminal would, with arguments (`add "buy milk"`). Files
  the program saves are kept between runs until you press *Clear saved data*.
- **Whole-program templates:** the Templates tab's *whole program* cards (blueprints) add complete
  files, such as a command-line to-do list, ready to run and to take apart.
- **Build your own script:** **New** starts a blank `main.py` (or starts from a template). In free
  build, a *Next step* checklist follows your progress: add blocks, replace TODOs, return what
  you promise, connect your functions, run it. Blocks can be moved into the block above (→), out
  of the block they're in (←), duplicated (⧉), moved up/down or deleted, and the value boxes
  suggest the names you've already defined.
- **Connecting code:** the Advisor spots a call to a function in another file without an import,
  a call to a name that doesn't exist (with "did you mean…?"), an import of a name the other file
  doesn't have, and a function nothing is connected to. Most come with a one-click fix.
- **Using a template:** after you insert one, a card explains how to use it: *Add a call in
  main()* calls it from the function you were working on (adding the import and any missing
  inputs), and *Try it* runs it with one of its tested examples.
- **Advisor:** live tips on deep nesting, long functions, files with too many jobs, repeated
  conditions, a missing return, and when to use a folder.
- **Templates tab:** search and filter the preset library, preview each template's code, and insert
  it into your file with its parameters and imports.
- **Export and import:** download a `.py` file or `plan.json`, and turn a plan into a project with
  `blockwise build plan.json --out my-project`. Plans exported from Sonic Code Studio
  (`sonic-template-v1`) open too.

To add a lesson, append an entry to `studio/lessons.js`. A lesson has a goal, steps, an explanation,
`concepts` (each needs an entry in the page's glossary), `tests` (calls with an `expect`ed value or
the exception they `raise`, or `run` + `argv` + expected `stdout` to run the file as a program), a `starter` plan and a `solution` plan. The tests check that every
lesson compiles, that its solution passes its tests, and that the guided starter does not.

The site is GitHub Pages serving the `main` branch; the root `index.html` forwards to `studio/`, so
merging to `main` publishes it. `.github/workflows/tests.yml` runs the test suite on pushes and PRs.

## Adding presets

Presets live in `blockwise/library/*.json`. Each preset is a plan for one function with
`{{param}}` placeholders, plus `examples` that the tests execute.
For file templates, an example can list `files` to create first, use `{dir}` in its arguments
for the folder they are written to, and list `then_files` with the contents expected afterwards.
Write template expressions the way Python prints them (e.g. `a or (b and c)`): a test checks that
the Studio shows exactly what `blockwise apply` writes.

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
- The plan grammar covers functions (with default values), module constants, if/else, for and
  while loops with break/continue, try/except/finally with one except clause, `with`, assignments
  to names (including `+=`), calls, returns, raises and TODOs. It has no classes or `async` yet; `blockwise coverage --status planned` lists
  every gap. A file's main block may not use `return` (use `sys.exit(code)`).
- The sound is decoration. It encodes only the kind of each block, never names or conditions.

## License

MIT, see [LICENSE](LICENSE). The plan grammar, compiler and checker are adapted from Sonic Code Studio, reused with the owner's permission.
