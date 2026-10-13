import csv
import math
import sys


def parse_amount(text):
    if text is None:
        return 0.0
    try:
        v = float(text.replace(",", ""))
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
        with open(path, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.reader(f))
    except (OSError, UnicodeDecodeError, csv.Error):
        print("error: cannot read " + path)
        return 1
    header = rows[0] if rows else []
    data = [r for r in rows[1:] if r]
    if data and gcol not in header:
        print("error: no column " + gcol)
        return 1
    totals = {}
    if data:
        gi = header.index(gcol)
        ai = header.index(acol) if acol in header else None
        for r in data:
            g = r[gi] if gi < len(r) else ""
            if g == "":
                g = "(blank)"
            a = parse_amount(r[ai]) if ai is not None and ai < len(r) else 0.0
            totals[g] = totals.get(g, 0.0) + a
    items = sorted(totals.items(), key=lambda kv: -kv[1])
    out = []
    for g, t in items:
        out.append("%s: %.2f" % (g, t + 0.0))
    out.append("total: %.2f" % (sum(totals.values()) + 0.0))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
