I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r34/app/report.py` using the Block-Wise `csv_report` blueprint, applied with `--set file=report`. My own checks passed.

I edited one thing by hand. `parse_amount` accepted `nan` and `inf`, which printed `nan` and `inf` in the report. I changed it so those count as 0, like any other non-numeric value.

I ran the behavioral checks in `scratch/` in two rounds, and `blockwise check` once at the end. It returned `ok` with no issues.
- **Example and amounts:** the `sales.csv` example prints as in the spec. Thousands separators, blank and non-numeric amounts and the `(blank)` group all work.
- **Tie order:** groups with equal totals stay in first-appearance order.
- **Header-only file:** it prints `total: 0.00` even when the group column doesn't exist.
- **Error cases:** the wrong argument count exits 2 with the usage line. An unreadable file exits 1 with `error: cannot read FILE`. A missing group column on a file with data rows exits 1 with `error: no column ...`.
- **Missing amount column:** a column name that isn't in the header gives all-zero totals.
- **Short rows:** a row with fewer fields than the header counts as 0.
- **`nan`/`inf` fix:** I re-ran the `nan`/`inf` file and the main sample after the edit, and both gave the expected output.
