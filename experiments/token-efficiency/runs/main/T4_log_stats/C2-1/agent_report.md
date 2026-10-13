I wrote `app/logstats.py` by applying the Block-Wise `log_stats` blueprint into `app`, with one hand edit. My own checks passed. I ran them in 3 batches, and the first batch covered several cases.

The edit: the template counted trailing blank lines as skipped. I added a loop that drops trailing blank lines after reading the file. I read the spec's "blank lines in the middle" as meaning trailing ones aren't counted, but that is my interpretation. Blank lines in the middle still count as skipped.

The checks, using sample logs in `scratch/`:
- **Normal output:** level counts, the top-3 error/CRITICAL messages, and `skipped N unreadable line(s)` were correct. Tie order followed first appearance.
- **Bad lines:** lowercase levels, a missing message, blank lines in the middle, and a line with too few fields were all skipped.
- **Empty file:** it prints `No log lines found.`
- **Missing file:** it prints `error: cannot read nope.log` and exits 1.
- **Wrong argument count:** zero or two arguments print the usage line and exit 2.
- **Trailing blanks:** a file ending in blank lines, and a file of only blank lines, behaved as intended.

Two Block-Wise runs: `blockwise check` reported no issues after the template was applied. After my edit it returned `ok` with "No plan yet; apply a preset first.", so it didn't re-check the edited file.

File written: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r41/app/logstats.py
