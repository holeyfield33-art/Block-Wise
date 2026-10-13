import json
import os
import sys

USAGE = "usage: store.py [set KEY VALUE | get KEY | delete KEY | list]"
FILE = "store.json"


def load():
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(k): (v if isinstance(v, str) else str(v)) for k, v in data.items()}


def save(data):
    tmp = FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.replace(tmp, FILE)


def main(argv):
    if not argv or argv[0] == "list":
        data = load()
        if not data:
            print("(empty)")
        else:
            for k in sorted(data):
                print(f"{k} = {data[k]}")
        return 0
    cmd, args = argv[0], argv[1:]
    if cmd == "set" and len(args) == 2:
        data = load()
        data[args[0]] = args[1]
        save(data)
        print(f"{args[0]} saved.")
        return 0
    if cmd == "get" and len(args) == 1:
        data = load()
        if args[0] not in data:
            print(f"error: no key {args[0]}")
            return 1
        print(data[args[0]])
        return 0
    if cmd == "delete" and len(args) == 1:
        data = load()
        if args[0] not in data:
            print(f"error: no key {args[0]}")
            return 1
        del data[args[0]]
        save(data)
        print(f"{args[0]} deleted.")
        return 0
    print(USAGE)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
