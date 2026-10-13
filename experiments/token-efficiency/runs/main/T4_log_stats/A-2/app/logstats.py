import sys

LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def main(argv):
    if len(argv) != 1:
        print("usage: logstats.py LOGFILE")
        return 2
    path = argv[0]
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.read().split("\n")
    except OSError:
        print("error: cannot read " + path)
        return 1
    if lines and lines[-1] == "":
        lines.pop()
    counts = {lv: 0 for lv in LEVELS}
    msgs = {}
    skipped = 0
    for line in lines:
        parts = line.split(None, 3)
        if len(parts) < 4 or parts[2] not in counts:
            skipped += 1
            continue
        counts[parts[2]] += 1
        if parts[2] in ("ERROR", "CRITICAL"):
            m = parts[3].strip()
            msgs[m] = msgs.get(m, 0) + 1
    out = []
    for lv in LEVELS:
        if counts[lv]:
            out.append("%s: %d" % (lv, counts[lv]))
    top = sorted(msgs.items(), key=lambda kv: -kv[1])[:3]  # stable sort
    for m, c in top:
        out.append("  %d x %s" % (c, m))
    if skipped:
        out.append("skipped %d unreadable line(s)" % skipped)
    if not out:
        out.append("No log lines found.")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
