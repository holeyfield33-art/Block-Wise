import json
import re
import sys

USAGE = "usage: inventory.py [add ITEM QTY | remove ITEM QTY | show | low [THRESHOLD]]"
FILE = "inventory.json"


def load():
    try:
        with open(FILE, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {k: v for k, v in data.items()
            if isinstance(v, int) and not isinstance(v, bool) and v > 0}


def save(items):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, sort_keys=True)


def is_whole(s):
    return s.isascii() and s.isdigit()


def fail(msg, code=1):
    print(msg)
    sys.exit(code)


def main(argv):
    if not argv or argv == ["show"]:
        items = load()
        if not items:
            print("No items.")
        for k in sorted(items):
            print(f"{k}: {items[k]}")
        return 0
    cmd = argv[0]
    if cmd == "low" and len(argv) <= 2:
        t = 5
        if len(argv) == 2:
            if not is_whole(argv[1]):
                fail("error: threshold must be a whole number")
            t = int(argv[1])
        items = load()
        low = [k for k in sorted(items) if items[k] < t]
        if not low:
            print("Nothing is low.")
        for k in low:
            print(f"{k}: {items[k]}")
        return 0
    if cmd in ("add", "remove") and len(argv) == 3:
        item, qty = argv[1], argv[2]
        if not re.fullmatch(r"[a-z0-9-]{1,30}", item):
            fail("error: invalid item name")
        if not is_whole(qty) or int(qty) < 1:
            fail("error: quantity must be a positive whole number")
        qty = int(qty)
        items = load()
        if cmd == "add":
            items[item] = items.get(item, 0) + qty
            save(items)
            print(f"Added {qty} x {item} (now {items[item]}).")
            return 0
        if item not in items:
            fail(f"error: unknown item {item}")
        if qty > items[item]:
            fail(f"error: only {items[item]} of {item} in stock")
        items[item] -= qty
        total = items[item]
        if total == 0:
            del items[item]
        save(items)
        print(f"Removed {qty} x {item} (now {total}).")
        return 0
    fail(USAGE, 2)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
