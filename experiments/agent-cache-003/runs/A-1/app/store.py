import json
import sys

USAGE = "usage: store.py [set KEY VALUE | get KEY | delete KEY | list]"
FILE = "store.json"


def load():
    try:
        with open(FILE, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(k): v if isinstance(v, str) else json.dumps(v) if not isinstance(v, (int, float)) else str(v)
            for k, v in data.items()}


def save(d):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def main(argv):
    if not argv or argv[0] == "list":
        d = load()
        if not d:
            print("(empty)")
        for k in sorted(d):
            print("%s = %s" % (k, d[k]))
        return 0
    cmd, args = argv[0], argv[1:]
    if cmd == "set" and len(args) == 2:
        d = load()
        d[args[0]] = args[1]
        save(d)
        print(args[0] + " saved.")
        return 0
    if cmd in ("get", "delete") and len(args) == 1:
        d = load()
        k = args[0]
        if k not in d:
            print("error: no key " + k)
            return 1
        if cmd == "get":
            print(d[k])
        else:
            del d[k]
            save(d)
            print(k + " deleted.")
        return 0
    print(USAGE)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
