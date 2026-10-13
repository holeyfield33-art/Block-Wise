I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r48/app/inventory.py`, and my own checks passed. I ran them once, as a single batch of 17 commands, and every output and exit code matched the spec.

- **Block-Wise:** I ran `find` once. It returned only `todo_cli`, `data_validator` and `kv_store`, and none fit this task, so I wrote the code by hand and did not run `apply` or `check`.
- **What the checks covered:** `show`, `add`, `remove` and `low`; invalid item names; bad quantities (`0` and `3.0`); a non-numeric threshold; unknown items; removing more than the stock; and wrong or unknown commands (exit code 2).
- **Not tested:** an invalid or non-dict `inventory.json`. The code treats both as an empty inventory, as the spec says.

I used 3 tool calls in total. The only other file is a scratch `inventory.json` that the checks created in `scratch/`.
