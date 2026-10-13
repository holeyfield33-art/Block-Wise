"""Security blocks: every shipped block's probes hold on the real code and catch every mutant.

Mutants (tests/mutants/<block>.json) are the block with one control removed or
done wrong. This is release gate G4: it proves the probes can detect a missing
control, so a clean probe run means something.
"""

import copy
import json
import re
from pathlib import Path

import pytest

from blockwise import secure_apply as sa
from blockwise.cli import main
from blockwise.presets import load_blueprints
from blockwise.probes import canonical_digest, detector_check, validate_security
from blockwise.secure_apply import load_approved, load_security_reviews, secure_apply

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
    for path in (ROOT / "blockwise").glob("*.py"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if ("approved" in line.lower() or "APPROVED_NAME" in line) and writers.search(line):
                pytest.fail(f"{path.name} may write the approval manifest: {line.strip()}")


# --- Security receipts from secure_apply(probe=True) (slice S3) -------------------------------

BLOCK = load_blueprints()["safe_write_text"]
VERSION = canonical_digest(BLOCK)
APPROVED = {"safe_write_text": VERSION}


def _review(**changes):
    return {"safe_write_text": {"block_version": VERSION, "real_block": "held", "killed": 5, "total": 5,
                                "mutant_suite": "sha256:x", "platform": "linux", "date": "2026-10-13", **changes}}


def test_probe_receipt_with_a_current_review(tmp_path):
    receipt = secure_apply("safe_write_text", tmp_path, ".", approved=APPROVED, probe=True, reviews=_review())
    security = receipt["security"]
    assert receipt["status"] == "approved"
    assert security["apply_receipt"] == receipt["receipt_id"]
    assert security["block_version"] == VERSION
    verdicts = {p["id"]: p["verdict"] for p in security["probes"]}
    assert set(verdicts.values()) <= {"HELD", "NOT_RUN"}
    # Only a platform that ran every probe may say security-reviewed (symlinks need rights on Windows).
    expected = "probed-with-gaps" if "NOT_RUN" in verdicts.values() else "security-reviewed"
    assert security["status"] == expected
    assert security["detector_check"]["killed"] == 5
    assert security["not_verified"]
    assert security["receipt_id"].startswith("sha256:")
    # Probing imports the written module without leaving bytecode caches in the workspace.
    assert not list(tmp_path.glob("**/__pycache__"))


@pytest.mark.parametrize("reviews", [{}, _review(block_version="sha256:old"), _review(real_block="held-with-gaps"),
                                     _review(killed=4)])
def test_missing_or_stale_review_is_never_security_reviewed(tmp_path, reviews):
    security = secure_apply("safe_write_text", tmp_path, ".", approved=APPROVED, probe=True, reviews=reviews)["security"]
    assert security["status"] == "probed-with-gaps"
    assert security["detector_check"] is None
    assert any("detector-check" in gap for gap in security["gaps"])


def test_a_weakened_block_that_is_approved_still_fails_its_probes(tmp_path, monkeypatch):
    # Even if someone approves a block whose size check was removed, the probes run
    # on the code actually written and the receipt says not-reviewed.
    weak = copy.deepcopy(BLOCK)
    body = weak["plan"]["modules"][0]["functions"][1]["body"]
    weak["plan"]["modules"][0]["functions"][1]["body"] = [n for n in body if n["kind"] != "branch"]
    monkeypatch.setattr(sa, "load_blueprints", lambda: {"safe_write_text": weak})
    receipt = secure_apply("safe_write_text", tmp_path, ".", approved={"safe_write_text": canonical_digest(weak)},
                           probe=True, reviews={})
    assert receipt["status"] == "approved"  # identity, workspace and structure are fine...
    security = receipt["security"]
    assert security["status"] == "not-reviewed"  # ...but the security probes are not.
    assert {p["id"]: p["verdict"] for p in security["probes"]}["P5"] == "BYPASSED"


def test_probe_on_a_block_without_a_security_section(tmp_path):
    receipt = secure_apply("csv_report", tmp_path, ".", probe=True)
    assert receipt["security"] == {"status": "not-reviewed", "reason": "not_a_security_block"}


def test_shipped_approval_and_review_match_the_current_block():
    # Editing the block (code, threats or probes) without a fresh review must break here.
    assert load_approved()["safe_write_text"] == VERSION
    review = load_security_reviews()["safe_write_text"]
    assert review["block_version"] == VERSION and review["real_block"] == "held"
    assert review["killed"] == review["total"] == 5
    suite = json.loads((MUTANTS / "safe_write_text.json").read_text(encoding="utf-8"))
    assert review["mutant_suite"] == canonical_digest(suite)


def test_cli_probe_and_review_exit_codes(tmp_path, capsys):
    # Approved in the shipped manifest: exit 0 only where the receipt says security-reviewed
    # (a host that cannot run every probe, e.g. Windows without symlink rights, gets gaps and 1).
    code = main(["secure-apply", "safe_write_text", "--project", str(tmp_path), "--probe"])
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["status"] == "approved"
    assert code == (0 if receipt["security"]["status"] == "security-reviewed" else 1)
    code = main(["security-review", "safe_write_text", "--mutants", str(MUTANTS / "safe_write_text.json")])
    result = json.loads(capsys.readouterr().out)
    assert result["record"]["block_version"] == VERSION
    assert result["record"]["killed"] == result["record"]["total"] == 5
    assert code == (0 if result["record"]["real_block"] == "held" else 1)
