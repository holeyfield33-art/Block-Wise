I wrote `app/store.py` from the Block-Wise `kv_store` blueprint (found with `find`, applied with `apply kv_store --into app`). The full path is /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r45/app/store.py. It is the only file I put in `app/`.

My behavioral checks passed. I ran them twice: a full command run, then a rerun of the one failing case after the fix.

- **Covered:** every command, wrong argument counts (exit 2), missing keys (exit 1), a missing or invalid `store.json`, and a non-ASCII value.
- **One bug found and fixed:** a `store.json` holding valid JSON that isn't an object (for example `[1,2]`) made `list` crash with "list index out of range". I edited `load()` to treat anything that isn't a dict as an empty store.
- **After the fix:** `[1,2]` gives `(empty)`, and `{"n":5}` still prints `5`.

I did not fully rerun the first check batch after the fix, only the two cases above. `blockwise check` passed after the blueprint was applied. After my edit it only said "No plan yet", so the edited file is not structure-checked.
