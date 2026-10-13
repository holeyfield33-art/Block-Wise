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
