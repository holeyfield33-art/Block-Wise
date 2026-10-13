You are the coding agent for one run of a controlled benchmark.

Workspace: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/ws002/t02
- Work ONLY inside the workspace. Do not read, list or search anything outside it; other runs and
  evaluation files exist on this machine and looking at them invalidates the run.
- Deliverable: the program file /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/ws002/t02/app/todo.py. Put nothing else in app/.
- Python: /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/python . Do not install packages. No network access.
- Budget: at most 5 tool calls. There is one attempt. Hidden acceptance tests will run
  `python app/todo.py ...` from a fresh temporary directory after you finish; you will not see them.
- End with a short completion record: files written and the generation response.

## Specification

# Task: to-do list command-line app

Write a command-line program `todo.py` (Python 3.11+, standard library only). It keeps its items in
the file `todo.json` in the current working directory, so items persist between runs.

## Usage

    python todo.py [list | add TEXT | done NUMBER]

## Behavior

1. `list`, or no arguments at all: print the items, numbered from 1 in the order they were added, one
   per line as `N. [x] TEXT` for a done item or `N. [ ] TEXT` for an open item. With no items print
   `Nothing to do.`
2. `add TEXT...`: all remaining arguments are joined with single spaces and stripped of surrounding
   whitespace to form the text. If the text is empty, print `error: text must not be empty` and exit
   with code 1 (nothing is saved). Otherwise append it as an open item, save, and print `Added.`
3. `done NUMBER`: mark item NUMBER (1-based) as done, save, and print `Marked done.` If there is no
   such item, print `error: no item NUMBER` and exit with code 1.
4. Any other command: print `usage: todo.py [list | add TEXT | done NUMBER]` and exit with code 2.
5. If `todo.json` is missing or does not contain valid JSON, treat the list as empty.
6. Successful commands exit with code 0.

## Example

    $ python todo.py add buy milk
    Added.
    $ python todo.py list
    1. [ ] buy milk

## Approved component: Block-Wise blueprint `todo_cli`

This specification is implemented by the approved, previously tested Block-Wise blueprint `todo_cli`
(blueprint file sha256 e2b1eb18ef25a78b3101c0531cdd89dac68f2443811a859e8c7b9592a8b518ea). Delegate the implementation to it:

    cd /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/ws002/t02 && /tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/blockwise apply todo_cli --into app

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