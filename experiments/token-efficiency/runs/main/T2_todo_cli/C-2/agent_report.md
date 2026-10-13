I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r06/app/todo.py`, and my own behavioral checks passed. I ran them twice, once on the generated file and once after my edits.

- **Generated file:** I applied the Block-Wise `todo_cli` blueprint into `app/` and did not read its code until the first check run. That run showed two gaps against the spec.
- **`done` argument parsing:** a non-numeric argument printed Python's own exception text, and `done` with no argument crashed with an `IndexError` message. A non-numeric argument now prints `error: no item X` and exits 1. `done` with no argument prints the usage line and exits 2. The spec doesn't cover that second case, so that choice is my guess.
- **Invalid `todo.json`:** valid JSON that isn't a list of item objects (for example `{"a":1}`) now counts as an empty list, since the spec's item 5 only covers missing or invalid JSON.
- **Checks run:**
  - no arguments, `list`, and the empty list
  - `add` with whitespace and with empty text, and `done` with a good, out-of-range, zero, negative and non-numeric number
  - an unknown command, a corrupt `todo.json`, and valid JSON that isn't a list
- **`blockwise check`:** it passed after the first apply. In the final run it reported "No plan yet" and checked 0 functions, so it didn't re-verify the edited file.
