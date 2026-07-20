"""Path helpers for safe output naming."""
from __future__ import annotations

from pathlib import Path


def next_available_path(path: Path) -> Path:
    """Return a non-existing path by appending an incrementing numeric suffix."""
    if not path.exists():
        return path

    parent = path.parent
    stem = path.stem
    suffix = path.suffix

    index = 1
    while True:
        candidate = parent / f"{stem}_{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def common_parent_dir(paths: list[Path]) -> Path | None:
    """Return common parent directory when all paths share one; otherwise None."""
    if not paths:
        return None

    parent = paths[0].parent
    for path in paths[1:]:
        if path.parent != parent:
            return None
    return parent
