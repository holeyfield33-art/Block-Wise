You are the coding agent for one run of a controlled benchmark.

Workspace: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r24
- Work ONLY inside the workspace. Do not read, list or search anything outside it; other runs and
  evaluation files exist on this machine and looking at them invalidates the run.
- Deliverable: the program file /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r24/app/inventory.py. Put nothing else you write in app/ except files a
  tool you were told to use creates there.
- You may write and run your own checks in /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r24/scratch/.
- Python: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/plainvenv/bin/python . Do not install packages. No network access.
- Budget: at most 30 tool calls. There is one attempt. Hidden acceptance tests will run
  `python app/inventory.py ...` from a fresh temporary directory after you finish.
- End with a short report: files written, whether your own checks passed, how many times you ran them.

## Specification

# Task: inventory tracker

Write a command-line program `inventory.py` (Python 3.11+, standard library only). It keeps stock
levels in the file `inventory.json` in the current working directory, so they persist between runs.

## Usage

    python inventory.py [add ITEM QTY | remove ITEM QTY | show | low [THRESHOLD]]

## Behavior

1. `show`, or no arguments: print every item as `ITEM: QTY`, one per line, sorted by item name. With no
   items print `No items.`
2. `add ITEM QTY`: increase ITEM's stock by QTY (a new item starts at 0), save, and print
   `Added QTY x ITEM (now TOTAL).`
3. `remove ITEM QTY`: decrease ITEM's stock by QTY, save, and print `Removed QTY x ITEM (now TOTAL).`
   When the stock reaches 0 the item is deleted from the inventory.
   - If ITEM is not in the inventory, print `error: unknown item ITEM` and exit with code 1.
   - If QTY is more than the current stock, print `error: only STOCK of ITEM in stock` and exit with
     code 1; nothing changes.
4. `low [THRESHOLD]`: print every item whose stock is below THRESHOLD (default 5) as `ITEM: QTY`,
   sorted by item name. If none, print `Nothing is low.` THRESHOLD must be a whole number of 0 or more,
   otherwise print `error: threshold must be a whole number` and exit with code 1.
5. Validation for `add` and `remove`, checked in this order before anything else happens:
   - ITEM must be 1 to 30 characters long and contain only lowercase letters a-z, digits and `-`;
     otherwise print `error: invalid item name` and exit with code 1.
   - QTY must be a positive whole number written with digits only (`3`, not `3.0`, `-1` or `0`);
     otherwise print `error: quantity must be a positive whole number` and exit with code 1.
6. Any other command, or a wrong number of arguments: print
   `usage: inventory.py [add ITEM QTY | remove ITEM QTY | show | low [THRESHOLD]]` and exit with code 2.
7. If `inventory.json` is missing or does not contain valid JSON, treat the inventory as empty.
8. Successful commands exit with code 0.

## Example

    $ python inventory.py add apple 3
    Added 3 x apple (now 3).
    $ python inventory.py low
    apple: 3

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
 "title": "Inventory tracker",
 "modules": [
  {
   "path": "inventory.py",
   "imports": [
    "import json",
    "import re",
    "import sys"
   ],
   "constants": [
    {
     "name": "STORE",
     "value": "'inventory.json'"
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
       ]
      }
     ],
     "requirements": [
      "A missing or broken file means an empty inventory."
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
     ]
    },
    {
     "name": "check_item",
     "parameters": [
      {
       "name": "item",
       "type": "str"
      }
     ],
     "returns": "None",
     "body": [
      {
       "kind": "branch",
       "condition": "not re.fullmatch('[a-z0-9-]{1,30}', item)",
       "body": [
        {
         "kind": "raise",
         "expression": "ValueError('invalid item name')"
        }
       ]
      }
     ]
    },
    {
     "name": "parse_qty",
     "parameters": [
      {
       "name": "text",
       "type": "str"
      }
     ],
     "returns": "int",
     "body": [
      {
       "kind": "branch",
       "condition": "not (text.isascii() and text.isdigit()) or int(text) == 0",
       "body": [
        {
         "kind": "raise",
         "expression": "ValueError('quantity must be a positive whole number')"
        }
       ]
      },
      {
       "kind": "return",
       "expression": "int(text)"
      }
     ]
    },
    {
     "name": "parse_threshold",
     "parameters": [
      {
       "name": "text",
       "type": "str"
      }
     ],
     "returns": "int",
     "body": [
      {
       "kind": "branch",
       "condition": "not (text.isascii() and text.isdigit())",
       "body": [
        {
         "kind": "raise",
         "expression": "ValueError('threshold must be a whole number')"
        }
       ]
      },
      {
       "kind": "return",
       "expression": "int(text)"
      }
     ]
    },
    {
     "name": "format_items",
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
         "expression": "'No items.'"
        }
       ]
      },
      {
       "kind": "return",
       "expression": "'\\n'.join((f'{key}: {data[key]}' for key in sorted(data)))"
      }
     ]
    },
    {
     "name": "low_items",
     "parameters": [
      {
       "name": "data",
       "type": "dict"
      },
      {
       "name": "threshold",
       "type": "int"
      }
     ],
     "returns": "str",
     "body": [
      {
       "kind": "assign",
       "target": "names",
       "expression": "[key for key in sorted(data) if data[key] < threshold]"
      },
      {
       "kind": "branch",
       "condition": "not names",
       "body": [
        {
         "kind": "return",
         "expression": "'Nothing is low.'"
        }
       ]
      },
      {
       "kind": "return",
       "expression": "'\\n'.join((f'{key}: {data[key]}' for key in names))"
      }
     ]
    },
    {
     "name": "add_item",
     "parameters": [
      {
       "name": "data",
       "type": "dict"
      },
      {
       "name": "item",
       "type": "str"
      },
      {
       "name": "qty",
       "type": "int"
      }
     ],
     "returns": "int",
     "body": [
      {
       "kind": "call",
       "expression": "data.update({item: data.get(item, 0) + qty})"
      },
      {
       "kind": "call",
       "expression": "save(STORE, data)"
      },
      {
       "kind": "call",
       "expression": "print(f'Added {qty} x {item} (now {data[item]}).')"
      },
      {
       "kind": "return",
       "expression": "0"
      }
     ]
    },
    {
     "name": "remove_item",
     "parameters": [
      {
       "name": "data",
       "type": "dict"
      },
      {
       "name": "item",
       "type": "str"
      },
      {
       "name": "qty",
       "type": "int"
      }
     ],
     "returns": "int",
     "body": [
      {
       "kind": "branch",
       "condition": "item not in data",
       "body": [
        {
         "kind": "raise",
         "expression": "ValueError(f'unknown item {item}')"
        }
       ]
      },
      {
       "kind": "branch",
       "condition": "qty > data[item]",
       "body": [
        {
         "kind": "raise",
         "expression": "ValueError(f'only {data[item]} of {item} in stock')"
        }
       ]
      },
      {
       "kind": "assign",
       "target": "now",
       "expression": "data[item] - qty"
      },
      {
       "kind": "branch",
       "condition": "now == 0",
       "body": [
        {
         "kind": "call",
         "expression": "data.pop(item)"
        }
       ],
       "otherwise": [
        {
         "kind": "call",
         "expression": "data.update({item: now})"
        }
       ]
      },
      {
       "kind": "call",
       "expression": "save(STORE, data)"
      },
      {
       "kind": "call",
       "expression": "print(f'Removed {qty} x {item} (now {now}).')"
      },
      {
       "kind": "return",
       "expression": "0"
      }
     ]
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
       "kind": "assign",
       "target": "data",
       "expression": "load(STORE)"
      },
      {
       "kind": "try",
       "exception": "ValueError",
       "alias": "error",
       "body": [
        {
         "kind": "branch",
         "condition": "not args or args == ['show']",
         "body": [
          {
           "kind": "call",
           "expression": "print(format_items(data))"
          }
         ],
         "otherwise": [
          {
           "kind": "branch",
           "condition": "args[0] in ('add', 'remove') and len(args) == 3",
           "body": [
            {
             "kind": "validate",
             "expression": "check_item(args[1])"
            },
            {
             "kind": "assign",
             "target": "qty",
             "expression": "parse_qty(args[2])"
            },
            {
             "kind": "branch",
             "condition": "args[0] == 'add'",
             "body": [
              {
               "kind": "return",
               "expression": "add_item(data, args[1], qty)"
              }
             ]
            },
            {
             "kind": "return",
             "expression": "remove_item(data, args[1], qty)"
            }
           ],
           "otherwise": [
            {
             "kind": "branch",
             "condition": "args[0] == 'low' and len(args) <= 2",
             "body": [
              {
               "kind": "assign",
               "target": "threshold",
               "expression": "parse_threshold(args[1] if len(args) == 2 else '5')"
              },
              {
               "kind": "call",
               "expression": "print(low_items(data, threshold))"
              }
             ],
             "otherwise": [
              {
               "kind": "call",
               "expression": "print('usage: inventory.py [add ITEM QTY | remove ITEM QTY | show | low [THRESHOLD]]')"
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
       ]
      },
      {
       "kind": "return",
       "expression": "0"
      }
     ],
     "requirements": [
      "Commands: add ITEM QTY, remove ITEM QTY, show, low [THRESHOLD]. Returns the exit code."
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
 ]
}
```