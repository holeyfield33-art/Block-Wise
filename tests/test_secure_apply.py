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


@pytest.mark.parametrize("into", ["../escape", "a/../../escape", "ABSOLUTE", "/abs", r"\abs", "C:/abs", "C:abs"])
def test_workspace_escape_via_into_is_blocked(tmp_path, into):
    root = tmp_path / "workspace"
    root.mkdir()
    if into == "ABSOLUTE":
        into = str(tmp_path / "abs_escape")
    receipt = secure_apply("csv_report", root, into)
    assert receipt["status"] == "refused"
    assert receipt["reason"] == "workspace_escape"
    assert [p for p in _py_files(tmp_path) if root not in p.parents] == []


def test_string_parameter_is_stored_as_a_literal_not_code(tmp_path):
    payload = "'); __import__('os').system('touch pwned'); ('"
    receipt = secure_apply("kv_store", tmp_path, ".", params={"store": payload})
    assert receipt["status"] == "approved"
    source = (tmp_path / receipt["outputs"][0]).read_text(encoding="utf-8")
    # The only occurrence of the payload is inside its quoted literal.
    assert payload not in source.replace(repr(payload), "")
    assert not (tmp_path / "pwned").exists()


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


def test_generation_uses_the_verified_copy_not_a_reload(tmp_path, monkeypatch):
    # The blueprint whose digest was checked must be the one generated from; if
    # generation reloaded the library, a changed file between the two loads
    # would be written under the old approval.
    import copy

    verified = copy.deepcopy(sa.load_blueprints()["csv_report"])
    verified["plan"]["modules"][0]["path"] = "verified_copy.py"
    monkeypatch.setattr(sa, "load_blueprints", lambda: {"csv_report": verified})
    receipt = secure_apply("csv_report", tmp_path, ".", approved={"csv_report": sa.canonical_digest(verified)},
                           references={"csv_report": sa.reference_output(verified)})
    assert receipt["status"] == "approved"
    assert receipt["outputs"] == ["verified_copy.py"]


def test_every_approved_blueprint_has_a_current_reference_output():
    # The drift alarm: if the compiler changes what an approved blueprint generates,
    # this fails until a person re-approves the new output.
    blueprints = sa.load_blueprints()
    references = sa.load_reference_outputs()
    for blueprint_id in load_approved():
        assert references.get(blueprint_id) == sa.reference_output(blueprints[blueprint_id]), blueprint_id


@pytest.mark.parametrize("references, reason", [({"csv_report": "sha256:" + "1" * 64}, "generator_changed"),
                                                ({}, "no_reference_output")])
def test_changed_or_missing_generator_output_is_refused(tmp_path, references, reason):
    receipt = secure_apply("csv_report", tmp_path, ".", references=references)
    assert receipt["status"] == "refused"
    assert receipt["reason"] == reason
    assert list(tmp_path.iterdir()) == []


def test_unverified_generation_is_rolled_back(tmp_path, monkeypatch):
    monkeypatch.setattr(sa, "check_project", lambda *a, **k: {"ok": False, "checked_functions": 1, "issues": ["x"]})
    receipt = secure_apply("csv_report", tmp_path, "tools/reports")
    assert receipt["status"] == "unverified"
    assert receipt["rolled_back"] == ["tools/reports/report.py"]
    assert list(tmp_path.iterdir()) == []  # no files, no plan, no folders left behind


def test_rollback_restores_an_existing_plan_and_keeps_existing_files(tmp_path, monkeypatch):
    assert secure_apply("kv_store", tmp_path, ".")["status"] == "approved"
    plan = (tmp_path / ".blockwise" / "plan.json").read_bytes()
    monkeypatch.setattr(sa, "check_project", lambda *a, **k: {"ok": False, "checked_functions": 0, "issues": []})
    assert secure_apply("csv_report", tmp_path, ".")["status"] == "unverified"
    assert (tmp_path / ".blockwise" / "plan.json").read_bytes() == plan
    assert sorted(p.name for p in tmp_path.glob("*.py")) == ["store.py"]


def test_receipt_records_the_parameters_used(tmp_path):
    receipt = secure_apply("kv_store", tmp_path, ".", params={"store": "notes.json"})
    assert receipt["params"] == {"file": "store", "store": "notes.json"}
    assert receipt["approved_output"] == sa.load_reference_outputs()["kv_store"]
