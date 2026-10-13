"""The Secure Apply trust boundary: approved identity, workspace containment,
fail-closed verification, and the receipt. Refusals must write nothing."""

import hashlib
from pathlib import Path

import pytest

from blockwise import secure_apply as sa
from blockwise.cli import main
from blockwise.secure_apply import load_approved, secure_apply


def _py_files(root):
    return list(Path(root).glob("**/*.py"))


def test_approved_blueprint_returns_a_valid_receipt(tmp_path):
    receipt = secure_apply("csv_report", tmp_path, ".")
    assert receipt["status"] == "approved"
    assert receipt["workspace"] == "authorized"
    assert receipt["outputs"] == ["report.py"]
    assert receipt["checks"].startswith("passed (")
    assert receipt["approved_version"] == load_approved()["csv_report"]
    assert receipt["receipt_id"].startswith("sha256:")
    # The output hash in the receipt matches the file actually written.
    written = (tmp_path / "report.py").read_bytes()
    assert receipt["output_hashes"] == ["sha256:" + hashlib.sha256(written).hexdigest()]


def test_tampered_blueprint_is_refused_and_writes_nothing(tmp_path):
    forged = dict(load_approved())
    forged["csv_report"] = "sha256:" + "0" * 64
    receipt = secure_apply("csv_report", tmp_path, ".", approved=forged)
    assert receipt["status"] == "refused"
    assert receipt["reason"] == "blueprint_hash_mismatch"
    assert _py_files(tmp_path) == []


def test_unapproved_blueprint_is_refused_and_writes_nothing(tmp_path):
    receipt = secure_apply("csv_report", tmp_path, ".", approved={})
    assert receipt == {"status": "refused", "reason": "blueprint_not_approved", "blueprint": "csv_report"}
    assert _py_files(tmp_path) == []


def test_unknown_blueprint_is_refused(tmp_path):
    receipt = secure_apply("does_not_exist", tmp_path)
    assert receipt["status"] == "refused"
    assert receipt["reason"] == "unknown_blueprint"


def test_invalid_parameters_are_refused_before_any_write(tmp_path):
    receipt = secure_apply("csv_report", tmp_path, ".", params={"not_a_real_param": "x"})
    assert receipt["status"] == "refused"
    assert receipt["reason"] == "invalid_parameters"
    assert _py_files(tmp_path) == []


def test_workspace_escape_via_symlink_is_blocked(tmp_path):
    root = tmp_path / "workspace"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    try:
        (root / "link").symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation not permitted on this host")
    receipt = secure_apply("csv_report", root, "link")
    assert receipt["status"] == "refused"
    assert receipt["reason"] == "workspace_escape"
    assert _py_files(outside) == []


def test_verification_failure_is_not_an_approval(tmp_path, monkeypatch):
    # Force the structural check to report nothing checked: a generation that
    # cannot be verified must never come back "approved".
    monkeypatch.setattr(sa, "check_project", lambda *a, **k: {"ok": True, "checked_functions": 0, "issues": []})
    receipt = secure_apply("csv_report", tmp_path, ".")
    assert receipt["status"] == "unverified"
    assert receipt["reason"] == "verification_incomplete"
    assert receipt["checked_functions"] == 0


def test_cli_returns_zero_on_approval_and_nonzero_on_refusal(tmp_path, capsys):
    assert main(["secure-apply", "csv_report", "--project", str(tmp_path)]) == 0
    capsys.readouterr()
    assert main(["secure-apply", "does_not_exist", "--project", str(tmp_path)]) == 1
