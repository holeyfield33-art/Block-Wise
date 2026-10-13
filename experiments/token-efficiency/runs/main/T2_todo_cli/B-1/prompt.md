You are the coding agent for one run of a controlled benchmark.

Workspace: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r17
- Work ONLY inside the workspace. Do not read, list or search anything outside it; other runs and
  evaluation files exist on this machine and looking at them invalidates the run.
- Deliverable: the program file /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r17/app/todo.py. Put nothing else you write in app/ except files a
  tool you were told to use creates there.
- You may write and run your own checks in /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r17/scratch/.
- Python: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/plainvenv/bin/python . Do not install packages. No network access.
- Budget: at most 30 tool calls. There is one attempt. Hidden acceptance tests will run
  `python app/todo.py ...` from a fresh temporary directory after you finish.
- End with a short report: files written, whether your own checks passed, how many times you ran them.

## Specification

# Task: to-do list command-line app

Write a command-line program `todo.py` (Python 3.11+, standard library only). It keeps its items in
the file `todo.json` in the current working directory, so items persist between runs.

## Usage

    python todo.py [list | add TEXT | done NUMBER]

## Behavior

1. `list`, or no arguments at all: print the items, numbered from 1 in the order they were added, one
   per line as `N. [x] TEXT` for a done item or `N. [ ] TEXT` for an open item. With no items print
   `Nothing to do.`
2. `add TEXT...`: all remaining arguments are joined with single spaces and stripped of surrounding
   whitespace to form the text. If the text is empty, print `error: text must not be empty` and exit
   with code 1 (nothing is saved). Otherwise append it as an open item, save, and print `Added.`
3. `done NUMBER`: mark item NUMBER (1-based) as done, save, and print `Marked done.` If there is no
   such item, print `error: no item NUMBER` and exit with code 1.
4. Any other command: print `usage: todo.py [list | add TEXT | done NUMBER]` and exit with code 2.
5. If `todo.json` is missing or does not contain valid JSON, treat the list as empty.
6. Successful commands exit with code 0.

## Example

    $ python todo.py add buy milk
    Added.
    $ python todo.py list
    1. [ ] buy milk

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
 "title": "Command-line to-do list",
 "modules": [
  {
   "path": "todo.py",
   "imports": [
    "import json",
    "import sys"
   ],
   "constants": [
    {
     "name": "STORE",
     "value": "'todo.json'"
    }
   ],
   "functions": [
    {
     "name": "load_items",
     "parameters": [
      {
       "name": "path",
       "type": "str"
      }
     ],
     "returns": "list",
     "requirements": [
      "A missing or broken file means an empty list."
     ],
     "body": [
      {
       "kind": "try",
       "exception": "(OSError, ValueError)",
       "body": [
        {
         "kind": "with",
         "context": "open(path, encoding='utf-8')",
         "alias": "handle",
         "body": [
          {
           "kind": "return",
           "expression": "json.load(handle)"
          }
         ]
        }
       ],
       "handler": [
        {
         "kind": "return",
         "expression": "[]"
        }
       ],
       "alias": "",
       "finally": []
      }
     ]
    },
    {
     "name": "save_items",
     "parameters": [
      {
       "name": "path",
       "type": "str"
      },
      {
       "name": "items",
       "type": "list"
      }
     ],
     "returns": "None",
     "body": [
      {
       "kind": "with",
       "context": "open(path, 'w', encoding='utf-8')",
       "alias": "handle",
       "body": [
        {
         "kind": "call",
         "expression": "json.dump(items, handle, indent=2)"
        }
       ]
      }
     ],
     "requirements": []
    },
    {
     "name": "add_item",
     "parameters": [
      {
       "name": "items",
       "type": "list"
      },
      {
       "name": "text",
       "type": "str"
      }
     ],
     "returns": "list",
     "body": [
      {
       "kind": "branch",
       "condition": "not text.strip()",
       "body": [
        {
         "kind": "raise",
         "expression": "ValueError('text must not be empty')"
        }
       ],
       "otherwise": []
      },
      {
       "kind": "call",
       "expression": "items.append({'text': text.strip(), 'done': False})"
      },
      {
       "kind": "return",
       "expression": "items"
      }
     ],
     "requirements": []
    },
    {
     "name": "complete_item",
     "parameters": [
      {
       "name": "items",
       "type": "list"
      },
      {
       "name": "number",
       "type": "int"
      }
     ],
     "returns": "list",
     "body": [
      {
       "kind": "branch",
       "condition": "number < 1 or number > len(items)",
       "body": [
        {
         "kind": "raise",
         "expression": "IndexError(f'no item {number}')"
        }
       ],
       "otherwise": []
      },
      {
       "kind": "call",
       "expression": "items[number - 1].update(done=True)"
      },
      {
       "kind": "return",
       "expression": "items"
      }
     ],
     "requirements": []
    },
    {
     "name": "format_items",
     "parameters": [
      {
       "name": "items",
       "type": "list"
      }
     ],
     "returns": "str",
     "body": [
      {
       "kind": "branch",
       "condition": "not items",
       "body": [
        {
         "kind": "return",
         "expression": "'Nothing to do.'"
        }
       ],
       "otherwise": []
      },
      {
       "kind": "assign",
       "target": "lines",
       "expression": "[]",
       "operator": "="
      },
      {
       "kind": "assign",
       "target": "number",
       "expression": "0",
       "operator": "="
      },
      {
       "kind": "loop",
       "target": "item",
       "iterable": "items",
       "body": [
        {
         "kind": "assign",
         "target": "number",
         "operator": "+=",
         "expression": "1"
        },
        {
         "kind": "assign",
         "target": "mark",
         "expression": "'x' if item['done'] else ' '",
         "operator": "="
        },
        {
         "kind": "call",
         "expression": "lines.append(str(number) + '. [' + mark + '] ' + item['text'])"
        }
       ]
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
      "Commands: list, add TEXT, done NUMBER. Returns the exit code."
     ],
     "body": [
      {
       "kind": "assign",
       "target": "items",
       "expression": "load_items(STORE)",
       "operator": "="
      },
      {
       "kind": "try",
       "exception": "(IndexError, ValueError)",
       "alias": "error",
       "body": [
        {
         "kind": "branch",
         "condition": "not args or args[0] == 'list'",
         "body": [
          {
           "kind": "call",
           "expression": "print(format_items(items))"
          }
         ],
         "otherwise": [
          {
           "kind": "branch",
           "condition": "args[0] == 'add'",
           "body": [
            {
             "kind": "call",
             "expression": "save_items(STORE, add_item(items, ' '.join(args[1:])))"
            },
            {
             "kind": "call",
             "expression": "print('Added.')"
            }
           ],
           "otherwise": [
            {
             "kind": "branch",
             "condition": "args[0] == 'done'",
             "body": [
              {
               "kind": "call",
               "expression": "save_items(STORE, complete_item(items, int(args[1])))"
              },
              {
               "kind": "call",
               "expression": "print('Marked done.')"
              }
             ],
             "otherwise": [
              {
               "kind": "call",
               "expression": "print('usage: todo.py [list | add TEXT | done NUMBER]')"
              },
              {
               "kind": "return",
               "expression": "2"
              }
             ]
            }
           ]
          }
         ]
        }
       ],
       "handler": [
        {
         "kind": "call",
         "expression": "print(f'error: {error}')"
        },
        {
         "kind": "return",
         "expression": "1"
        }
       ],
       "finally": []
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
   ]
  }
 ],
 "requirements": []
}
```