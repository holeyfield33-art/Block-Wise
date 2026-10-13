I wrote `app/report.py` by running `blockwise apply csv_report --into app`, and I did not edit the generated code.

My checks passed. I ran them once, as a single batch of 9 CLI runs plus one `blockwise check`, and `check` reported no issues.

The cases I ran:
- **Basic report:** the spec example prints the expected output.
- **Messy data:** thousands commas, a blank group (shown as `(blank)`), non-numeric, blank and missing amounts, and a negative amount all behaved as specified.
- **Ordering:** groups sort by total, largest first, and ties keep file order.
- **Header-only CSV:** prints just `total: 0.00`.
- **Errors:** an unknown group column gives `error: no column region` with exit 1, an unreadable file gives `error: cannot read FILE` with exit 1, and a wrong argument count prints the usage line with exit 2.
- **Amount column not in the header:** all amounts count as 0.

The generated file is `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r30/app/report.py`. My check files are in `scratch/`.
