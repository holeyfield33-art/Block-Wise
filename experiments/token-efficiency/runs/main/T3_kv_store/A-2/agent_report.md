I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r27/app/store.py`, and my own checks passed. I ran them once, as a single manual shell sequence in the `scratch/` directory, using 2 tool calls in total.

The checks covered:
- `list` and no arguments, including the `(empty)` output
- `set`, `get` and `delete`, including the missing-key error with exit code 1
- wrong argument counts and an unknown command, which print the usage line with exit code 2
- a `store.json` containing invalid JSON, which is treated as an empty store

A `store.json` that holds valid JSON but is not an object is also treated as empty. I did not run that case.
