I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r38/app/report.py`, and my own checks passed. I ran them 3 times (about 10 cases in the first run, 2 more cases after the edit, plus a re-run of the earlier cases).

**How it was built:** I applied the `csv_report` template with `blockwise apply csv_report --into app`. I then made two edits to the generated code:
- It now reads the file as `utf-8-sig`, so a UTF-8 byte-order mark doesn't break the header lookup. With plain `utf-8`, a BOM file reported "no column g".
- `nan` and `inf` amounts now count as 0 instead of being parsed as numbers.

**What I checked, all as expected:**
- The example from the spec.
- Thousands separators, blank and non-numeric amounts, and a `(blank)` group.
- Equal totals keeping first-seen order, and a negative amount.
- A header-only file and an empty file, which print only `total: 0.00`.
- A missing group column (exit 1), a missing file (exit 1), and the wrong number of arguments (exit 2).
- An amount column that doesn't exist, which counts every amount as 0.

`blockwise check` reported ok with no issues, though it only checks structure.
