"""Add sibling monorepo packages to sys.path when not pip-installed."""

from __future__ import annotations

import sys
from pathlib import Path


def _repo_root() -> Path:
    # .../packages/uri2vql/src/uri2vql/_bootstrap.py → repo root (vql/)
    return Path(__file__).resolve().parents[4]


def _prepend(path: Path) -> None:
    text = str(path)
    if path.is_dir() and text not in sys.path:
        sys.path.insert(0, text)


def ensure_img2vql() -> None:
    try:
        import img2vql  # noqa: F401
        return
    except ImportError:
        pass

    root = _repo_root()
    _prepend(root / "packages" / "img2vql" / "src")

    # img2nl sibling clone (~/github/wronai/img2nl when vql is ~/github/oqlos/vql)
    for candidate in (
        root.parent.parent / "wronai" / "img2nl" / "src",
        root / ".." / ".." / "wronai" / "img2nl" / "src",
    ):
        _prepend(candidate.resolve())
