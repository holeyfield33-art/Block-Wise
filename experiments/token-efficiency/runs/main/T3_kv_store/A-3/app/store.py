import json
import sys

USAGE = "usage: store.py [set KEY VALUE | get KEY | delete KEY | list]"
PATH = "store.json"


def load():
    try:
        with open(PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def save(data):
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)


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
    if cmd in ("get", "delete") and len(args) == 1:
        data = load()
        key = args[0]
        if key not in data:
            print(f"error: no key {key}")
            return 1
        if cmd == "get":
            print(data[key])
        else:
            del data[key]
            save(data)
            print(f"{key} deleted.")
        return 0
    print(USAGE)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
