I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r29/app/inventory.py`, and my own check passed. I ran it once, as a single batch of 12 command invocations in `scratch/`, which covered:
- `show` with no items
- `add`
- `low`
- `remove` with too much stock
- `remove` of an unknown item
- `remove` down to 0
- an invalid item name
- quantity 0
- a bad threshold
- an unknown command

Every output and exit code matched the spec. The script is also never run with a malformed `inventory.json`, so spec rule 7 (missing or invalid JSON treated as empty) was only exercised for the missing-file case. Total tool calls used: 3.
