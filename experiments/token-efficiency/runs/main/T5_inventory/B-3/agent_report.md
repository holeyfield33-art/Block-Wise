I wrote /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r39/app/inventory.py, following the plan's imports, constant, function signatures and body structure. It is the only file in app/.

My own check passed. I ran one script, once, from scratch/, covering these cases:
- **add:** adding a new item prints the "Added" line.
- **low:** `low` lists items under the default threshold of 5.
- **remove:** removing down to 0 deletes the item, so it then shows as unknown.
- **errors, exit code 1:** an unknown item, a quantity above stock, an invalid item name, a zero quantity, and a non-numeric threshold.
- **usage, exit code 2:** an unrecognised command prints the usage line.
- **show:** `show` lists the remaining items.

All outputs and exit codes matched the spec. I did not test a missing or invalid `inventory.json` separately.

I used 3 tool calls in total (Read, one Bash to write the file and run the check, and this handback).
