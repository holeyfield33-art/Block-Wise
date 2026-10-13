I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r26/app/store.py`. My own checks passed, and I ran them once, as a single batch of 15 commands in a fresh directory under `scratch/`.

The checks covered:
- no arguments and `list` with an extra argument
- `set`, `get` and `delete`, including a missing key (exit 1)
- a wrong argument count and an unknown command (exit 2 with the usage line)
- a `store.json` holding a non-dict (`[1]`) and one with invalid JSON (both treated as empty)

I did not test non-ASCII keys or values.

I used 2 tool calls in total, plus the read of the task file.
