I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r50/app/todo.py`. I applied the Block-Wise `todo_cli` blueprint (`blockwise find` first, then `apply todo_cli --into app`), then edited it.

**What I changed in the generated file:**
- `done` with a non-numeric or missing number now prints `error: no item X` and exits 1. The template crashed on that case with a Python int-parsing message.
- `todo.json` that is valid JSON but not a list of items (for example `{"a":1}`) is treated as empty. Before, it would have crashed later.

**My checks passed, and I ran them twice** (an initial run, then a re-run after the edits), in `scratch/t`. They covered:
- no arguments
- `add` with empty, whitespace-only, and multi-space text
- `done` with valid, out-of-range, 0, non-numeric, and missing numbers
- an unknown command (exit 2)
- corrupt JSON and non-list JSON
- `list` output

**Block-Wise `check` reports `ok: false`.** It flags `load_items` and `main` as `body_changed`, because of my two edits above. It checks structure, not behavior, and I left the edits in because the behavior checks pass. `app/` contains only `todo.py`.
