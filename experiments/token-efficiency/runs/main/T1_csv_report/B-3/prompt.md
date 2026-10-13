You are the coding agent for one run of a controlled benchmark.

Workspace: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r32
- Work ONLY inside the workspace. Do not read, list or search anything outside it; other runs and
  evaluation files exist on this machine and looking at them invalidates the run.
- Deliverable: the program file /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r32/app/report.py. Put nothing else you write in app/ except files a
  tool you were told to use creates there.
- You may write and run your own checks in /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r32/scratch/.
- Python: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/plainvenv/bin/python . Do not install packages. No network access.
- Budget: at most 30 tool calls. There is one attempt. Hidden acceptance tests will run
  `python app/report.py ...` from a fresh temporary directory after you finish.
- End with a short report: files written, whether your own checks passed, how many times you ran them.

## Specification

# Task: CSV group-and-total report

Write a command-line program `report.py` (Python 3.11+, standard library only).

## Usage

    python report.py FILE GROUP_COLUMN AMOUNT_COLUMN

## Behavior

1. With any number of arguments other than exactly 3, print
   `usage: report.py FILE GROUP_COLUMN AMOUNT_COLUMN` and exit with code 2.
2. Read FILE as a UTF-8 CSV whose first row is the header. If the file cannot be opened, print
   `error: cannot read FILE` (with the given file name) and exit with code 1.
3. If the CSV has at least one data row and GROUP_COLUMN is not one of its header names, print
   `error: no column GROUP_COLUMN` and exit with code 1.
4. Group the data rows by the value in GROUP_COLUMN. A blank (empty) group value is grouped under the
   label `(blank)`.
5. For each row, parse the AMOUNT_COLUMN value as a number. Commas are thousands separators and are
   removed before parsing (`"1,200"` is 1200). A blank, missing or non-numeric amount counts as 0, and
   the row still belongs to its group.
6. Print one line per group, `GROUP: TOTAL`, with TOTAL formatted to exactly 2 decimal places,
   ordered by total from largest to smallest (groups with equal totals keep the order in which they
   first appear in the file).
7. Finally print `total: GRAND_TOTAL` (2 decimal places), the sum of all group totals. A CSV with a
   header but no data rows prints only `total: 0.00`.
8. Exit with code 0 after a successful report.

## Example

`sales.csv`:

    region,amount
    north,10
    south,5.5

`python report.py sales.csv region amount` prints:

    north: 10.00
    south: 5.50
    total: 15.50

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
 "title": "CSV report: group and total",
 "modules": [
  {
   "path": "report.py",
   "imports": [
    "import csv",
    "import sys"
   ],
   "functions": [
    {
     "name": "read_rows",
     "parameters": [
      {
       "name": "path",
       "type": "str"
      }
     ],
     "returns": "list",
     "body": [
      {
       "kind": "with",
       "context": "open(path, newline='', encoding='utf-8')",
       "alias": "handle",
       "body": [
        {
         "kind": "return",
         "expression": "list(csv.DictReader(handle))"
        }
       ]
      }
     ],
     "requirements": []
    },
    {
     "name": "parse_amount",
     "parameters": [
      {
       "name": "text",
       "type": "str"
      }
     ],
     "returns": "float",
     "requirements": [
      "Commas are thousands separators; anything that isn't a number counts as 0."
     ],
     "body": [
      {
       "kind": "try",
       "exception": "ValueError",
       "body": [
        {
         "kind": "return",
         "expression": "float(text.replace(',', ''))"
        }
       ],
       "handler": [
        {
         "kind": "return",
         "expression": "0.0"
        }
       ],
       "alias": "",
       "finally": []
      }
     ]
    },
    {
     "name": "totals_by",
     "parameters": [
      {
       "name": "rows",
       "type": "list"
      },
      {
       "name": "group",
       "type": "str"
      },
      {
       "name": "amount",
       "type": "str"
      }
     ],
     "returns": "dict",
     "body": [
      {
       "kind": "assign",
       "target": "totals",
       "expression": "{}",
       "operator": "="
      },
      {
       "kind": "loop",
       "target": "row",
       "iterable": "rows",
       "body": [
        {
         "kind": "assign",
         "target": "key",
         "expression": "row.get(group) or '(blank)'",
         "operator": "="
        },
        {
         "kind": "call",
         "expression": "totals.update({key: totals.get(key, 0.0) + parse_amount(row.get(amount) or '')})"
        }
       ]
      },
      {
       "kind": "return",
       "expression": "totals"
      }
     ],
     "requirements": []
    },
    {
     "name": "format_report",
     "parameters": [
      {
       "name": "totals",
       "type": "dict"
      }
     ],
     "returns": "str",
     "body": [
      {
       "kind": "assign",
       "target": "lines",
       "expression": "[]",
       "operator": "="
      },
      {
       "kind": "loop",
       "target": "key",
       "iterable": "sorted(totals, key=totals.get, reverse=True)",
       "body": [
        {
         "kind": "call",
         "expression": "lines.append(f'{key}: {totals[key]:.2f}')"
        }
       ]
      },
      {
       "kind": "call",
       "expression": "lines.append(f'total: {sum(totals.values()):.2f}')"
      },
      {
       "kind": "return",
       "expression": "'\\n'.join(lines)"
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
     "requirements": [
      "Usage: FILE GROUP_COLUMN AMOUNT_COLUMN. Returns the exit code."
     ],
     "body": [
      {
       "kind": "branch",
       "condition": "len(args) != 3",
       "body": [
        {
         "kind": "call",
         "expression": "print('usage: report.py FILE GROUP_COLUMN AMOUNT_COLUMN')"
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
         "kind": "assign",
         "target": "rows",
         "expression": "read_rows(args[0])",
         "operator": "="
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
       "kind": "branch",
       "condition": "rows and args[1] not in rows[0]",
       "body": [
        {
         "kind": "call",
         "expression": "print(f'error: no column {args[1]}')"
        },
        {
         "kind": "return",
         "expression": "1"
        }
       ],
       "otherwise": []
      },
      {
       "kind": "call",
       "expression": "print(format_report(totals_by(rows, args[1], args[2])))"
      },
      {
       "kind": "return",
       "expression": "0"
      }
     ]
    }
   ],
   "entry": [
    {
     "kind": "call",
     "expression": "sys.exit(main(sys.argv[1:]))"
    }
   ],
   "constants": []
  }
 ],
 "requirements": []
}
```