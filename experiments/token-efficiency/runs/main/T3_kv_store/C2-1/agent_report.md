Report: wrote /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r21/app/store.py (applied via `blockwise apply kv_store --into app`). Scratch data only in scratch/t/.

My behavioral checks passed after one hand fix. They covered set, get, delete, list, no arguments, missing keys (exit 1), wrong argument counts and unknown commands (usage, exit 2), a corrupt store.json, and `list extra`. They found one bug in the generated code: valid JSON that isn't an object (e.g. `[1,2]`) made `list` error and `set` crash. I edited `load()` so a non-dict is treated as an empty store, then re-checked that case and it works.

`blockwise check` was clean before my edit. It now reports `body_changed` on `load`, which is expected because I edited a function Block-Wise wrote. I left it.

I ran the behavioral checks in two rounds (the second only covered the fix), and `blockwise check` twice.
