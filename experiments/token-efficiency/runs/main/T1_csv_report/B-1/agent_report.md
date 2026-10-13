I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r54/app/report.py`, following the plan exactly. It has the same imports, functions, signatures, body structure and entry block.

I ran my own checks once, as a single batch of 5 commands, and they all passed:
- A normal file with a blank group, a comma-separated amount (`"1,200"`) and a non-numeric amount produced the correct sorted report and exit code 0.
- A header-only file printed `total: 0.00` with exit code 0.
- A missing group column printed `error: no column foo` with exit code 1.
- A nonexistent file printed `error: cannot read nope.csv` with exit code 1.
- Running with no arguments printed the usage line with exit code 2.

The check files are in `scratch/`. I didn't test equal totals, so the first-appearance tie order isn't checked.
