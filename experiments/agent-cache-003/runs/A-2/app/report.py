import csv
import math
import sys


def parse_amount(s):
    if s is None:
        return 0.0
    s = s.replace(",", "").strip()
    if not s:
        return 0.0
    try:
        v = float(s)
    except ValueError:
        return 0.0
    if not math.isfinite(v):
        return 0.0
    return v


def main(argv):
    if len(argv) != 3:
        print("usage: report.py FILE GROUP_COLUMN AMOUNT_COLUMN")
        return 2
    path, gcol, acol = argv
    try:
        with open(path, encoding="utf-8-sig", errors="replace", newline="") as f:
            rows = list(csv.reader(f))
    except (OSError, csv.Error):
        print("error: cannot read %s" % path)
        return 1
    header = rows[0] if rows else []
    data = [r for r in rows[1:] if r]
    if data and gcol not in header:
        print("error: no column %s" % gcol)
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
    grand = 0.0
    for g, t in items:
        print("%s: %.2f" % (g, t + 0.0))
        grand += t
    print("total: %.2f" % (grand + 0.0))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
