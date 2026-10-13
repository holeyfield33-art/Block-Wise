I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r51/app/logstats.py`. My own checks passed, and I ran them in 3 batches of shell commands.

- **Source:** I applied Block-Wise's `log_stats` blueprint into `app/`, so `app/logstats.py` is that generated code plus one change. `blockwise check` passed on the generated file. I did not run it again after my edit, because the output said "No plan yet" and checked 0 functions.
- **My change:** I drop trailing blank lines before counting, so a file ending in blank lines does not report them as skipped. I read "blank lines in the middle" as meaning trailing ones should not count, and the spec leaves that open. A file containing only blank lines prints `No log lines found.`
- **Checks run:**
  - Mixed levels and ERROR/CRITICAL message ties, which kept first-appearance order.
  - Messages with extra whitespace.
  - Lowercase or unknown levels, lines with fewer than 4 fields, and a stray `\xff` byte.
  - An empty file.
  - A missing file, which printed `error: cannot read nofile` with exit code 1.
  - Zero arguments and two arguments, which printed the usage line with exit code 2.
  - A file with only unreadable lines, which printed just the skipped line.
- **Result:** all output matched the spec and the exit code was 0 on success.
- **Scratch files:** my test logs are in `scratch/`.
