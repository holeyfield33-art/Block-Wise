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
