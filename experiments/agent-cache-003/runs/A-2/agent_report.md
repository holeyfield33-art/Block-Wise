All four programs are written in /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/ws003/s08/app/, and app/ holds nothing else. I ran each once from scratch/ with the plainvenv Python on small test inputs, and the output matched the spec. I did not test every branch.

- **report.py:**
  - A CSV with `(blank)` and `north` groups and a non-numeric amount printed `(blank): 1200.00`, `north: 10.00`, `south: 5.50`, `total: 1215.50`, so comma stripping, `(blank)` grouping, non-numeric amounts counting as 0 and the sort all worked.
  - `error: no column zz` exited 1, and an unreadable file printed `error: cannot read nofile` and exited 1.
  - Calling it with no arguments printed the usage line. I did not check that this exits 2, only the output.
- **todo.py:**
  - `add` printed `Added.`; an empty add printed the error and exited 1; `done 1` printed `Marked done.`; and `done 3` printed `error: no item 3` and exited 1.
  - `list` printed `1. [x] buy milk`, and the no-argument run on a missing `todo.json` printed `Nothing to do.`.
  - An unknown command printed the usage line and exited 2.
- **store.py:**
  - The empty store printed `(empty)`, and `set`, `get`, `list` (sorted by key) and `delete` all worked.
  - `get` on a missing key printed `error: no key b` and exited 1, and `set a` with a missing value printed the usage line and exited 2.
- **logstats.py:**
  - On a test log with two ERROR lines, one CRITICAL, one INFO, a blank line and a garbage line, it printed `INFO: 1`, `ERROR: 2`, `CRITICAL: 1`, `  2 x db timeout`, `  1 x x y` and `skipped 2 unreadable line(s)`. An empty file printed `No log lines found.`.
  - I did not run the wrong-argument-count or unreadable-file cases.

Where the spec was ambiguous, I made these choices:
- **logstats.py:** blank lines at the very end of a log are not counted as skipped; blank lines in the middle are.
- **todo.py:** `done` without exactly one argument prints the usage line and exits 2.
- **report.py:** it accepts a UTF-8 byte order mark at the start of the file.
