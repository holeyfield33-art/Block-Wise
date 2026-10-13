I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r04/app/inventory.py`, and my own checks passed. I ran the check script once, in a temp directory, and every output and exit code matched the spec.

- **Block-Wise:** I ran `find` once. Its three suggestions (`todo_cli`, `data_validator`, `kv_store`) did not match an inventory tracker, so I wrote the code by hand. I did not run `apply` or `check`.
- **What the checks covered:**
  - `show` and `low`, including a threshold of 0 and non-numeric or negative thresholds.
  - `add` and `remove`, including deleting an item when its stock reaches 0.
  - Unknown item and over-stock errors.
  - Bad item names and bad quantities (`0`, `3.0`).
  - Usage errors with exit code 2, including wrong argument counts.
  - Invalid JSON in `inventory.json`, treated as empty.
- **Files:** `inventory.py` is the only file in `app/`. The check script is `scratch/t.sh`.
- **Tool calls:** I used 3 of the 30.
