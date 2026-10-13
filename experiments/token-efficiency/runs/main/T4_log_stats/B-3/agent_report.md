I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r28/app/logstats.py`, following the plan's imports, constants, functions and body structure.

My own checks passed. I ran them once, as a single batch, by hand against two small test files (`a.log` and an empty `e.log`) in `scratch/`, and read the output myself. They covered:
- **Mixed file:** per-level counts, the top error messages (with a tie broken by first appearance), and the skipped-line count for a blank line and a bad line.
- **Empty file:** it printed `No log lines found.`
- **Missing file:** it printed the error message and exited with 1.
- **No arguments:** it printed the usage message and exited with 2.

The exit code 0 case was also checked, but only on the mixed file. I did not write a separate test script. I used 6 tool calls in total.
