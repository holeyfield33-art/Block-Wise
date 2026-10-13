I wrote `app/store.py` in the r16 workspace. It came from the Block-Wise `kv_store` blueprint, applied with `file=store`, and my own behavior checks passed.

- **Block-Wise:** `find` returned `kv_store`, and I applied it. The one change I made was in `load`. The generated code crashed on a store.json holding valid JSON that isn't an object, such as `[1]`. `load` now treats that as an empty store.
- **Checks:** I ran one batch of behavior checks, then one re-check after the fix. It covered these cases:
  - no arguments and `list`, including extra arguments
  - `set`, `get` and `delete`, including a missing key (exit 1)
  - wrong argument counts and an unknown command (exit 2)
  - a corrupt store.json and a non-object store.json
  - an empty value
- **`blockwise check`:** it ran once and reported no issues, but its note says "No plan yet", so it checked 0 functions.

Deliverable: `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r16/app/store.py`
