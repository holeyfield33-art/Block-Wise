I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r36/app/store.py`, and my checks passed. I ran them once, as a single command in `scratch/`.

The checks covered:
- no arguments
- `set`
- `list` with an extra argument
- `get`
- `delete`
- a missing key (exit 1)
- `set` with the wrong argument count (usage message, exit 2)
- an invalid `store.json` (treated as empty)

I did not separately test `store.json` containing valid JSON that isn't an object. The code treats that as empty too, and any value read from the file is printed as text.
