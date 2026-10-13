I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r10/app/store.py`, following the plan's imports, constant, functions and body structure. My own checks passed, and I ran them once (a single shell script, 1 of the 30 tool calls allowed).

The checks ran in `scratch/` and covered:
- empty `list`
- `set` and sorted `list`
- `get` on an existing and a missing key (exit 1)
- `delete` on an existing and a missing key (exit 1)
- a wrong argument count (usage message, exit 2)
- an unknown command (usage message, exit 2)
- a corrupt `store.json` (treated as empty)

Nothing else is in `app/`.
