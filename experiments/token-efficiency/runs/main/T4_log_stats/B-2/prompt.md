You are the coding agent for one run of a controlled benchmark.

Workspace: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r13
- Work ONLY inside the workspace. Do not read, list or search anything outside it; other runs and
  evaluation files exist on this machine and looking at them invalidates the run.
- Deliverable: the program file /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r13/app/logstats.py. Put nothing else you write in app/ except files a
  tool you were told to use creates there.
- You may write and run your own checks in /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r13/scratch/.
- Python: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/plainvenv/bin/python . Do not install packages. No network access.
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

## Structured plan (Block-Wise plan.json)

The program must follow this plan exactly: same module, imports, constants, functions (names,
typed parameters, return types) and body structure. Element kinds: `branch` = if/else
(`otherwise` is the else part), `loop` = for, `while`, `try` (with `handler` = except), `with`,
`assign`, `call` = an expression statement, `validate` = a call that checks input, `return`,
`raise`; `entry` is the module's main block (`if __name__ == '__main__':`). Write the Python
yourself; no Block-Wise tool is available.

```json
{
 "format": "blockwise-plan-v1",
 "title": "Log file summary",
 "modules": [
  {
   "path": "logstats.py",
   "imports": [
    "import sys"
   ],
   "constants": [
    {
     "name": "LEVELS",
     "value": "('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')"
    },
    {
     "name": "TOP",
     "value": "3"
    }
   ],
   "functions": [
    {
     "name": "parse_line",
     "parameters": [
      {
       "name": "line",
       "type": "str"
      }
     ],
     "returns": "dict | None",
     "requirements": [
      "Expected shape: DATE TIME LEVEL message"
     ],
     "body": [
      {
       "kind": "assign",
       "target": "parts",
       "expression": "line.split(maxsplit=3)",
       "operator": "="
      },
      {
       "kind": "branch",
       "condition": "len(parts) < 4 or parts[2] not in LEVELS",
       "body": [
        {
         "kind": "return",
         "expression": "None"
        }
       ],
       "otherwise": []
      },
      {
       "kind": "return",
       "expression": "{'level': parts[2], 'message': parts[3].strip()}"
      }
     ]
    },
    {
     "name": "summarize",
     "parameters": [
      {
       "name": "lines",
       "type": "list"
      }
     ],
     "returns": "dict",
     "body": [
      {
       "kind": "assign",
       "target": "counts",
       "expression": "{level: 0 for level in LEVELS}",
       "operator": "="
      },
      {
       "kind": "assign",
       "target": "errors",
       "expression": "{}",
       "operator": "="
      },
      {
       "kind": "assign",
       "target": "skipped",
       "expression": "0",
       "operator": "="
      },
      {
       "kind": "loop",
       "target": "line",
       "iterable": "lines",
       "body": [
        {
         "kind": "assign",
         "target": "entry",
         "expression": "parse_line(line)",
         "operator": "="
        },
        {
         "kind": "branch",
         "condition": "entry is None",
         "body": [
          {
           "kind": "assign",
           "target": "skipped",
           "operator": "+=",
           "expression": "1"
          },
          {
           "kind": "continue"
          }
         ],
         "otherwise": []
        },
        {
         "kind": "call",
         "expression": "counts.update({entry['level']: counts[entry['level']] + 1})"
        },
        {
         "kind": "branch",
         "condition": "entry['level'] in ('ERROR', 'CRITICAL')",
         "body": [
          {
           "kind": "call",
           "expression": "errors.update({entry['message']: errors.get(entry['message'], 0) + 1})"
          }
         ],
         "otherwise": []
        }
       ]
      },
      {
       "kind": "return",
       "expression": "{'counts': counts, 'errors': errors, 'skipped': skipped}"
      }
     ],
     "requirements": []
    },
    {
     "name": "format_summary",
     "parameters": [
      {
       "name": "summary",
       "type": "dict"
      }
     ],
     "returns": "str",
     "body": [
      {
       "kind": "assign",
       "target": "lines",
       "expression": "[f'{level}: {count}' for level, count in summary['counts'].items() if count]",
       "operator": "="
      },
      {
       "kind": "assign",
       "target": "errors",
       "expression": "summary['errors']",
       "operator": "="
      },
      {
       "kind": "loop",
       "target": "message",
       "iterable": "sorted(errors, key=errors.get, reverse=True)[:TOP]",
       "body": [
        {
         "kind": "call",
         "expression": "lines.append(f'  {errors[message]} x {message}')"
        }
       ]
      },
      {
       "kind": "branch",
       "condition": "summary['skipped']",
       "body": [
        {
         "kind": "call",
         "expression": "lines.append(f\"skipped {summary['skipped']} unreadable line(s)\")"
        }
       ],
       "otherwise": []
      },
      {
       "kind": "return",
       "expression": "'\\n'.join(lines) or 'No log lines found.'"
      }
     ],
     "requirements": []
    },
    {
     "name": "main",
     "parameters": [
      {
       "name": "args",
       "type": "list"
      }
     ],
     "returns": "int",
     "body": [
      {
       "kind": "branch",
       "condition": "len(args) != 1",
       "body": [
        {
         "kind": "call",
         "expression": "print('usage: logstats.py LOGFILE')"
        },
        {
         "kind": "return",
         "expression": "2"
        }
       ],
       "otherwise": []
      },
      {
       "kind": "try",
       "exception": "OSError",
       "body": [
        {
         "kind": "with",
         "context": "open(args[0], encoding='utf-8', errors='replace')",
         "alias": "handle",
         "body": [
          {
           "kind": "assign",
           "target": "lines",
           "expression": "handle.readlines()",
           "operator": "="
          }
         ]
        }
       ],
       "handler": [
        {
         "kind": "call",
         "expression": "print(f'error: cannot read {args[0]}')"
        },
        {
         "kind": "return",
         "expression": "1"
        }
       ],
       "alias": "",
       "finally": []
      },
      {
       "kind": "call",
       "expression": "print(format_summary(summarize(lines)))"
      },
      {
       "kind": "return",
       "expression": "0"
      }
     ],
     "requirements": []
    }
   ],
   "entry": [
    {
     "kind": "call",
     "expression": "sys.exit(main(sys.argv[1:]))"
    }
   ]
  }
 ],
 "requirements": []
}
```