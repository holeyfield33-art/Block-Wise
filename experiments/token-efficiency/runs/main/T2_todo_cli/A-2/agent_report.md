I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r43/app/todo.py` and nothing else in `app/`.

My own check passed. I ran it once, in `scratch/`, with a single shell script. It covered:
- no arguments
- add (including stripping and joining the text)
- done
- list
- `done` with a nonexistent item (exit 1)
- add with empty text (exit 1)
- an unknown command (exit 2)
- an invalid `todo.json`, which gave `Nothing to do.`

I made two choices the spec doesn't cover:
- `done` with no number prints the usage line and exits 2.
- A non-numeric or zero `done` argument prints `error: no item ARG` and exits 1.
