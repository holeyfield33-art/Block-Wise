I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r01/app/report.py`, and my own checks passed. I ran two rounds of checks, in 2 bash calls (about 7 of the 30 tool calls used).

I found the `csv_report` blueprint with `blockwise find` and applied it with `apply csv_report --into app --set file=report`. I did not read the generated code until after the first checks. After the first round I made three small edits to what Block-Wise wrote:
- **Encoding:** it now opens the file with `utf-8-sig`, so a leading byte-order mark doesn't break the header.
- **Non-finite amounts:** `nan` and `inf` now count as 0.
- **Unreadable files:** a file that isn't valid UTF-8, or a malformed CSV, now prints `error: cannot read FILE` and exits with code 1.

`blockwise check` returned ok before and after the edits. It reported 0 functions checked, so it didn't test anything meaningful.

The checks covered each spec rule:
- **Usage:** a wrong argument count prints the usage line and exits 2.
- **Unreadable file:** a missing file prints `error: cannot read nofile.csv` and exits 1.
- **Missing group column:** it prints the error and exits 1 when there is at least one data row. A header-only file prints `total: 0.00`. A completely empty file prints `error: no column region` and exits 1, which the spec doesn't cover.
- **Mixed data:** a blank group becomes `(blank)`, and `"1,200"` parses as 1200. Blank, missing and non-numeric amounts count as 0 and the row stays in its group. Totals print with 2 decimals and sort largest first, and the grand total is correct.
- **Other inputs:** a negative amount, an amount with surrounding spaces and a missing amount column (all rows 0.00) behaved sensibly.

I didn't test tie ordering for groups with equal totals. The code uses Python's stable sort with `reverse=True`, which keeps first-appearance order for ties.
