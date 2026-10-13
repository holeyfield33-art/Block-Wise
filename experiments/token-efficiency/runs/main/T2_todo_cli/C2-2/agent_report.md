I wrote `app/todo.py` (in the r02 workspace). It passes my behavioral checks, but the final `blockwise check` run flags `main` as `body_changed`.

- **Template:** I applied it with `blockwise apply todo_cli --into app`, which wrote `app/todo.py`.
- **Checks:** I ran one batch of behavioral checks, then a second short batch after my edit, so two runs in total. In `scratch/t` I covered:
  - list with no items and with no arguments
  - add with extra spaces, with whitespace only, and with no text
  - done on valid, out-of-range and zero numbers
  - an unknown command (exit 2)
  - a corrupt `todo.json`, which is treated as empty
- **One edit:** the template crashed on `done x` and on `done` with no number. It printed Python exception text instead of the spec's message. I changed the `done` branch of `main` so a bad or missing number prints `error: no item X` and exits 1. That output is not stated in the spec; it is my reading of the "no such item" rule.
- **Block-Wise check:** after that edit, `blockwise check` reports `{"ok":false, ... "problem":"body_changed"}` for `main`, because I changed its structure. The check only compares structure, not behavior. I chose the fix for the bad-number cases over a clean check.
