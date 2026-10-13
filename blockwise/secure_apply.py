"""Secure Apply: a trusted boundary around blueprint generation.

An agent asks for an approved blueprint; this boundary enforces, in trusted
local code (never model instructions):

  * blueprint identity - the blueprint must match an approved SHA-256 digest in
    approved.json, or it is refused and nothing is written;
  * workspace containment - every file written must resolve inside the
    authorized project root, so a symlinked directory cannot redirect a write
    outside it;
  * fail-closed verification - the structural check must actually check at least
    one function and report no issues, or the receipt is not "approved".

The agent receives only a compact receipt, never the generated source. The
controls live here, not in the blueprint data or the model's instructions:
reference to a blueprint is not authority to generate it, and a successful
generation is not, by itself, an approval.
"""

import hashlib
import json
import platform
import sys
from importlib import resources
from pathlib import Path, PurePosixPath, PureWindowsPath

from .compiler import compile_score
from .presets import PresetError, load_blueprints, render_blueprint
from .probes import ProbeError, run_probes, summarize, validate_security
from .project import apply_blueprint, check_project, plan_path
from .schema import ScoreError

APPROVED_PACKAGE = "blockwise"
APPROVED_NAME = "approved.json"


def canonical_digest(blueprint):
    """Stable SHA-256 of a blueprint's content, independent of file formatting.

    Hashing the canonical JSON (sorted keys, no insignificant whitespace) rather
    than raw file bytes keeps the approved digest identical across platforms and
    line-ending conventions, while still changing the moment the content does.
    """
    body = json.dumps(blueprint, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()


def _manifest():
    return json.loads(resources.files(APPROVED_PACKAGE).joinpath(APPROVED_NAME).read_text(encoding="utf-8"))


def load_approved():
    """Return {blueprint_id: approved_digest} from the shipped approved.json."""
    return _manifest().get("blueprints", {})


def load_reference_outputs():
    """Return {blueprint_id: digest of its generated files at default parameters}.

    Approval pins the blueprint; this pins the generator. If the compiler's output
    for an approved blueprint changes, the blueprint is refused until a person
    re-approves the new output.
    """
    return _manifest().get("reference_outputs", {})


def reference_output(blueprint):
    """Digest of {path: source} generated from a blueprint at its default parameters."""
    return canonical_digest(compile_score(render_blueprint(blueprint)))


def effective_params(blueprint, params):
    """Every parameter's value for this generation: what was set, else the default."""
    return {name: (params or {}).get(name, spec.get("default")) for name, spec in blueprint["params"].items()}


def load_security_reviews():
    """Return {block_id: review record} - detector-check results a person committed to approved.json."""
    return _manifest().get("security_reviews", {})


def _security_receipt(blueprint, version, source, apply_receipt_id, reviews):
    """Probe the generated module and summarize the evidence; only all-HELD plus a current review passes."""
    try:
        security = validate_security(blueprint)
    except ProbeError as exc:
        return {"status": "not-reviewed", "reason": "invalid_security_section", "detail": str(exc)}
    results = run_probes(source, security)
    probe_status = summarize(results)["status"]
    review = reviews.get(blueprint["id"]) or {}
    review_current = (review.get("block_version") == version and review.get("real_block") == "held"
                      and review.get("total", 0) > 0 and review.get("killed") == review.get("total"))
    if probe_status == "not-held":
        status = "not-reviewed"
    elif probe_status == "held" and review_current:
        status = "security-reviewed"
    else:
        status = "probed-with-gaps"
    classes = {t["id"]: t["class"] for t in security["threats"]}
    held_threats = {t for t in classes if all(r["verdict"] == "HELD" for r in results if r["threat"] == t)}
    gaps = [f"{r['id']} not run: {r['detail']}" for r in results if r["verdict"] == "NOT_RUN"]
    if not review_current:
        gaps.append("no current detector-check review for this block version")
    receipt = {
        "status": status, "block": blueprint["id"], "block_version": version, "apply_receipt": apply_receipt_id,
        "threats": {"declared": len(classes), "held": len(held_threats)},
        "probes": [{"id": r["id"], "threat": r["threat"], "class": classes.get(r["threat"], "FUNCTIONAL"),
                    "verdict": r["verdict"], **({} if r["verdict"] == "HELD" else {"detail": r["detail"]})}
                   for r in results],
        "detector_check": ({k: review[k] for k in ("killed", "total", "mutant_suite", "platform", "date")}
                           if review_current else None),
        "gaps": gaps,
        "not_verified": security["not_verified"],
        "environment": {"python": platform.python_version(), "platform": sys.platform},
    }
    receipt["receipt_id"] = canonical_digest(receipt)
    return receipt


def _file_digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _within(root, destination):
    """True if the resolved destination is the root or sits inside it."""
    return root == destination or root in destination.parents


def _roll_back(fresh, new_dirs, plan_file, plan_before):
    """Undo a generation that is not an approval: remove files it created, restore the plan."""
    for target in fresh:
        if target.is_file():
            target.unlink()
    if plan_before is None:
        plan_file.unlink(missing_ok=True)
    else:
        plan_file.write_bytes(plan_before)
    for folder in sorted(new_dirs, key=lambda d: len(d.parts), reverse=True):
        try:
            folder.rmdir()
        except OSError:
            pass


def secure_apply(blueprint_id, project=".", into=".", params=None, approved=None, probe=False, reviews=None,
                 references=None):
    """Generate an approved blueprint behind the trust boundary; return a receipt.

    A receipt with ``status == "approved"`` means the blueprint matched its
    approved digest, every output stayed inside the authorized workspace, and
    the generator still produces the approved reference output, every output
    stayed inside the authorized workspace, and the structural check verified
    at least one function with no issues. Any other status means nothing should
    be trusted: refusals write no files, and an unverified generation is rolled
    back.

    With ``probe=True`` an approved security block's probes are then run
    against the module just written, and the receipt gains a ``security``
    section; its status is "security-reviewed" only if every probe HELD and a
    person has committed a current detector-check review for this version.
    """
    approved = load_approved() if approved is None else approved
    blueprints = load_blueprints()
    if blueprint_id not in blueprints:
        return {"status": "refused", "reason": "unknown_blueprint", "blueprint": blueprint_id}
    if blueprint_id not in approved:
        return {"status": "refused", "reason": "blueprint_not_approved", "blueprint": blueprint_id}
    actual = canonical_digest(blueprints[blueprint_id])
    if actual != approved[blueprint_id]:
        return {"status": "refused", "reason": "blueprint_hash_mismatch", "blueprint": blueprint_id,
                "approved_version": approved[blueprint_id], "actual_version": actual}
    references = load_reference_outputs() if references is None else references
    output_version = reference_output(blueprints[blueprint_id])
    if references.get(blueprint_id) != output_version:
        return {"status": "refused", "reason": "generator_changed" if blueprint_id in references else "no_reference_output",
                "blueprint": blueprint_id, "approved_output": references.get(blueprint_id), "actual_output": output_version}

    # Validate parameters by rendering first; this writes nothing.
    try:
        rendered = render_blueprint(blueprints[blueprint_id], params or {})
    except (PresetError, ScoreError) as exc:
        return {"status": "refused", "reason": "invalid_parameters", "blueprint": blueprint_id, "detail": str(exc)}

    # Workspace containment: resolve every target and confirm it stays inside the
    # authorized root. resolve() follows symlinks, so a symlinked subdirectory
    # cannot redirect a write outside the root even though the relative path is
    # itself normalized.
    root = Path(project).resolve()
    if not root.is_dir():
        return {"status": "refused", "reason": "workspace_not_found", "project": str(project)}
    # `into` is relative to the workspace. An absolute or drive-qualified path is
    # refused on every platform rather than reinterpreted (stripping a leading "/"
    # would silently turn "/tmp/x" into "tmp/x" inside the root).
    windows = PureWindowsPath(into)
    if PurePosixPath(into).is_absolute() or windows.drive or windows.root:
        return {"status": "refused", "reason": "workspace_escape", "path": into}
    prefix = "" if into in ("", ".") else into.strip("/") + "/"
    for module in rendered["modules"]:
        relative = prefix + module["path"]
        if not _within(root, (root / relative).resolve()):
            return {"status": "refused", "reason": "workspace_escape", "path": relative}

    # Remember what exists now, so a generation that is not approved can be undone.
    targets = [root / (prefix + module["path"]) for module in rendered["modules"]]
    fresh = [target for target in targets if not target.exists()]
    plan_file = plan_path(root)
    new_dirs = {folder for target in [*fresh, plan_file] for folder in target.parents
                if root in folder.parents and not folder.exists()}
    plan_before = plan_file.read_bytes() if plan_file.exists() else None
    try:
        # Generate from the exact copy whose digest was checked, never a fresh reload.
        result = apply_blueprint(str(root), blueprint_id, into, params or {}, blueprint=blueprints[blueprint_id])
    except (PresetError, ScoreError, OSError) as exc:
        _roll_back(fresh, new_dirs, plan_file, plan_before)
        return {"status": "refused", "reason": "generation_failed", "blueprint": blueprint_id, "detail": str(exc)}
    written = result["added"]

    # Fail-closed verification: a generation that produced nothing to check, or a
    # check that reports issues, is not an approval.
    check = check_project(str(root), strict=False)
    checked = check.get("checked_functions", 0)
    if checked < 1 or not check.get("ok"):
        _roll_back(fresh, new_dirs, plan_file, plan_before)
        return {"status": "unverified", "reason": "verification_incomplete", "blueprint": blueprint_id,
                "checked_functions": checked, "issues": check.get("issues", []), "rolled_back": written}

    output_hashes = [_file_digest(root / path) for path in written]
    receipt = {"status": "approved", "blueprint": blueprint_id, "approved_version": actual,
               "approved_output": output_version, "params": effective_params(blueprints[blueprint_id], params),
               "workspace": "authorized", "outputs": written, "output_hashes": output_hashes,
               "checks": f"passed ({checked} function{'' if checked == 1 else 's'})"}
    receipt["receipt_id"] = "sha256:" + hashlib.sha256(
        json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    if probe:
        blueprint = blueprints[blueprint_id]
        if "security" not in blueprint:
            receipt["security"] = {"status": "not-reviewed", "reason": "not_a_security_block"}
        else:
            source = root / (prefix + rendered["modules"][0]["path"])
            reviews = load_security_reviews() if reviews is None else reviews
            receipt["security"] = _security_receipt(blueprint, actual, source, receipt["receipt_id"], reviews)
    return receipt
