I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/ws/p06/app/report.py` and my own checks passed, all in one run (one command, four invocations).

The four invocations covered:
- **Normal report:** a CSV with a blank group, a `"1,200"` amount and a non-numeric amount printed the right groups, totals and grand total.
- **Missing group column:** printed `error: no column x` and exited 1.
- **Unreadable file:** printed `error: cannot read nope` and exited 1.
- **No arguments:** printed the usage line and exited 2.

I did not test the header-only CSV case (`total: 0.00`) or the equal-totals ordering rule.

A few behaviours the spec didn't pin down:
- **Missing amount column:** if the amount column isn't in the header, every amount counts as 0.
- **Short rows:** rows with too few fields count as 0 for the missing amount and fall under `(blank)` for a missing group.
- **Totals:** summed as floats, so rounding follows normal float formatting.
- **Numeric edge cases:** `nan` and `inf` count as 0.
- **File reading:** a UTF-8 BOM is stripped, and a decode error is reported as `cannot read`.
- **Blank lines:** empty lines are skipped.

My test file is `scratch/t.csv`, in the same workspace. Nothing else was written to `app/`.
