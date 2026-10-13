I wrote `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r09/app/store.py` by running `blockwise apply kv_store --into app`. My own checks passed.

- **Fix to the generated code:** it crashed when `store.json` held valid JSON that wasn't an object, such as `[1]`. I changed `load()` so a non-dict result is treated as an empty store.
- **Checks run:** I ran one batch of behavioral checks (about 20 commands) in `scratch/t`, then a short re-run after the fix. They covered all the commands, every usage-error case (exit 2), missing keys (exit 1), `list` with extra arguments, a corrupt `store.json`, and the `[1]` case.
- **`blockwise check`:** I ran it twice. The first run, before my edit, reported no issues. The second, after my edit, also reported none, but it said "No plan yet" and checked 0 functions, so it covered nothing that time.
- **Tool calls:** 5 of the 30 allowed, including reading the task file.
