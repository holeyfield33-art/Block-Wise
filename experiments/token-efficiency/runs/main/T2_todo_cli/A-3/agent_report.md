I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r05/app/todo.py`, and my own check passed. I ran it once, as a single shell sequence in `scratch/`.

The sequence covered these cases:
- an empty list
- `add` with extra whitespace
- an empty `add`, which exits 1
- `done 1`, which marks the item done
- `done 3` on a missing item, which exits 1
- `list` after those changes
- an unknown command, which exits 2
- a corrupt `todo.json`, which lists as empty

All output matched the spec. I did not test non-numeric or zero arguments to `done`; by the code they print `error: no item ARG` and exit 1.

The spec doesn't say what a bare `done` with no number or `done` with extra arguments should do, so I made both print the usage line and exit 2. `list` with extra arguments does the same.

A valid but non-list `todo.json` is also treated as empty. Nothing else is in `app/`.
