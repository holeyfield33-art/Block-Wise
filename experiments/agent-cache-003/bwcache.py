"""bwcache: hash-pinned, on-demand access to approved Block-Wise blueprints (prototype, Experiment 003).

Wraps the unchanged Block-Wise CLI. It never prints source code; every command prints one compact
JSON line.

  bwcache index                     approved ids, one-line purpose, program name
  bwcache get <id>                  the approved record for one blueprint (version, hashes, apply command)
  bwcache apply <id> --into <dir>   verify the pinned blueprint hash, generate, verify the program hash
  bwcache verify                    re-check every pin against the installed library

Exit codes: 0 ok, 2 bad input, 3 not approved (unknown id or hash mismatch).
Environment: BWCACHE_PINS (pins file, default: manifest/PINS_v1.json next to this file).
"""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

PINS = Path(os.environ.get("BWCACHE_PINS", Path(__file__).resolve().parent / "manifest" / "PINS_v1.json"))


def emit(data, code=0):
    print(json.dumps(data, separators=(",", ":")))
    raise SystemExit(code)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def library_blueprint_bytes(bp):
    from importlib import resources
    return resources.files("blockwise.library").joinpath("blueprints", f"{bp}.json").read_bytes()


def load_pins():
    return json.loads(PINS.read_text(encoding="utf-8"))


def record(pins, bp):
    entry = pins["blueprints"].get(bp)
    if entry is None:
        emit({"ok": False, "error": f"{bp} is not an approved blueprint", "version": pins["version"]}, 3)
    return entry


def check_blueprint(pins, bp):
    entry = record(pins, bp)
    try:
        actual = sha(library_blueprint_bytes(bp))
    except FileNotFoundError:
        emit({"ok": False, "error": f"{bp} is missing from the installed library", "version": pins["version"]}, 3)
    if actual != entry["blueprint_sha256"]:
        emit({"ok": False, "error": f"{bp} changed since it was approved; not trusted", "version": pins["version"],
              "pinned": entry["blueprint_sha256"][:16], "installed": actual[:16]}, 3)
    return entry


def main(argv):
    if not argv:
        emit({"ok": False, "error": "usage: bwcache index|get <id>|apply <id> --into <dir>|verify"}, 2)
    pins, command = load_pins(), argv[0]
    if command == "index":
        emit({"ok": True, "version": pins["version"],
              "blueprints": [{"id": k, "does": v["does"], "program": v["program"]} for k, v in pins["blueprints"].items()]})
    if command == "get" and len(argv) == 2:
        entry = record(pins, argv[1])
        emit({"ok": True, "version": pins["version"], "id": argv[1], **entry,
              "apply": f"bwcache apply {argv[1]} --into app"})
    if command == "apply" and len(argv) == 4 and argv[2] == "--into":
        bp, into = argv[1], Path(argv[3])
        entry = check_blueprint(pins, bp)
        target = into / entry["program"]
        if target.exists():
            emit({"ok": False, "error": f"{target} already exists; not regenerating"}, 2)
        r = subprocess.run([sys.executable, "-m", "blockwise", "apply", bp, "--into", str(into)], capture_output=True, text=True)
        if r.returncode != 0:
            emit({"ok": False, "error": "generation failed", "detail": r.stdout.strip()[:200]}, 3)
        if sha(target.read_bytes()) != entry["program_sha256"]:
            target.rename(target.with_name(target.name + ".unapproved"))
            emit({"ok": False, "error": "generated program does not match the approved hash; quarantined"}, 3)
        emit({"ok": True, "version": pins["version"], "id": bp, "file": str(target), "hash_verified": True})
    if command == "verify":
        bad = []
        for bp, entry in pins["blueprints"].items():
            try:
                if sha(library_blueprint_bytes(bp)) != entry["blueprint_sha256"]:
                    bad.append(bp)
            except FileNotFoundError:
                bad.append(bp)
        emit({"ok": not bad, "version": pins["version"], "changed": bad}, 0 if not bad else 3)
    emit({"ok": False, "error": "usage: bwcache index|get <id>|apply <id> --into <dir>|verify"}, 2)


if __name__ == "__main__":
    main(sys.argv[1:])
