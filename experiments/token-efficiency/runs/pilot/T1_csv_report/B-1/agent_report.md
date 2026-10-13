I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/ws/p01/app/report.py`, following the plan exactly: same imports, function names, typed parameters, return types and body structure, with the `__main__` entry block.

My own checks passed. I ran them once, as a single batch of 5 invocations: normal report with a blank group, comma amount and non-numeric amount; header-only file; missing group column; unreadable file; and no arguments. Exit codes and output matched the spec in every case.

The only other file I created is the check data in `scratch/` (`s.csv` and `h.csv`). I used 2 tool calls.
