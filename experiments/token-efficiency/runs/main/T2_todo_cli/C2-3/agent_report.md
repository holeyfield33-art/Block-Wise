I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r55/app/todo.py`. My own behavior checks passed, but the Block-Wise `check` now fails.

- **How it was built:** I ran `blockwise apply todo_cli --into app`, which wrote `app/todo.py`. `check` passed on the untouched file.
- **Behavior checks:** The first run covered no arguments, `add`, empty and whitespace-only `add`, `list`, `done`, a missing item, an unknown command, and a corrupt `todo.json`. It showed two problems:
  - `done x` and a bare `done` crashed with Python's own error text.
  - A `todo.json` containing valid JSON of the wrong shape, such as `[1]`, was not handled.
- **Edits:** I fixed both in `main` and `load_items`.
  - A non-numeric `done` argument now prints `error: no item x` and exits 1. A bare `done` prints `error: no item` and exits 1, which is my guess because the spec doesn't cover it.
  - Wrong-shape `todo.json` content is now treated as an empty list.
- **Re-runs:** A second, shorter run after the edits passed. In total I ran my checks twice.
- **`check` failure:** `blockwise check` now reports `body_changed` for `load_items`, `format_items` and `main`, because I edited generated code. Block-Wise checks structure only, and the edits were deliberate.
- **Tool calls:** I used 4 of the 30 allowed.
