import csv
import io
import math
import sys

USAGE = "usage: report.py FILE GROUP_COLUMN AMOUNT_COLUMN"


def parse_amount(s):
    if s is None:
        return 0.0
    try:
        v = float(s.replace(",", ""))
    except ValueError:
        return 0.0
    if not math.isfinite(v):
        return 0.0
    return v


def fmt(v):
    return "%.2f" % (v + 0.0) if round(v, 2) != 0 else "0.00"


def main(argv):
    if len(argv) != 3:
        print(USAGE)
        return 2
    path, gcol, acol = argv
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError, ValueError):
        print("error: cannot read " + path)
        return 1
    rows = [r for r in csv.reader(io.StringIO(text, newline="")) if r]
    header = rows[0] if rows else []
    data = rows[1:]
    if data and gcol not in header:
        print("error: no column " + gcol)
        return 1
    gi = header.index(gcol) if gcol in header else None
    ai = header.index(acol) if acol in header else None
    totals = {}
    for r in data:
        g = r[gi] if gi is not None and gi < len(r) else ""
        if g == "":
            g = "(blank)"
        a = parse_amount(r[ai]) if ai is not None and ai < len(r) else 0.0
        totals[g] = totals.get(g, 0.0) + a
    items = sorted(totals.items(), key=lambda kv: -kv[1])
    for g, t in items:
        print("%s: %s" % (g, fmt(t)))
    print("total: " + fmt(sum(totals.values())))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
