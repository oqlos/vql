"""img2nl metadata slices persisted into VQL program JSON."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from img2vql.fingerprint import load_program_fingerprint


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


def _compact_special_hits(special: dict[str, Any]) -> dict[str, Any]:
    barcodes = special.get("barcodes", {})
    ocr = special.get("ocr", {})
    return {
        "has_qr": bool(special.get("has_qr")),
        "has_text": bool(special.get("has_text")),
        "barcode_count": int(barcodes.get("count", 0)),
        "ocr_preview": str(ocr.get("text_preview", ""))[:200],
    }


def _text_likely(features: dict[str, Any], special: dict[str, Any]) -> bool:
    """True when heuristics suggest OCR is worth trying."""
    if special.get("has_text"):
        return False
    edges = features.get("edges", {})
    scene = features.get("scene", {})
    ocr = special.get("ocr", {})
    if edges.get("text_likelihood"):
        return True
    if ocr.get("skipped"):
        return True
    return scene.get("scene_class") in {"ui_with_text", "dense_ui_or_code", "ui_blocks"}


def rapidocr_special_hits(
    image_path: str | Path,
    *,
    max_lines: int = 5,
    max_chars: int = 200,
) -> dict[str, Any]:
    """Run rapidocr when img2nl OCR was skipped or missed text."""
    path = Path(image_path).expanduser()
    if not path.is_file():
        return {}

    try:
        from rapidocr_onnxruntime import RapidOCR
        import numpy as np
        from PIL import Image
    except ImportError:
        return {}

    try:
        rgb = Image.open(path).convert("RGB")
        engine = RapidOCR()
        result, _elapsed = engine(np.array(rgb))
    except Exception:
        return {}

    lines: list[str] = []
    if result:
        for row in result:
            if len(row) >= 2 and row[1]:
                lines.append(str(row[1]).strip())

    if not lines:
        return {}

    preview = " ".join(lines[:max_lines]).strip()
    if len(preview) > max_chars:
        preview = preview[: max_chars - 3] + "..."

    return {
        "has_text": True,
        "ocr": {
            "available": True,
            "skipped": False,
            "lines": lines[:max_lines],
            "text_preview": preview,
            "line_count": len(lines),
            "has_text": True,
            "source": "rapidocr",
        },
    }


def auto_ocr_special_hits(
    image_path: str | Path,
    features: dict[str, Any],
) -> dict[str, Any]:
    """Try rapidocr then imgl when img2nl did not extract text but UI looks textual."""
    special = features.get("special_hits", {})
    if not _text_likely(features, special):
        return {}

    path = Path(image_path).expanduser()
    rapid = rapidocr_special_hits(path)
    if rapid.get("has_text"):
        return rapid
    return imgl_ocr_special_hits(path)


def imgl_ocr_special_hits(
    image_path: str | Path,
    *,
    lang: str = "eng",
    max_lines: int = 5,
    max_chars: int = 200,
) -> dict[str, Any]:
    """Run imgl Tesseract OCR and return a special_hits-shaped slice."""
    try:
        from imgl.ocr import get_ocr_backend
        from imgl.preprocess import preprocess
    except ImportError:
        return {}

    path = Path(image_path).expanduser()
    if not path.is_file():
        return {}

    try:
        prepared = preprocess(path)
        boxes = get_ocr_backend("tesseract").run(prepared.image, lang=lang)
    except Exception:
        return {}

    lines = [box.text.strip() for box in boxes if box.text.strip()]
    preview = " ".join(lines[:max_lines]).strip()
    if len(preview) > max_chars:
        preview = preview[: max_chars - 3] + "..."

    if not lines:
        return {}

    return {
        "has_text": True,
        "ocr": {
            "available": True,
            "skipped": False,
            "lines": lines[:max_lines],
            "text_preview": preview,
            "line_count": len(lines),
            "has_text": True,
            "source": "imgl_tesseract",
        },
    }


def _merge_special_hits(
    img2nl_special: dict[str, Any],
    imgl_special: dict[str, Any],
) -> dict[str, Any]:
    """Prefer img2nl barcodes/QR; fill OCR from imgl when img2nl missed text."""
    if not imgl_special.get("has_text"):
        return _compact_special_hits(img2nl_special)

    merged = dict(img2nl_special)
    ocr = dict(merged.get("ocr", {}))
    ocr.update(imgl_special.get("ocr", {}))
    merged["ocr"] = ocr
    merged["has_text"] = True
    return _compact_special_hits(merged)


def img2nl_metadata_slice(
    image_path: str | Path,
    *,
    locale: str = "pl",
    reference_fingerprint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run img2nl once and return compact metadata for vql.json."""
    try:
        from img2nl import analyze_image
    except ImportError:
        return {}

    path = Path(image_path).expanduser()
    if not path.is_file():
        return {}

    result = analyze_image(
        path,
        skip_thumbnail=True,
        locale=locale,
        reference_fingerprint=reference_fingerprint,
    )
    if not result.ok:
        return {"img2nl_error": result.error or "analyze failed"}

    features = result.features
    special = features.get("special_hits", {})
    ocr_extra = auto_ocr_special_hits(path, features) if not special.get("has_text") else {}
    similarity = features.get("similarity", {})
    out: dict[str, Any] = {
        "img2nl_text": result.text,
        "scene_class": features.get("scene", {}).get("scene_class", ""),
        "llm_hint": result.llm_hint,
        "special_hits": _merge_special_hits(special, ocr_extra),
    }
    fp = features.get("fingerprint")
    if isinstance(fp, dict) and fp.get("available"):
        out["fingerprint"] = fp
    if similarity.get("available"):
        out["similarity"] = _json_safe(similarity)
    return _json_safe(out)


def merge_program_metadata(
    metadata: dict[str, Any],
    image_path: str | Path,
    *,
    locale: str = "pl",
    reference_fingerprint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge img2nl slice into program metadata dict."""
    merged = dict(metadata)
    merged.update(
        img2nl_metadata_slice(
            image_path,
            locale=locale,
            reference_fingerprint=reference_fingerprint,
        )
    )
    merged["analyzed_at"] = datetime.now(UTC).isoformat()
    merged["image"] = str(Path(image_path).expanduser())
    return merged


def refresh_program_metadata(
    vql_program: str | Path,
    image_path: str | Path,
    *,
    locale: str = "pl",
) -> dict[str, Any]:
    """Update img2nl metadata in an existing program without rebuilding layers."""
    prog_path = Path(vql_program).expanduser()
    image = Path(image_path).expanduser()
    if not prog_path.is_file():
        return {"ok": False, "error": f"program not found: {prog_path}"}
    if not image.is_file():
        return {"ok": False, "error": f"image not found: {image}"}

    try:
        data = json.loads(prog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}

    ref = load_program_fingerprint(prog_path)
    meta = merge_program_metadata(
        data.get("metadata", {}),
        image,
        locale=locale,
        reference_fingerprint=ref,
    )
    data["metadata"] = meta
    prog_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "program": str(prog_path),
        "image": str(image),
        "unchanged": True,
        "metadata": meta,
        "fingerprint": meta.get("fingerprint", {}),
        "special_hits": meta.get("special_hits", {}),
        "scene_class": meta.get("scene_class", ""),
    }


def metadata_from_diagnose(diag: dict[str, Any]) -> dict[str, Any]:
    """Extract compact img2nl metadata from a diagnose payload."""
    features = diag.get("features", {})
    special = features.get("special_hits", {})
    image_path = diag.get("path", "")
    ocr_extra = (
        auto_ocr_special_hits(image_path, features)
        if image_path and not special.get("has_text")
        else {}
    )
    out: dict[str, Any] = {
        "img2nl_text": diag.get("text", ""),
        "scene_class": features.get("scene", {}).get("scene_class", ""),
        "llm_hint": diag.get("llm_hint", {}),
        "special_hits": _merge_special_hits(special, ocr_extra),
        "diagnose_recommendation": diag.get("recommendation", ""),
        "diagnosed_at": datetime.now(UTC).isoformat(),
        "image": diag.get("path", ""),
    }
    fp = features.get("fingerprint")
    if isinstance(fp, dict) and fp.get("available"):
        out["fingerprint"] = fp
    similarity = features.get("similarity", {})
    if similarity.get("available"):
        out["similarity"] = _json_safe(similarity)
    return _json_safe(out)


def save_diagnose_to_program(
    vql_program: str | Path,
    diag: dict[str, Any],
) -> dict[str, Any]:
    """Persist diagnose/img2nl results into program metadata."""
    prog_path = Path(vql_program).expanduser()
    if not prog_path.is_file():
        return {"ok": False, "error": f"program not found: {prog_path}", "saved": False}
    if not diag.get("ok"):
        return {"ok": False, "error": diag.get("error", "diagnose failed"), "saved": False}

    try:
        data = json.loads(prog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc), "saved": False}

    meta = dict(data.get("metadata", {}))
    meta.update(metadata_from_diagnose(diag))
    data["metadata"] = meta
    prog_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "saved": True,
        "program": str(prog_path),
        "metadata": meta,
        "recommendation": diag.get("recommendation", ""),
    }
