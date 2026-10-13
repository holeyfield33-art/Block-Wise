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
            if isinstance(k, str) and isinstance(v, int) and not isinstance(v, bool)}


def save(inv):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(inv, f, indent=2, sort_keys=True)


def is_digits(s):
    return re.fullmatch(r"[0-9]+", s) is not None


def fail(msg, code=1):
    print(msg)
    sys.exit(code)


def validate(item, qty):
    if re.fullmatch(r"[a-z0-9-]{1,30}", item) is None:
        fail("error: invalid item name")
    if not is_digits(qty) or int(qty) <= 0:
        fail("error: quantity must be a positive whole number")
    return int(qty)


def main(argv):
    if not argv or (argv[0] == "show" and len(argv) == 1):
        inv = load()
        if not inv:
            print("No items.")
        for k in sorted(inv):
            print(f"{k}: {inv[k]}")
        return 0
    cmd = argv[0]
    if cmd in ("add", "remove") and len(argv) == 3:
        item = argv[1]
        qty = validate(item, argv[2])
        inv = load()
        if cmd == "add":
            inv[item] = inv.get(item, 0) + qty
            save(inv)
            print(f"Added {qty} x {item} (now {inv[item]}).")
            return 0
        if item not in inv:
            fail(f"error: unknown item {item}")
        if qty > inv[item]:
            fail(f"error: only {inv[item]} of {item} in stock")
        inv[item] -= qty
        total = inv[item]
        if total == 0:
            del inv[item]
        save(inv)
        print(f"Removed {qty} x {item} (now {total}).")
        return 0
    if cmd == "low" and len(argv) in (1, 2):
        th = 5
        if len(argv) == 2:
            if not is_digits(argv[1]):
                fail("error: threshold must be a whole number")
            th = int(argv[1])
        inv = load()
        low = [k for k in sorted(inv) if inv[k] < th]
        if not low:
            print("Nothing is low.")
        for k in low:
            print(f"{k}: {inv[k]}")
        return 0
    print(USAGE)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
