I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r47/app/report.py`, following the plan's functions, imports, bodies and entry block exactly. My own checks passed, and I ran them once, as a single batch of 6 invocations.

The checks used test CSVs in `scratch/`:
- **Normal report:** a file with a blank group, `"1,200"` and a non-numeric amount printed the groups sorted largest to smallest, the blank group as `(blank)`, and the correct grand total.
- **Header-only file:** printed only `total: 0.00`.
- **Missing group column:** printed `error: no column zz` and exited 1.
- **Unreadable file:** printed `error: cannot read nope` and exited 1.
- **No arguments:** printed the usage line and exited 2.

I did not separately test the tie-ordering rule (equal totals keep first-appearance order). The plan's `sorted(..., reverse=True)` is stable, so it should hold.
