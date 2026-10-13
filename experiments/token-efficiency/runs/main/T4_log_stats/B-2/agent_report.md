I wrote /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r13/app/logstats.py, following plan.json exactly: the same imports, constants, function signatures and body structure.

My own checks passed. I ran them once, in a single Bash call, with these results:
- A sample log with a blank line, a malformed line and a repeated ERROR message gave the expected level counts, `2 x db timeout`, and `skipped 2 unreadable line(s)`.
- A nonexistent file printed `error: cannot read nope` and exited 1.
- An empty file printed `No log lines found.`
- Running with no arguments printed the usage line and exited 2.

The scratch files are in the workspace `scratch/` directory. I used 3 tool calls in total.
