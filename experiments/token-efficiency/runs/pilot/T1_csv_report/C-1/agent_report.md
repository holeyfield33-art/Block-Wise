I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/ws/p02/app/report.py`. My own checks passed, and I ran them two rounds (about 8 invocations in total).

I applied the Block-Wise `csv_report` blueprint, which matched the task. The generated code already handled everything in the spec. I made three small hardening edits:
- It now opens the file as `utf-8-sig`, so a leading BOM doesn't break the header.
- `nan` and `inf` amounts count as 0 instead of corrupting the totals.
- Unreadable files (bad encoding or a CSV error) now print `error: cannot read FILE` and exit 1.

Checks I ran in `scratch/`:
- **Mixed file:** a blank group, a thousands-separator amount (`"1,200"`), a non-numeric amount and an empty amount. The groups were ordered correctly and the totals were right.
- **Header-only file:** prints only `total: 0.00` and exits 0.
- **Missing group column:** prints `error: no column nope` and exits 1.
- **Missing file:** prints `error: cannot read missing.csv` and exits 1.
- **Wrong argument count:** prints the usage line and exits 2.
- **Missing amount column:** every group totals 0.00.
- **BOM, `nan`/`inf`, short row, padded and negative amounts:** all handled correctly.

`blockwise check` reported no issues on the first run, which covered the generated functions. After my edits it reported "No plan yet" and checked 0 functions, so the structure check did not re-verify the edited file.
