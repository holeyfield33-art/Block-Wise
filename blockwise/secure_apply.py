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
from importlib import resources
from pathlib import Path

from .presets import PresetError, load_blueprints, render_blueprint
from .project import apply_blueprint, check_project
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


def load_approved():
    """Return {blueprint_id: approved_digest} from the shipped approved.json."""
    data = resources.files(APPROVED_PACKAGE).joinpath(APPROVED_NAME).read_text(encoding="utf-8")
    return json.loads(data).get("blueprints", {})


def _file_digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _within(root, destination):
    """True if the resolved destination is the root or sits inside it."""
    return root == destination or root in destination.parents


def secure_apply(blueprint_id, project=".", into=".", params=None, approved=None):
    """Generate an approved blueprint behind the trust boundary; return a receipt.

    A receipt with ``status == "approved"`` means the blueprint matched its
    approved digest, every output stayed inside the authorized workspace, and
    the structural check verified at least one function with no issues. Any
    other status means nothing should be trusted; refusals write no files.
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
    prefix = "" if into in ("", ".") else into.strip("/") + "/"
    for module in rendered["modules"]:
        relative = prefix + module["path"]
        if not _within(root, (root / relative).resolve()):
            return {"status": "refused", "reason": "workspace_escape", "path": relative}

    try:
        result = apply_blueprint(str(root), blueprint_id, into, params or {})
    except (PresetError, ScoreError, OSError) as exc:
        return {"status": "refused", "reason": "generation_failed", "blueprint": blueprint_id, "detail": str(exc)}
    written = result["added"]

    # Fail-closed verification: a generation that produced nothing to check, or a
    # check that reports issues, is not an approval.
    check = check_project(str(root), strict=False)
    checked = check.get("checked_functions", 0)
    if checked < 1 or not check.get("ok"):
        return {"status": "unverified", "reason": "verification_incomplete", "blueprint": blueprint_id,
                "checked_functions": checked, "issues": check.get("issues", []), "outputs": written}

    output_hashes = [_file_digest(root / path) for path in written]
    receipt = {"status": "approved", "blueprint": blueprint_id, "approved_version": actual,
               "workspace": "authorized", "outputs": written, "output_hashes": output_hashes,
               "checks": f"passed ({checked} function{'' if checked == 1 else 's'})"}
    receipt["receipt_id"] = "sha256:" + hashlib.sha256(
        json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return receipt
