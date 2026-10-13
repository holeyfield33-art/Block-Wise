I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/ws/p04/app/inventory.py`, following the plan's imports, constant, functions, signatures and body structure.

My checks passed, and I ran them once. That was a single batch of 15 commands run from `scratch/t`, covering:
- show on an empty inventory
- add (two adds on the same item)
- low (default threshold, explicit threshold, and a bad threshold)
- remove (too much, unknown item, and down to zero, which deletes the item)
- an invalid item name
- a quantity of `0` and of `3.0`
- an unknown command
- a wrong argument count

Each printed the expected message and exit code. I did not test a corrupt `inventory.json`.
