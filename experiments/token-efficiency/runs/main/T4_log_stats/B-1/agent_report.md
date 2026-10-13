I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r15/app/logstats.py`, following the plan exactly. That means the same imports, constants, function signatures and body structure.

My own check passed, and I ran it once. I used a sample log with a blank line, a junk line and a duplicated error message. The output was correct (`INFO: 1`, `ERROR: 2`, `  2 x db timeout`, `skipped 2 unreadable line(s)`) and the exit code was 0. A missing file printed `error: cannot read nope` and exited with 1.

I did not run the wrong-argument-count case (usage message, exit 2), the empty-file case, or the three-message limit.

The test log is in `scratch/`. I used 2 tool calls.
