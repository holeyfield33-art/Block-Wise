You are the coding agent for one run of a controlled benchmark.

Workspace: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/ws002/t01
- Work ONLY inside the workspace. Do not read, list or search anything outside it; other runs and
  evaluation files exist on this machine and looking at them invalidates the run.
- Deliverable: the program file /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/ws002/t01/app/store.py. Put nothing else in app/.
- Python: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/python . Do not install packages. No network access.
- Budget: at most 5 tool calls. There is one attempt. Hidden acceptance tests will run
  `python app/store.py ...` from a fresh temporary directory after you finish; you will not see them.
- End with a short completion record: files written and the generation response.

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

## Approved component: Block-Wise blueprint `kv_store`

This specification is implemented by the approved, previously tested Block-Wise blueprint `kv_store`
(blueprint file sha256 a369afe1360b440a73eb617a55ff27bb03125245c272cba46d12710c2c364899). Delegate the implementation to it:

    cd /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/ws002/t01 && /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/blockwise apply kv_store --into app

Trust rules for this run:
1. The blueprint is an approved component that already passes its acceptance tests.
2. Run the command above once. A response with `"ok":true` means the task is complete.
3. Do not open, read, print or inspect any generated file.
4. Do not rewrite, improve or extend the generated code.
5. Do not run `/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/blockwise check`.
6. Do not run the program, tests or any debugging.
7. Do not run `apply` again after a successful response.
8. Do not write documentation or any other file.
9. If the response is not `"ok":true`, stop and report the response; do not try to fix it.
10. Finish with the file path(s) from the response and the response line itself.