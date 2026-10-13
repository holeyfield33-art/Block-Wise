I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r33/app/report.py`, and my own checks passed.

I found `csv_report` with `find` and applied it with `apply csv_report --into app --set file=report`. I then edited the generated file once. The generated `parse_amount` accepted `nan` and `inf` as numbers, which turned totals into `nan`. I added a `math.isfinite` check so those count as 0.

My checks used scratch CSVs in `scratch/`. They covered:
- a blank group, which prints as `(blank)`
- amounts with thousands separators, plus blank and non-numeric amounts
- a missing file (exit 1)
- a missing group column (exit 1)
- a header-only file (prints `total: 0.00`)
- the wrong argument count (exit 2)
- tied totals, which keep file order
- a short row
- a missing amount column, where every group totals 0.00
- `nan` and `inf` amounts

All matched the spec. I ran the checks twice: one batch before the fix, and a re-run of the `nan` and main cases after it. `blockwise check` reported no issues, but it noted that no plan had been applied, so it didn't really check anything.

I used 6 tool calls in total, besides reading the task file.
