I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r12/app/report.py`, and my own checks passed. I ran them once, as a single batch of 5 invocations, using test files in `scratch/`.

Those runs covered:
- the normal report, including a `"1,200"` amount, a blank group and a non-numeric amount;
- a header-only file, which prints only `total: 0.00`;
- a missing group column, which prints `error: no column q` and exits 1;
- an unreadable file, which prints `error: cannot read nope.csv` and exits 1;
- no arguments, which prints the usage line and exits 2.

The spec left three points open, so I made these choices:
- **Rounding:** totals use Python floats, so 2-decimal rounding follows float behaviour rather than decimal half-up. A reference built on Decimal could differ on values like 2.675.
- **Amount parsing:** `nan`, `inf` and amounts containing `_` count as 0.
- **Short rows:** a row missing the group column goes under `(blank)`, and a row missing the amount column counts as 0.

A UTF-8 BOM at the start of the file is stripped.
