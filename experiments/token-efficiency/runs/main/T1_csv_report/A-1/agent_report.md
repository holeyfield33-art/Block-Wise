I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r56/app/report.py`, and my own check passed on the one run I did.

That run used a few small CSVs I made in `scratch/`. It covered:
- A normal report, including a comma amount (`"1,200"`), a non-numeric amount, a blank group and a short row.
- A header-only file.
- A missing group column.
- An unreadable file.
- A wrong number of arguments.

Every output and exit code matched the spec.

Floats are used for the sums and 2-decimal formatting. A value like 2.675 can therefore round the way Python floats do, not the way decimals would.

I also made the program treat NaN and infinity as 0, skip fully blank lines, and accept a UTF-8 BOM. The spec doesn't cover these, so they are my own choices.
