import json
import sys

FILE = "todo.json"
USAGE = "usage: todo.py [list | add TEXT | done NUMBER]"


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
        if isinstance(it, dict) and isinstance(it.get("text"), str):
            items.append({"text": it["text"], "done": bool(it.get("done"))})
    return items


def save(items):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(items, f)


def main(argv):
    cmd = argv[0] if argv else "list"
    if cmd == "list" and len(argv) <= 1:
        items = load()
        if not items:
            print("Nothing to do.")
        for i, it in enumerate(items, 1):
            print(f"{i}. [{'x' if it['done'] else ' '}] {it['text']}")
        return 0
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
        arg = argv[1]
        items = load()
        n = None
        try:
            n = int(arg.strip())
        except ValueError:
            pass
        if n is None or n < 1 or n > len(items):
            print(f"error: no item {arg}")
            return 1
        items[n - 1]["done"] = True
        save(items)
        print("Marked done.")
        return 0
    print(USAGE)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
