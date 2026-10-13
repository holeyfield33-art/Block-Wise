You are the coding agent for one run of a controlled benchmark.

Workspace: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/ws002/t04
- Work ONLY inside the workspace. Do not read, list or search anything outside it; other runs and
  evaluation files exist on this machine and looking at them invalidates the run.
- Deliverable: the program file /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/ws002/t04/app/logstats.py. Put nothing else in app/.
- Python: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/python . Do not install packages. No network access.
- Budget: at most 5 tool calls. There is one attempt. Hidden acceptance tests will run
  `python app/logstats.py ...` from a fresh temporary directory after you finish; you will not see them.
- End with a short completion record: files written and the generation response.

## Specification

# Task: log statistics

Write a command-line program `logstats.py` (Python 3.11+, standard library only).

## Usage

    python logstats.py LOGFILE

## Behavior

1. With any number of arguments other than exactly 1, print `usage: logstats.py LOGFILE` and exit
   with code 2.
2. Read LOGFILE as UTF-8 text (replace undecodable bytes rather than failing). If it cannot be opened,
   print `error: cannot read LOGFILE` (the given name) and exit with code 1.
3. A valid line has at least four whitespace-separated fields: `DATE TIME LEVEL MESSAGE...`, where
   LEVEL is exactly one of `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`, and the message is the rest
   of the line after LEVEL with surrounding whitespace removed. Every other line, including blank lines
   in the middle of the file, is unreadable and is skipped.
4. Print the number of lines per level as `LEVEL: COUNT`, in the order DEBUG, INFO, WARNING, ERROR,
   CRITICAL, leaving out levels with a count of 0.
5. Then list the most frequent messages of ERROR and CRITICAL lines combined: up to 3 lines, each as
   two spaces, the count, ` x `, and the message (`  2 x db timeout`), ordered by count from highest to
   lowest; messages with equal counts keep the order in which they first appear.
6. If any lines were skipped, finish with `skipped N unreadable line(s)`.
7. If nothing at all would be printed (for example, an empty file), print `No log lines found.`
8. Exit with code 0 after printing the summary.

## Example

`app.log`:

    2026-10-12 09:00:00 INFO started
    2026-10-12 09:00:01 ERROR db timeout

`python logstats.py app.log` prints:

    INFO: 1
    ERROR: 1
      1 x db timeout

## Approved component: Block-Wise blueprint `log_stats`

This specification is implemented by the approved, previously tested Block-Wise blueprint `log_stats`
(blueprint file sha256 80c2fbbff44d5b05989c34d980e1d9bca38fca3bada9397be14870f97fec31c7). Delegate the implementation to it:

    cd /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/ws002/t04 && /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/blockwise apply log_stats --into app

Trust rules for this run:
1. The blueprint is an approved component that already passes its acceptance tests.
2. Run the command above once. A response with `"ok":true` means the task is complete.
3. Do not open, read, print or inspect any generated file.
4. Do not rewrite, improve or extend the generated code.
5. Do not run `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/blockwise check`.
6. Do not run the program, tests or any debugging.
7. Do not run `apply` again after a successful response.
8. Do not write documentation or any other file.
9. If the response is not `"ok":true`, stop and report the response; do not try to fix it.
10. Finish with the file path(s) from the response and the response line itself.