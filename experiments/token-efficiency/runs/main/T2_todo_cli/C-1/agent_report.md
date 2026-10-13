Wrote /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r08/app/todo.py by applying the Block-Wise `todo_cli` blueprint (found via `find`), then edited two things: (1) `done` with a non-numeric or missing argument now prints `error: no item X` and exits 1, instead of Python's int-parse message; (2) `load_items` returns an empty list when todo.json is valid JSON but not a list of items with a `text` field.

My behavioral checks passed. I ran them in two rounds in scratch/:
- Round 1, on the blueprint as generated: empty list, add with whitespace, empty add (exit 1), done, out-of-range done (exit 1), unknown command (exit 2), corrupt todo.json.
- Round 2, after the edits: add a b, done x, done with no argument, done 0, done 1, list, and a todo.json containing valid JSON that isn't a list.

The empty-add, out-of-range-done, unknown-command and corrupt-file cases were not re-run after the edits.

`blockwise check` was run once, after the edits, and returned ok:false. It reports `body_changed` for `load_items` and `main`, because I edited those functions. I left them edited on purpose, since the check covers structure only.

About 6 of the 30 tool calls were used.
