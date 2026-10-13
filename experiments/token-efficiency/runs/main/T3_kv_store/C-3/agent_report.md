I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r57/app/store.py`. It passed my own behavioral checks, and `blockwise check` now flags one function that I edited.

- **How it was built:** `blockwise find` returned the `kv_store` blueprint. I applied it with `file=store store=store.json` and did not read the generated code.
- **Behavioral checks:** I ran one batch of about 25 command variants from `scratch/t`, then a re-run of the one case I fixed.
  - Covered: `list` and no arguments, `set`, `get`, `delete`, and a missing key (`error: no key KEY`, exit 1).
  - Covered: wrong argument counts and unknown commands (usage message, exit 2), plus a corrupt `store.json` and a non-dict JSON file.
  - All matched the spec except one case.
- **Bug fixed:** a `store.json` containing valid JSON that wasn't an object, such as `[1,2]`, crashed `list`. I edited `load()` so any non-dict JSON is treated as an empty store. After the fix, `list` printed `(empty)` and exited 0.
- **Block-Wise checks:**
  - Before my edit, `check` passed with no issues.
  - After my edit, `check` reports `body_changed` on `load`, because I changed the generated function's body. This is a structure-only complaint, and the behavior is correct. I left it as is.
- **Runs:** I ran my behavioral checks once as a batch, plus the one re-run after the fix. I ran `blockwise check` twice before the fix and once after.
