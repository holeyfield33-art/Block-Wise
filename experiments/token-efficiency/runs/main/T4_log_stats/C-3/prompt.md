You are the coding agent for one run of a controlled benchmark.

Workspace: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r51
- Work ONLY inside the workspace. Do not read, list or search anything outside it; other runs and
  evaluation files exist on this machine and looking at them invalidates the run.
- Deliverable: the program file /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r51/app/logstats.py. Put nothing else you write in app/ except files a
  tool you were told to use creates there.
- You may write and run your own checks in /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r51/scratch/.
- Python: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/python . Do not install packages. No network access.
- Budget: at most 30 tool calls. There is one attempt. Hidden acceptance tests will run
  `python app/logstats.py ...` from a fresh temporary directory after you finish.
- End with a short report: files written, whether your own checks passed, how many times you ran them.

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

## Tool available: Block-Wise

Block-Wise is installed: run it as `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/blockwise <command>` from the workspace directory /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r51. Every command
prints one compact JSON line. Commands:
- `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/blockwise find <words>`: the 3 best-matching presets/blueprints for a few words
- `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/blockwise list [--category validation|auth|data|files|blueprint]`
- `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/blockwise show <id> [--set k=v ...]`: the code a preset or blueprint would write (not written to disk)
- `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/blockwise apply <id> --into <file.py or folder> [--set k=v ...]`: writes it (blueprints take a folder)
- `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/blockwise check`: structure check of everything applied
Exit codes: 0 ok, 1 check found issues, 2 bad input.

Rules for using it (adapted from the project's docs/agent-instructions.md):
1. Before writing a small, common Python function or a small command-line tool, search with `find`.
2. If a result fits, `apply` it with the right names. Don't re-type code a preset provides. Do not
   print or read generated code unless your own checks fail and you need it to fix a problem.
3. If the result lists a `todo`, fill only that part. After editing files Block-Wise wrote, run `check`.
4. Block-Wise checks structure, not behavior: still run your own behavioral checks.
If nothing fits, write the code normally. Don't force a preset that doesn't match the task.