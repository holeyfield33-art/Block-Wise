I wrote /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r23/app/inventory.py, and my own check passed. I ran it once, as a single batch of 14 commands in scratch/. The commands covered:
- show with no items
- add, remove and low
- invalid item name, quantity 0 and 3.0
- unknown item and insufficient stock
- a bad threshold
- removing down to 0, which deleted the item
- an unknown command and the wrong number of arguments

Every output and exit code matched the spec. I did not test a corrupt or missing `inventory.json` by hand. The code treats a missing file, invalid JSON, or JSON that isn't an object as an empty inventory.

Only that one file is in app/.
