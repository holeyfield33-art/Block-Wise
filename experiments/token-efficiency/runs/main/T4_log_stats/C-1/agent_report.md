Files written: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r49/app/logstats.py. It was created by `blockwise apply log_stats --into app` and I did not edit it. `blockwise check` reported no issues.

My own checks passed, and I ran them once, as a single batch. Test files are in the workspace scratch/ directory (a.log, b.log, e.log, s.log).

What the batch covered:
- The spec example.
- A mixed file with tied message counts, which kept first-appearance order.
- Unreadable lines: blank, whitespace-only, lowercase level, three fields only, and an invalid byte in the level.
- Empty file, which printed "No log lines found."
- A file with only unreadable lines, which printed only the skipped count.
- Missing file, which printed the error and exited 1.
- Zero arguments and two arguments, which printed the usage line and exited 2.

All of these matched the spec. I did not test a file that fails with something other than not found, such as a directory path.
