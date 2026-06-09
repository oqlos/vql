"""Refresh img2nl metadata in an adopted VQL program."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def refresh_window_metadata(
    image: str | Path,
    *,
    vql_program: str | Path,
    locale: str = "pl",
) -> dict[str, Any]:
    """Refresh img2nl metadata in program without rebuilding VQL layers."""
    try:
        from img2vql.metadata import refresh_program_metadata

        payload = refresh_program_metadata(vql_program, image, locale=locale)
    except ImportError:
        return {
            "ok": False,
            "error": "img2vql/img2nl not installed for metadata refresh",
        }
    payload["vql_program"] = str(vql_program)
    return payload
