"""Diagnose whether a capture is worth LLM / VQL adopt."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _normalize_locale(locale: str) -> str:
    try:
        from img2nl.i18n import normalize_locale

        return normalize_locale(locale)
    except ImportError:
        loc = (locale or "pl").strip().lower()
        return "en" if loc.startswith("en") else "pl"


from img2vql.fingerprint import load_program_fingerprint
from img2vql.metadata import _json_safe, save_diagnose_to_program


def diagnose_image(
    image_path: str | Path,
    *,
    locale: str = "pl",
    translate_mode: str = "auto",
    reference_fingerprint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run img2nl heuristics on an image file."""
    from img2nl import analyze_image

    loc = _normalize_locale(locale)
    result = analyze_image(
        image_path,
        skip_thumbnail=False,
        locale=loc,
        translate_mode=translate_mode,  # type: ignore[arg-type]
        reference_fingerprint=reference_fingerprint,
    )
    if not result.ok:
        return {"ok": False, "path": str(image_path), "error": result.error, "locale": loc}
    return {
        "ok": True,
        "path": result.path,
        "text": result.text,
        "thumbnail": result.thumbnail,
        "features": result.features,
        "llm_hint": result.llm_hint,
        "width": result.width,
        "height": result.height,
        "locale": loc,
        "source": "img2vql",
    }


def diagnose_for_vql(
    image_path: str | Path,
    *,
    vql_program: str | Path | None = None,
    locale: str = "pl",
    translate_mode: str = "auto",
    save_to_program: bool = False,
) -> dict[str, Any]:
    """
    Combine img2nl diagnose with optional existing VQL program summary.

    Helps decide: grid-only adopt (vql window) vs send thumbnail to LLM.
    """
    ref_fp = load_program_fingerprint(vql_program)
    diag = diagnose_image(
        image_path,
        locale=locale,
        translate_mode=translate_mode,
        reference_fingerprint=ref_fp,
    )
    if not diag.get("ok"):
        return diag

    out: dict[str, Any] = {
        **diag,
        "vql_program": str(vql_program) if vql_program else "",
        "recommendation": _recommendation(diag),
    }

    if vql_program and Path(vql_program).is_file():
        try:
            import json

            from vql.schema.program import VQLProgram

            data = json.loads(Path(vql_program).read_text(encoding="utf-8"))
            program = VQLProgram.from_dict(data)
            out["vql_object_count"] = program.object_count()
            out["vql_dominant_colors"] = program.metadata.get("dominant_colors", [])
            out["vql_fingerprint"] = program.metadata.get("fingerprint", {})
        except Exception as exc:
            out["vql_error"] = str(exc)

    similarity = diag.get("features", {}).get("similarity", {})
    if similarity.get("available"):
        out["similarity"] = similarity

    if save_to_program and vql_program:
        saved = save_diagnose_to_program(vql_program, out)
        out["program_save"] = saved
        if saved.get("ok"):
            out["saved_to_program"] = True

    return _json_safe(out)


def _recommendation(diag: dict[str, Any]) -> str:
    features = diag.get("features", {})
    similarity = features.get("similarity", {})
    scene = features.get("scene", {})
    if similarity.get("match") or scene.get("scene_class") == "unchanged_screen":
        return "skip_unchanged_screen"
    hint = diag.get("llm_hint", {})
    colors = features.get("colors", {})
    if hint.get("send_to_llm"):
        return "send_thumbnail_to_llm"
    if colors.get("is_monochrome") and colors.get("is_mostly_dark"):
        return "skip_llm_blank_capture"
    return "use_vql_grid_only"
