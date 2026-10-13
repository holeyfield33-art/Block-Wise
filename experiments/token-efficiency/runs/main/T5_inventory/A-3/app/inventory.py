import json
import re
import sys

USAGE = "usage: inventory.py [add ITEM QTY | remove ITEM QTY | show | low [THRESHOLD]]"
FILE = "inventory.json"
NAME_RE = re.compile(r"[a-z0-9-]{1,30}")


def load():
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    out = {}
    for k, v in data.items():
        if isinstance(v, int) and not isinstance(v, bool) and v > 0:
            out[k] = v
    return out


def save(inv):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(inv, f, indent=2, sort_keys=True)


def fail(msg, code=1):
    print(msg)
    sys.exit(code)


def whole(s):
    if s.isascii() and s.isdigit():
        try:
            return int(s)
        except ValueError:
            return None
    return None


def main(argv):
    if not argv or argv == ["show"]:
        inv = load()
        if not inv:
            print("No items.")
        for k in sorted(inv):
            print(f"{k}: {inv[k]}")
        return 0
    cmd = argv[0]
    if cmd in ("add", "remove") and len(argv) == 3:
        item, qty_s = argv[1], argv[2]
        if not NAME_RE.fullmatch(item):
            fail("error: invalid item name")
        qty = whole(qty_s)
        if qty is None or qty < 1:
            fail("error: quantity must be a positive whole number")
        inv = load()
        if cmd == "add":
            inv[item] = inv.get(item, 0) + qty
            save(inv)
            print(f"Added {qty} x {item} (now {inv[item]}).")
        else:
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
    if cmd == "low" and len(argv) <= 2:
        th = 5
        if len(argv) == 2:
            th = whole(argv[1])
            if th is None:
                fail("error: threshold must be a whole number")
        inv = load()
        rows = [k for k in sorted(inv) if inv[k] < th]
        if not rows:
            print("Nothing is low.")
        for k in rows:
            print(f"{k}: {inv[k]}")
        return 0
    print(USAGE)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
