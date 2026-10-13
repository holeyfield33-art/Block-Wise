I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/ws/p03/app/report.py`. My own checks passed. I ran them in two rounds, with 9 spec cases in the first and 3 re-checks after the edits.

- **How it was built:** I applied the Block-Wise `csv_report` blueprint with `apply csv_report --into app`, then checked it by running it.
- **What I changed:** the template treated `nan` and `inf` amounts as numbers, which printed `nan` or `inf` totals. I made any non-finite amount count as 0. I also made undecodable or unreadable input (a directory, or bad UTF-8) print `error: cannot read FILE` and exit 1.
- **Checks that passed:**
  - The example from the spec.
  - Thousands separators (`"1,200"` is 1200).
  - Blank, missing and non-numeric amounts count as 0, and the row stays in its group.
  - A blank group value shows as `(blank)`.
  - Ties keep their first-seen order.
  - A header-only file prints only `total: 0.00`.
  - A wrong number of arguments prints the usage line and exits 2.
  - A missing file prints the cannot-read error and exits 1.
  - A group column that isn't in the header prints the no-column error and exits 1.
  - An unknown amount column gives 0.00 for every group.
- **Block-Wise `check`:** it reported no issues after my edits. It only checks structure, not behavior.
- **Possible acceptance-test mismatch:** a file with a UTF-8 BOM reports `no column` for the first header, because the spec says plain UTF-8 and I left it that way.
