import sys

LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def main(argv):
    if len(argv) != 1:
        print("usage: logstats.py LOGFILE")
        return 2
    path = argv[0]
    try:
        with open(path, "rb") as f:
            text = f.read().decode("utf-8", errors="replace")
    except OSError:
        print("error: cannot read %s" % path)
        return 1
    lines = text.split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    counts = {l: 0 for l in LEVELS}
    msgs = {}
    skipped = 0
    for line in lines:
        parts = line.split(None, 3)
        if len(parts) >= 4 and parts[2] in counts:
            counts[parts[2]] += 1
            if parts[2] in ("ERROR", "CRITICAL"):
                m = parts[3].strip()
                msgs[m] = msgs.get(m, 0) + 1
        else:
            skipped += 1
    out = ["%s: %d" % (l, counts[l]) for l in LEVELS if counts[l]]
    for m, c in sorted(msgs.items(), key=lambda kv: -kv[1])[:3]:
        out.append("  %d x %s" % (c, m))
    if skipped:
        out.append("skipped %d unreadable line(s)" % skipped)
    if not out:
        out.append("No log lines found.")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
