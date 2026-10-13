All four programs are written in `.../ws003/s01/app/`, and `app/` holds nothing else. I used 2 tool calls and checked each program with my own runs in `scratch/t`. The hidden tests were not run.

**`app/report.py`**
- Grouping and totals: a messy CSV gave `(blank): 1200.00`, `north: 10.00`, `south: 5.50`, `total: 1215.50`. The blank group's `"1,200"` parsed correctly, and the non-numeric amount and the short row counted as 0.
- Errors: `error: no column nope` exited 1, and `error: cannot read missing.csv` exited 1. Running it with no arguments printed the usage line and exited 2.
- A header-only file with a nonexistent group column printed only `total: 0.00` and exited 0.

**`app/todo.py`**
- With no `todo.json`, no arguments printed `Nothing to do.`
- `add buy   milk` printed `Added.` and stored "buy milk". Whitespace-only text printed `error: text must not be empty` and exited 1.
- After `done 1`, `list` showed `1. [x] buy milk` and `2. [ ] two`. `done 5` printed `error: no item 5` and exited 1. `bogus` printed the usage line and exited 2.

**`app/store.py`**
- With no `store.json`, `list` printed `(empty)`. `set b 2` and `set a x` printed `b saved.` and `a saved.`, and `get a` printed `x`.
- `get z` printed `error: no key z` and exited 1. `list` showed `a = x` then `b = 2`, sorted by key. `delete a` printed `a deleted.`
- `set a` with a missing value printed the usage line and exited 2.

**`app/logstats.py`**
- A sample log with one INFO, one ERROR and one CRITICAL line, two lines of junk, and one blank line in the middle printed `INFO: 1`, `ERROR: 1`, `CRITICAL: 1`, `  2 x db timeout`, and `skipped 3 unreadable line(s)`.
- An empty file printed `No log lines found.` A missing file printed `error: cannot read nope` and exited 1.

I made three choices where the spec was ambiguous:
- **Trailing blank lines:** `logstats.py` ignores them rather than counting them as skipped.
- **`done` argument count:** `todo.py done` with a missing or extra argument prints the usage line and exits 2.
- **Group labels:** `report.py` treats only an exactly empty group value as `(blank)`.
