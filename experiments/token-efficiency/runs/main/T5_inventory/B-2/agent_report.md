I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r40/app/inventory.py`, following the plan's module, constants, functions and body structure. Nothing else is in `app/`.

My checks passed. I ran them once, as a single batch of 13 commands in `scratch/`, using a throwaway `inventory.json` there. They covered:
- `show` on an empty inventory, plus `add` and `low`.
- `remove` down to zero, which deleted the item.
- An unknown item and an over-stock `remove`.
- An invalid item name, a zero quantity and a non-numeric threshold.
- An unknown command and a wrong argument count.

Every message and exit code (0, 1 or 2) matched the spec. I did not test a corrupt `inventory.json` file.

I used 3 tool calls.
