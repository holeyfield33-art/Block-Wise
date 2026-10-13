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
