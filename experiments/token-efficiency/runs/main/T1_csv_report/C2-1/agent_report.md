I wrote `app/report.py` by running `blockwise apply csv_report --into app`, and I didn't edit it. The workspace is `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r42`.

`blockwise check` passed with no issues. I also ran my own behavioral checks once, in a single batch of 7 invocations, and all matched the spec:
- **Example:** the sales example from the spec prints the expected output.
- **Messy amounts:** thousands separators, blank groups (shown as `(blank)`), non-numeric amounts, missing fields and tie ordering all came out as specified.
- **Edge cases:** a header-only file prints `total: 0.00`, and an unknown group column on a file with data rows prints `error: no column nope`.
- **Exit codes:** a missing file exits 1 with the "cannot read" message, and a wrong argument count prints the usage line and exits 2.

The check files are in `scratch/`. I used 3 tool calls in total.
