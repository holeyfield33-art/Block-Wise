I wrote app/inventory.py and my own checks passed. I ran them once, as a single batch of 14 CLI invocations in the scratch directory.

- **File written:** `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r24/app/inventory.py`. It follows the plan's imports, `STORE` constant, function signatures and body structure. The nested if/else in `main` is written as `elif`, which is equivalent.
- **What the checks covered:**
  - `show` on an empty inventory.
  - `add` of a new item and of an existing one.
  - `low` printing `Nothing is low.`
  - `remove` with too much stock (exit 1), of an unknown item (exit 1), and down to zero, which deletes the item.
  - An invalid item name, quantities `0` and `3.0`, a threshold of `-1`, an unknown command, and a wrong argument count (exit 2).
- **Not run:** `low` listing items below the threshold, and a corrupt `inventory.json`.
- **Tool calls:** I used 2 of the 30 allowed.
