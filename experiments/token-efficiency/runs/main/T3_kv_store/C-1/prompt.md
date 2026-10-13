You are the coding agent for one run of a controlled benchmark.

Workspace: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r16
- Work ONLY inside the workspace. Do not read, list or search anything outside it; other runs and
  evaluation files exist on this machine and looking at them invalidates the run.
- Deliverable: the program file /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r16/app/store.py. Put nothing else you write in app/ except files a
  tool you were told to use creates there.
- You may write and run your own checks in /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r16/scratch/.
- Python: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/python . Do not install packages. No network access.
- Budget: at most 30 tool calls. There is one attempt. Hidden acceptance tests will run
  `python app/store.py ...` from a fresh temporary directory after you finish.
- End with a short report: files written, whether your own checks passed, how many times you ran them.

## Specification

# Task: persistent key-value store

Write a command-line program `store.py` (Python 3.11+, standard library only). It keeps its data in
the file `store.json` in the current working directory, so values persist between runs.

## Usage

    python store.py [set KEY VALUE | get KEY | delete KEY | list]

## Behavior

1. `list` (any further arguments are ignored), or no arguments: print every entry as `KEY = VALUE`, one per line, sorted by key. With no
   entries print `(empty)`.
2. `set KEY VALUE` (exactly two arguments after `set`): store VALUE under KEY (replacing any old
   value), save, and print `KEY saved.`
3. `get KEY` (exactly one argument): print the stored value. If KEY does not exist, print
   `error: no key KEY` and exit with code 1.
4. `delete KEY` (exactly one argument): remove KEY, save, and print `KEY deleted.` If KEY does not
   exist, print `error: no key KEY` and exit with code 1.
5. Anything else, including a known command with the wrong number of arguments: print
   `usage: store.py [set KEY VALUE | get KEY | delete KEY | list]` and exit with code 2.
6. If `store.json` is missing or does not contain valid JSON, treat the store as empty.
7. Successful commands exit with code 0. Values are stored and printed as text.

## Example

    $ python store.py set name Ana
    name saved.
    $ python store.py get name
    Ana

## Tool available: Block-Wise

Block-Wise is installed: run it as `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/blockwise <command>` from the workspace directory /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r16. Every command
prints one compact JSON line. Commands:
- `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/blockwise find <words>`: the 3 best-matching presets/blueprints for a few words
- `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/blockwise list [--category validation|auth|data|files|blueprint]`
- `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/blockwise show <id> [--set k=v ...]`: the code a preset or blueprint would write (not written to disk)
- `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/blockwise apply <id> --into <file.py or folder> [--set k=v ...]`: writes it (blueprints take a folder)
- `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/blockwise check`: structure check of everything applied
Exit codes: 0 ok, 1 check found issues, 2 bad input.

Rules for using it (adapted from the project's docs/agent-instructions.md):
1. Before writing a small, common Python function or a small command-line tool, search with `find`.
2. If a result fits, `apply` it with the right names. Don't re-type code a preset provides. Do not
   print or read generated code unless your own checks fail and you need it to fix a problem.
3. If the result lists a `todo`, fill only that part. After editing files Block-Wise wrote, run `check`.
4. Block-Wise checks structure, not behavior: still run your own behavioral checks.
If nothing fits, write the code normally. Don't force a preset that doesn't match the task.