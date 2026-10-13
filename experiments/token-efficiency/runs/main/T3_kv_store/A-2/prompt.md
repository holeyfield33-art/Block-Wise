You are the coding agent for one run of a controlled benchmark.

Workspace: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r27
- Work ONLY inside the workspace. Do not read, list or search anything outside it; other runs and
  evaluation files exist on this machine and looking at them invalidates the run.
- Deliverable: the program file /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r27/app/store.py. Put nothing else you write in app/ except files a
  tool you were told to use creates there.
- You may write and run your own checks in /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r27/scratch/.
- Python: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/plainvenv/bin/python . Do not install packages. No network access.
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