"""Fingerprint helpers — persist in vql.json and compare captures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def fingerprint_for_image(image_path: str | Path) -> dict[str, Any] | None:
    """Compute perceptual hash fingerprint for an image file."""
    try:
        from PIL import Image
        from img2nl.features.fingerprint import analyze_fingerprint
    except ImportError:
        return None

    path = Path(image_path).expanduser()
    if not path.is_file():
        return None
    im = Image.open(path)
    fp = analyze_fingerprint(im)
    return fp if fp.get("available") else None


def load_program_fingerprint(vql_program: str | Path | None) -> dict[str, Any] | None:
    """Load stored fingerprint from VQL program metadata."""
    if not vql_program:
        return None
    path = Path(vql_program).expanduser()
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    fp = data.get("metadata", {}).get("fingerprint")
    if isinstance(fp, dict) and fp.get("available"):
        return fp
    return None


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except (AttributeError, ValueError):
            pass
    return value


def compare_with_program(
    image_path: str | Path,
    vql_program: str | Path,
    *,
    hash_threshold: int = 5,
) -> dict[str, Any]:
    """Compare image fingerprint against stored program baseline."""
    ref = load_program_fingerprint(vql_program)
    if not ref:
        return {
            "ok": False,
            "error": "no fingerprint in program metadata; run analyze/adopt first",
            "match": False,
        }

    try:
        from img2nl import analyze_image
    except ImportError:
        return {"ok": False, "error": "img2nl not installed", "match": False}

    result = analyze_image(
        image_path,
        skip_thumbnail=True,
        reference_fingerprint=ref,
    )
    if not result.ok:
        return {"ok": False, "error": result.error or "analyze failed", "match": False}

    similarity = result.features.get("similarity", {})
    scene = result.features.get("scene", {})
    special = result.features.get("special_hits", {})
    return _json_safe(
        {
            "ok": True,
            "match": bool(similarity.get("match")),
            "phash_distance": similarity.get("phash_distance"),
            "hash_threshold": hash_threshold,
            "scene_class": scene.get("scene_class"),
            "reference_phash": ref.get("phash", ""),
            "current_phash": result.features.get("fingerprint", {}).get("phash", ""),
            "similarity": similarity,
            "special_hits": {
                "has_qr": special.get("has_qr", False),
                "has_text": special.get("has_text", False),
                "barcode_count": special.get("barcodes", {}).get("count", 0),
                "ocr_preview": special.get("ocr", {}).get("text_preview", ""),
            },
        }
    )
