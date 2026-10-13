I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r17/app/todo.py`, following the plan exactly (same imports, constant, functions, signatures and body structure).

I ran one manual sequence of commands from `scratch/` and the output matched the spec every time. It covered:
- an empty list
- `add`
- an empty `add` (error message, exit 1)
- `done`
- `done` on a missing item (error message, exit 1)
- `list`
- an unknown command (usage message, exit 2)

It was a single run, with no separate test file. I made 2 tool calls in total.
