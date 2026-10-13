I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r20/app/todo.py`, and my own checks passed. I ran them once, as a single manual sequence in `scratch/`. They covered:
- `list` with no items, and a corrupt `todo.json`
- `add`, including extra spaces and empty text
- `done`, for a valid and an out-of-range number
- an unknown command, which exits with code 2 and prints the usage line
- `list` after changes, which showed the done item as `[x]`

Choices the spec didn't settle:
- `done` with no number prints the usage line and exits 2.
- `done` with a non-integer, zero or negative number prints `error: no item ARG` and exits 1.
- Valid JSON that isn't a list is treated as an empty list.
