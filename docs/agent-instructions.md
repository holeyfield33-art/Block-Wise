## Blockwise building blocks
Before writing a small, common Python function or a small command-line tool, search Blockwise:
1. `find_presets` with a few words (e.g. "validate csv emails", "retry", "group and total").
2. If a result fits, `show_preset` to read what it writes, then `apply_preset` with the right
   names in `params`. Don't re-type code a preset provides.
3. If the result lists a `todo`, fill only that part, using only the calls it allows.
4. After editing files that Blockwise wrote, run `check_project`. Fix the issues it reports, or
   tell me why the change was intended.
5. Blockwise checks structure, not behavior: still run the tests.
If nothing fits, write the code normally. Don't force a preset that doesn't match the task.
