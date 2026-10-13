I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r32/app/report.py` and my checks passed. I ran them once, in a single batch. The program follows the plan exactly: same imports, the five functions with their typed signatures, and the entry block.

The batch ran four cases against a small CSV in `scratch/` (`s.csv`):
- **Normal report:** the output was `(blank): 1200.00`, `north: 10.00`, `south: 5.50` and `total: 1215.50`, with exit code 0. That covers the blank group label, the thousands comma and the non-numeric amount counting as 0.
- **Unknown group column:** printed `error: no column x` and exited 1.
- **Missing file:** printed `error: cannot read nope` and exited 1.
- **No arguments:** printed the usage line and exited 2.

I did not test a header-only CSV, equal totals, or a missing amount column.
