I wrote /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r07/app/todo.py. My behavioral checks passed, but `blockwise check` fails on the final file.

**How it was built:** `blockwise find` returned the `todo_cli` blueprint, and I applied it with `apply todo_cli --into app`. The unmodified blueprint passed `blockwise check`. The only file in app/ is todo.py.

**Edits I made to the blueprint:**
- **`load_items`:** it now returns an empty list when the JSON is not a list. It also drops entries that are not dicts with a string `text`. Before this, a todo.json containing `{"a":1}` or `[1,"x"]` crashed `list` with a TypeError.
- **`format_items`:** it reads `done` with `.get`.
- **`done` in `main`:** a non-numeric or missing argument now prints `error: no item ...` and exits 1. Before this, it printed Python's own error text.

**Checks:**
- **Own checks:** I ran them twice by hand with shell loops in scratch/t, not a script. They covered:
  - no arguments, `list`, and an empty list
  - `add` with empty, blank, multi-word, and extra-spaced text
  - `done` on valid, zero, out-of-range, non-numeric, missing and negative numbers
  - an unknown command, which gives the usage line and exit code 2
  - a garbage todo.json, plus a todo.json holding a non-list or non-dict entries
  - the exit codes and output text for all of the above
- **Result:** the second run, after the edits, covered the edited behaviour and passed. In the first run, `done abc`, `done` and the non-list and non-dict todo.json cases failed and prompted the edits. I did not rerun the full first-run list after editing, only the edited cases.
- **`blockwise check`:** I ran it twice. It passed on the unmodified blueprint. After my edits it reports `body_changed` on `load_items`, `format_items` and `main`. I left that as is because the edits fix real crashes and the tool only checks structure.
