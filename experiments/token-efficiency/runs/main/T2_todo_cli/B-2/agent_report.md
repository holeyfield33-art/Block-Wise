I wrote app/todo.py to the plan and my own checks passed.

- **File written:** `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r14/app/todo.py`. It matches the plan's imports, constant, function signatures, return types and body structure.
- **Checks:** I ran one sequence of 8 commands in `scratch/t`, all in a single Bash call, and every result matched the spec:
  - `list` on an empty store, `add`, `list`, `done`, `list` again
  - `add` with empty text (error, exit 1)
  - `done 5` on a missing item (error, exit 1)
  - an unknown command (usage message, exit 2)
- **Tool calls:** 2 of the 30 allowed.
- **Not tested:** a corrupt or missing `todo.json` file, and `done` with no number or a non-numeric one. The plan's `except (IndexError, ValueError)` should print `error: ...` and exit 1 for the last two.
