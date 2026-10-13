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
    except OSError:
        print(f"error: cannot read {name}")
        return 1
    text = data.decode("utf-8", errors="replace")
    lines = text.split("\n")
    while lines and not lines[-1].strip():
        lines.pop()

    counts = {l: 0 for l in LEVELS}
    msgs = {}
    skipped = 0
    for line in lines:
        parts = line.split(None, 3)
        if len(parts) >= 4 and parts[2] in counts:
            lvl = parts[2]
            counts[lvl] += 1
            if lvl in ("ERROR", "CRITICAL"):
                m = parts[3].strip()
                msgs[m] = msgs.get(m, 0) + 1
        else:
            skipped += 1

    out = []
    for l in LEVELS:
        if counts[l]:
            out.append(f"{l}: {counts[l]}")
    top = sorted(msgs.items(), key=lambda kv: -kv[1])[:3]  # stable sort keeps first-seen order
    for m, c in top:
        out.append(f"  {c} x {m}")
    if skipped:
        out.append(f"skipped {skipped} unreadable line(s)")
    if not out:
        out.append("No log lines found.")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
