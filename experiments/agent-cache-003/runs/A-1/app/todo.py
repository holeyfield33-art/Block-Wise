import json
import sys

USAGE = "usage: todo.py [list | add TEXT | done NUMBER]"
FILE = "todo.json"


def load():
    try:
        with open(FILE, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return []
    if not isinstance(data, list):
        return []
    items = []
    for it in data:
        if isinstance(it, dict):
            items.append({"text": str(it.get("text", "")), "done": bool(it.get("done", False))})
    return items


def save(items):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def main(argv):
    if not argv or argv[0] == "list":
        items = load()
        if not items:
            print("Nothing to do.")
        for n, it in enumerate(items, 1):
            print("%d. [%s] %s" % (n, "x" if it["done"] else " ", it["text"]))
        return 0
    cmd = argv[0]
    if cmd == "add":
        text = " ".join(argv[1:]).strip()
        if not text:
            print("error: text must not be empty")
            return 1
        items = load()
        items.append({"text": text, "done": False})
        save(items)
        print("Added.")
        return 0
    if cmd == "done" and len(argv) == 2:
        items = load()
        try:
            n = int(argv[1])
        except ValueError:
            n = 0
        if n < 1 or n > len(items):
            print("error: no item " + argv[1])
            return 1
        items[n - 1]["done"] = True
        save(items)
        print("Marked done.")
        return 0
    print(USAGE)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
