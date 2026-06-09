"""Optional img2nl fingerprint enrichment for adopted programs."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def optional_fingerprint(image_path: Path) -> dict[str, Any]:
    """Best-effort fingerprint when img2nl is available without img2vql."""
    try:
        from PIL import Image
        from img2nl.features.fingerprint import analyze_fingerprint

        fp = analyze_fingerprint(Image.open(image_path))
        return {"fingerprint": fp} if fp.get("available") else {}
    except ImportError:
        return {}


def enrich_program_metadata(base: dict[str, Any], path: Path) -> dict[str, Any]:
    try:
        from img2vql.metadata import merge_program_metadata

        return merge_program_metadata(base, path)
    except ImportError:
        meta = {
            **base,
            "analyzed_at": datetime.now(UTC).isoformat(),
            "image": str(path),
            **optional_fingerprint(path),
        }
        return meta
