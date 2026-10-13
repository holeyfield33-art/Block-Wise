import sys

LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def main(argv):
    if len(argv) != 1:
        print("usage: logstats.py LOGFILE")
        return 2
    name = argv[0]
    try:
        with open(name, "rb") as f:
            data = f.read()
    except (OSError, ValueError):
        print("error: cannot read %s" % name)
        return 1
    text = data.decode("utf-8", errors="replace")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    counts = {l: 0 for l in LEVELS}
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
    for l in LEVELS:
        if counts[l]:
            out.append("%s: %d" % (l, counts[l]))
    top = sorted(msgs.items(), key=lambda kv: -kv[1])[:3]
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
