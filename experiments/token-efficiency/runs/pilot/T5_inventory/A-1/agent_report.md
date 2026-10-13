I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/ws/p07/app/inventory.py` and my own checks passed. I ran them once, as a single batch of 14 commands.

The checks covered show on an empty inventory, add, and remove down to 0 (which deletes the item). They also covered an invalid item name, quantity 0 and quantity `3.0`, removing more than the stock, removing an unknown item, `low` with the default threshold, `low 2`, `low -1`, an unknown command, and a wrong argument count. Output and exit codes (0, 1, 2) matched the spec each time. I did not test a corrupt `inventory.json` or a non-dict JSON file separately; the code treats both as an empty inventory.

The only other thing I created is `inventory.json`, left in `scratch/` by those test runs. Nothing else is in `app/`.
