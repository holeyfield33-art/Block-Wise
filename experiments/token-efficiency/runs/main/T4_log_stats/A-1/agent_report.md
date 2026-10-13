I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r35/app/logstats.py`, and my own checks passed. I ran them once, in a single batch of 4 invocations.

The checks covered:
- a mixed log with blank and bad lines
- an empty file
- a missing file
- no arguments

Counts, top-message ordering, skipped lines and the exit codes 0, 1 and 2 all came out as the spec says. The test log is `scratch/a.log`; the empty file is `scratch/e.log`.

I read two ambiguous points in the spec this way:
- **Trailing newline:** the empty piece after the final newline is not counted as a skipped line.
- **Other blank lines:** every other blank line is skipped, including blank lines at the very end of the file.
