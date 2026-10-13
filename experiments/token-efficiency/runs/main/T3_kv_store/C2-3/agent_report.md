I wrote `app/store.py` by applying the Block-Wise `kv_store` blueprint, and my own behavior checks pass. The only tool-written file in `app/` is `store.py`, at /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r44/app/store.py.

**Block-Wise:** I ran `find`, then `apply kv_store --into app`, then `check`, which reported no issues. A later `check` run from the `scratch/t` directory reported "No plan yet", so it didn't re-check the final file.

**One fix after the first check run:** if `store.json` held valid JSON that wasn't an object, such as `[1,2]`, `list` crashed with "list index out of range". I changed `load` to treat any non-dict as an empty store. After that, `list` printed `(empty)` and a following `set` worked.

**My checks:** I ran two scripted batches, one before the fix and a short one after it. They covered these cases:
- no arguments and `list` with extra arguments
- `set`, `get` and `delete`, including a missing key (exit code 1)
- overwriting an existing key
- sorted `list` output
- wrong argument counts and unknown commands (usage message, exit code 2)
- a missing, broken or non-object `store.json`

**One unspecified case:** an empty-string key is accepted.
