"""Bounded, non-executing repository reader used by the plan checker.

Adapted from the Sonic Code Studio S2 scanner: links are refused, sizes are
bounded, and files are read as bytes only. Nothing is imported or executed.
"""

import os
import stat
from pathlib import Path

DEFAULT_EXCLUDES = (".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache",
                    ".blockwise")
MAX_FILES = 2048
MAX_FILE_BYTES = 2_000_000
MAX_TOTAL_BYTES = 50_000_000


class ScanError(ValueError):
    pass


def _is_link(path, info):
    return stat.S_ISLNK(info.st_mode) or (os.name == "nt" and bool(getattr(info, "st_file_attributes", 0) & 0x400))


def scan(root, excludes=DEFAULT_EXCLUDES, suffixes=(".py",)):
    """Return [{"path", "bytes"}] for regular files under root with the given suffixes."""
    root_path = Path(root)
    if not root_path.is_dir() or _is_link(root_path, root_path.lstat()):
        raise ScanError("Project must be a regular directory, not a link")
    root_path = root_path.resolve()
    records, total = [], 0
    for directory, folders, files in os.walk(root_path):
        folders[:] = sorted(f for f in folders if f not in excludes
                            and not _is_link(Path(directory) / f, (Path(directory) / f).lstat()))
        for name in sorted(files):
            path = Path(directory) / name
            info = path.lstat()
            if _is_link(path, info) or not stat.S_ISREG(info.st_mode) or path.suffix not in suffixes:
                continue
            if info.st_size > MAX_FILE_BYTES:
                raise ScanError(f"File exceeds {MAX_FILE_BYTES} bytes: {path.relative_to(root_path)}")
            data = path.read_bytes()
            total += len(data)
            if total > MAX_TOTAL_BYTES or len(records) >= MAX_FILES:
                raise ScanError("Project exceeds the checker's size bounds")
            records.append({"path": path.relative_to(root_path).as_posix(), "bytes": data})
    return records
