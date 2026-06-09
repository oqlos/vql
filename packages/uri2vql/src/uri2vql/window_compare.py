"""Compare capture fingerprint against a VQL program baseline."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def compare_window_image(
    image: str | Path,
    *,
    vql_program: str | Path,
) -> dict[str, Any]:
    """Compare capture fingerprint against stored VQL program baseline."""
    try:
        from img2vql.fingerprint import compare_with_program

        payload = compare_with_program(image, vql_program)
    except ImportError:
        return {
            "ok": False,
            "error": "img2vql/img2nl not installed for fingerprint compare",
            "match": False,
        }
    payload["path"] = str(image)
    payload["vql_program"] = str(vql_program)
    return payload
