"""Security blocks: every shipped block's probes hold on the real code and catch every mutant.

Mutants (tests/mutants/<block>.json) are the block with one control removed or
done wrong. This is release gate G4: it proves the probes can detect a missing
control, so a clean probe run means something.
"""

import json
import re
from pathlib import Path

import pytest

from blockwise.presets import load_blueprints
from blockwise.probes import detector_check, validate_security

ROOT = Path(__file__).resolve().parents[1]
MUTANTS = Path(__file__).parent / "mutants"
SECURITY_BLOCKS = sorted(k for k, v in load_blueprints().items() if "security" in v)


def test_there_is_at_least_one_security_block():
    assert "safe_write_text" in SECURITY_BLOCKS


@pytest.mark.parametrize("block_id", SECURITY_BLOCKS)
def test_security_block_passes_gates_and_kills_every_mutant(block_id):
    blueprint = load_blueprints()[block_id]
    validate_security(blueprint)
    suite_path = MUTANTS / f"{block_id}.json"
    assert suite_path.is_file(), f"security block {block_id} needs a mutant suite at {suite_path}"
    report = detector_check(blueprint, json.loads(suite_path.read_text(encoding="utf-8")))
    held = {r["id"]: r["verdict"] for r in report["real_results"]}
    assert all(v in ("HELD", "NOT_RUN") for v in held.values()), held
    survivors = [m for m in report["mutants"] if not m["killed"]]
    assert survivors == [], survivors
    assert report["ok"]


def test_no_code_path_writes_the_approval_manifest():
    # Release gate G7: approvals are human-reviewed commits. Library code may read
    # approved.json, but nothing in the package may open it for writing.
    # A line-level grep: a heuristic, but it catches the obvious regression.
    writers = re.compile(r"write_text|write_bytes|json\.dump\(|open\(")
    mentions = []
    for path in (ROOT / "blockwise").glob("*.py"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if "approved.json" in line:
                mentions.append(path.name)
            if "approved" in line.lower() and writers.search(line):
                pytest.fail(f"{path.name} may write the approval manifest: {line.strip()}")
    assert set(mentions) <= {"secure_apply.py"}
