# Using Blockwise from an AI coding agent

Blockwise gives an agent a library of **tested Python building blocks** it can drop into a project
with one short call, instead of writing the code token by token:

- **Presets:** single functions, such as "reject non-positive numbers", "owner or admin only" or
  "binary search".
- **Blueprints:** whole runnable programs, such as a CSV report tool, a to-do app or a JSON fetcher.

Everything it adds is recorded in a plan, so `check` can later tell whether the code still has the
structure it was given.

This guide covers setup (MCP or command line), the workflow to give your agent, and what to expect.

## 1. Install

Blockwise needs Python 3.11 or newer. It isn't on PyPI yet, so install it from GitHub:

```bash
pip install "blockwise[mcp] @ git+https://github.com/holeyfield33-art/Block-Wise"
blockwise list --category blueprint     # quick check that it works
```

Leave out `[mcp]` if you only want the command line. If you install into a virtual environment,
note the full path to the `blockwise` executable (for example `/home/me/.venv/bin/blockwise`, or
`C:\Users\me\.venv\Scripts\blockwise.exe` on Windows). Agent hosts often start tools without your
shell's `PATH`.

## 2. Connect it

### Option A: MCP server (recommended)

`blockwise mcp` runs an MCP server over stdio with six tools:

| Tool | What it does |
|---|---|
| `find_presets(query)` | The 3 best matches for a few words. **Start here** (~150 tokens). |
| `list_presets(category)` | Everything, or one category: `validation`, `auth`, `data`, `files`, `blueprint` (~1,600 tokens for all). |
| `show_preset(preset, params)` | The exact code a preset or blueprint would write, without writing it. |
| `apply_preset(preset, into, params, project)` | Writes it. For a preset, `into` is a file (`app/checks.py`). For a blueprint, it's a folder (`tools`, or `.`). |
| `check_project(project, strict)` | Confirms that everything applied still has its planned structure. |
| `coverage(source)` | Whether some Python could be expressed as a plan, and which constructs couldn't. |

**Claude Code.** In your project folder:

```bash
claude mcp add blockwise -- blockwise mcp
# with a virtual environment, use the full path:
claude mcp add blockwise -- /home/me/.venv/bin/blockwise mcp
```

To share the setup with your team, add `--scope project`. That writes it to `.mcp.json` in the
repository.

**Any other MCP host** (Claude Desktop, Cursor, and others) takes the same JSON:

```json
{ "mcpServers": { "blockwise": { "command": "blockwise", "args": ["mcp"] } } }
```

The six tool definitions add about **640 tokens** to the agent's context for each session. That is
the fixed price; section 4 shows what it buys.

### Option B: Command line only

Any agent that can run shell commands can use the same features. Every command prints one compact
JSON line:

```bash
blockwise find reject negative number
blockwise show require_positive --set value=qty
blockwise apply require_positive --into shop/checks.py --set value=qty
blockwise apply data_validator --into tools
blockwise check
blockwise coverage --file app/report.py
```

Exit codes: `0` ok, `1` the check found issues, `2` bad input.

## 3. Tell the agent how to use it

Agents use tools better with a short rule. Paste this into your `CLAUDE.md` or `AGENTS.md` (the
same text is in [agent-instructions.md](agent-instructions.md)):

```markdown
## Blockwise building blocks
Before writing a small, common Python function or a small command-line tool, search Blockwise:
1. `find_presets` with a few words (e.g. "validate csv emails", "retry", "group and total").
2. If a result fits, `show_preset` to read what it writes, then `apply_preset` with the right
   names in `params`. Don't re-type code a preset provides.
3. If the result lists a `todo`, fill only that part, using only the calls it allows.
4. After editing files that Blockwise wrote, run `check_project`. Fix the issues it reports, or
   tell me why the change was intended.
5. Blockwise checks structure, not behavior: still run the tests.
If nothing fits, write the code normally. Don't force a preset that doesn't match the task.
```

## 4. What it saves, measured

These figures come from `python benchmarks/token_cost.py`. They count output tokens at 5× the
input price, which is the usual ratio. The token counts are close estimates: the script uses an
OpenAI tokenizer as a stand-in, not Claude's own.

| | Write it yourself | Use Blockwise | Saved per use |
|---|---|---|---|
| A preset (23 single functions, average) | ~45 output tokens | ~10 output + ~20 input | ~150 input-equivalent |
| A blueprint (7 programs, 410–610 tokens of code) | ~410–610 output tokens | ~8 output + ~27 input | **~2,000–3,000** input-equivalent |

You also pay about 150 tokens to find something with `find_presets`, plus the 640-token tool
definitions once per session.

What that means in practice:

- **Blueprints pay off immediately.** One blueprint use covers the session's fixed cost several
  times over.
- **Single-function presets are close to break-even on tokens.** A model writes a 5-line function
  cheaply anyway. Their real value is reliability: tested behavior, the same code every time, and a
  `check` that catches later drift.

Measure your own sessions before making claims about a whole workflow.

## 5. What Blockwise checks, and what it doesn't

- **Checked:**
  - every preset and blueprint example is run in the test suite;
  - blueprints run as real programs with real files (and, for the fetcher, a local web server);
  - `check` confirms the planned functions, guards, call order, imports, constants and main
    blocks are still in place.
- **Not checked:**
  - **behavior after you edit the code.** `check` compares structure. Code written inside a TODO,
    or a changed condition, can still be wrong. Run your tests.
  - **security beyond what a template states.** For example, `password_problems` explains why a
    password is weak; it doesn't store or hash passwords.
- **Not supported yet:** classes, `async`, decorators, `*args`/`**kwargs`, several `except`
  clauses, and loop unpacking (`for k, v in …`). `coverage` lists every gap, and `coverage --file`
  tells you whether a given file could become a plan.

## 6. Reference

- [Template library and Studio overview](../README.md)
- Every preset: `blockwise list`. Every blueprint: `blockwise list --category blueprint`.
- Blueprints:

  | Blueprint | What it does |
  |---|---|
  | `todo_cli` | to-do list |
  | `kv_store` | key-value store |
  | `csv_report` | group and total a CSV |
  | `log_stats` | log summary |
  | `data_validator` | check a CSV of people |
  | `file_organizer` | sort files into folders, dry run first |
  | `fetch_json` | JSON from a URL |
  | `safe_write_text` | security block: write only inside a folder (`secure-apply --probe`) |
  | `url_allowlist` | security block: SSRF-safe URL allowlist check (`secure-apply --probe`) |
- Adding your own presets and blueprints: see "Adding presets" in the README.
