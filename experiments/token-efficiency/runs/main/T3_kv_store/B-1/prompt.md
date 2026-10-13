You are the coding agent for one run of a controlled benchmark.

Workspace: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r10
- Work ONLY inside the workspace. Do not read, list or search anything outside it; other runs and
  evaluation files exist on this machine and looking at them invalidates the run.
- Deliverable: the program file /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r10/app/store.py. Put nothing else you write in app/ except files a
  tool you were told to use creates there.
- You may write and run your own checks in /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r10/scratch/.
- Python: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/plainvenv/bin/python . Do not install packages. No network access.
- Budget: at most 30 tool calls. There is one attempt. Hidden acceptance tests will run
  `python app/store.py ...` from a fresh temporary directory after you finish.
- End with a short report: files written, whether your own checks passed, how many times you ran them.

## Specification

# Task: persistent key-value store

Write a command-line program `store.py` (Python 3.11+, standard library only). It keeps its data in
the file `store.json` in the current working directory, so values persist between runs.

## Usage

    python store.py [set KEY VALUE | get KEY | delete KEY | list]

## Behavior

1. `list` (any further arguments are ignored), or no arguments: print every entry as `KEY = VALUE`, one per line, sorted by key. With no
   entries print `(empty)`.
2. `set KEY VALUE` (exactly two arguments after `set`): store VALUE under KEY (replacing any old
   value), save, and print `KEY saved.`
3. `get KEY` (exactly one argument): print the stored value. If KEY does not exist, print
   `error: no key KEY` and exit with code 1.
4. `delete KEY` (exactly one argument): remove KEY, save, and print `KEY deleted.` If KEY does not
   exist, print `error: no key KEY` and exit with code 1.
5. Anything else, including a known command with the wrong number of arguments: print
   `usage: store.py [set KEY VALUE | get KEY | delete KEY | list]` and exit with code 2.
6. If `store.json` is missing or does not contain valid JSON, treat the store as empty.
7. Successful commands exit with code 0. Values are stored and printed as text.

## Example

    $ python store.py set name Ana
    name saved.
    $ python store.py get name
    Ana

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
 "title": "Key-value store in a JSON file",
 "modules": [
  {
   "path": "store.py",
   "imports": [
    "import json",
    "import sys"
   ],
   "constants": [
    {
     "name": "STORE",
     "value": "'store.json'"
    }
   ],
   "functions": [
    {
     "name": "load",
     "parameters": [
      {
       "name": "path",
       "type": "str"
      }
     ],
     "returns": "dict",
     "requirements": [
      "A missing or broken file means an empty store."
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
         "expression": "{}"
        }
       ],
       "alias": "",
       "finally": []
      }
     ]
    },
    {
     "name": "save",
     "parameters": [
      {
       "name": "path",
       "type": "str"
      },
      {
       "name": "data",
       "type": "dict"
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
         "expression": "json.dump(data, handle, indent=2, sort_keys=True)"
        }
       ]
      }
     ],
     "requirements": []
    },
    {
     "name": "format_entries",
     "parameters": [
      {
       "name": "data",
       "type": "dict"
      }
     ],
     "returns": "str",
     "body": [
      {
       "kind": "branch",
       "condition": "not data",
       "body": [
        {
         "kind": "return",
         "expression": "'(empty)'"
        }
       ],
       "otherwise": []
      },
      {
       "kind": "return",
       "expression": "'\\n'.join((f'{key} = {data[key]}' for key in sorted(data)))"
      }
     ],
     "requirements": []
    },
    {
     "name": "require_key",
     "parameters": [
      {
       "name": "data",
       "type": "dict"
      },
      {
       "name": "key",
       "type": "str"
      }
     ],
     "returns": "None",
     "body": [
      {
       "kind": "branch",
       "condition": "key not in data",
       "body": [
        {
         "kind": "raise",
         "expression": "LookupError(f'no key {key}')"
        }
       ],
       "otherwise": []
      }
     ],
     "requirements": []
    },
    {
     "name": "set_value",
     "parameters": [
      {
       "name": "data",
       "type": "dict"
      },
      {
       "name": "key",
       "type": "str"
      },
      {
       "name": "value",
       "type": "str"
      }
     ],
     "returns": "int",
     "body": [
      {
       "kind": "call",
       "expression": "data.update({key: value})"
      },
      {
       "kind": "call",
       "expression": "save(STORE, data)"
      },
      {
       "kind": "call",
       "expression": "print(f'{key} saved.')"
      },
      {
       "kind": "return",
       "expression": "0"
      }
     ],
     "requirements": []
    },
    {
     "name": "get_value",
     "parameters": [
      {
       "name": "data",
       "type": "dict"
      },
      {
       "name": "key",
       "type": "str"
      }
     ],
     "returns": "int",
     "body": [
      {
       "kind": "validate",
       "expression": "require_key(data, key)"
      },
      {
       "kind": "call",
       "expression": "print(data[key])"
      },
      {
       "kind": "return",
       "expression": "0"
      }
     ],
     "requirements": []
    },
    {
     "name": "delete_value",
     "parameters": [
      {
       "name": "data",
       "type": "dict"
      },
      {
       "name": "key",
       "type": "str"
      }
     ],
     "returns": "int",
     "body": [
      {
       "kind": "validate",
       "expression": "require_key(data, key)"
      },
      {
       "kind": "call",
       "expression": "data.pop(key)"
      },
      {
       "kind": "call",
       "expression": "save(STORE, data)"
      },
      {
       "kind": "call",
       "expression": "print(f'{key} deleted.')"
      },
      {
       "kind": "return",
       "expression": "0"
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
      "Commands: set KEY VALUE, get KEY, delete KEY, list. Returns the exit code."
     ],
     "body": [
      {
       "kind": "assign",
       "target": "data",
       "expression": "load(STORE)",
       "operator": "="
      },
      {
       "kind": "try",
       "exception": "LookupError",
       "alias": "error",
       "body": [
        {
         "kind": "branch",
         "condition": "not args or args[0] == 'list'",
         "body": [
          {
           "kind": "call",
           "expression": "print(format_entries(data))"
          }
         ],
         "otherwise": [
          {
           "kind": "branch",
           "condition": "args[0] == 'set' and len(args) == 3",
           "body": [
            {
             "kind": "return",
             "expression": "set_value(data, args[1], args[2])"
            }
           ],
           "otherwise": [
            {
             "kind": "branch",
             "condition": "args[0] == 'get' and len(args) == 2",
             "body": [
              {
               "kind": "return",
               "expression": "get_value(data, args[1])"
              }
             ],
             "otherwise": [
              {
               "kind": "branch",
               "condition": "args[0] == 'delete' and len(args) == 2",
               "body": [
                {
                 "kind": "return",
                 "expression": "delete_value(data, args[1])"
                }
               ],
               "otherwise": [
                {
                 "kind": "call",
                 "expression": "print('usage: store.py [set KEY VALUE | get KEY | delete KEY | list]')"
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