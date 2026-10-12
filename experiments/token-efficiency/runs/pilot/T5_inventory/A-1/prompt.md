You are the coding agent for one run of a controlled benchmark.

Workspace: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/ws/p07
- Work ONLY inside the workspace. Do not read, list or search anything outside it; other runs and
  evaluation files exist on this machine and looking at them invalidates the run.
- Deliverable: the program file /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/ws/p07/app/inventory.py. Put nothing else you write in app/ except files a
  tool you were told to use creates there.
- You may write and run your own checks in /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/ws/p07/scratch/.
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