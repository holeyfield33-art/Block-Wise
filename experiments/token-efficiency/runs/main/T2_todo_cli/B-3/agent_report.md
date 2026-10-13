I wrote app/todo.py (/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r46/app/todo.py), following the plan's structure exactly. My own check passed. I ran it once, as a single manual sequence in scratch/t.

It covered the empty list, add, empty-text add (error, exit 1), done, a missing item number (error, exit 1), list output, and an unknown command (usage message, exit 2). All matched the spec.

I did not test `done` with a non-numeric or missing argument. Per the plan, both are caught as ValueError or IndexError, so they print `error: ...` and exit 1.
