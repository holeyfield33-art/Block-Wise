I wrote `app/logstats.py` in the r03 workspace (full path: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r03/app/logstats.py).

My own checks passed, and I ran them once, in a single batch. They covered:
- a mixed log (valid lines, a bad line, a blank line in the middle, trailing blank lines)
- an empty file
- a missing file
- no arguments

Each case printed the expected output and exit code.

Two spec gaps I had to decide:
- Trailing blank lines at the end of the file are not counted as skipped. Only blank lines in the middle count.
- Message counting strips surrounding whitespace, so `db timeout  ` and `db timeout` count as the same message.

I also left a sample log, `t.log`, and an empty file, `e.log`, in `scratch/`.
