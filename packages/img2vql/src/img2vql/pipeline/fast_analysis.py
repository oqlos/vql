"""Fast preliminary analysis levels (img2nl + img2vql heuristics)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

AdoptMethod = Literal["auto", "grid", "detect", "imgl"]


def level0_image_stats(image_path: str | Path) -> dict[str, Any]:
    from vql.adopt.window import image_stats

    return {"level": "L0_stats", **image_stats(image_path)}


def level1_img2nl_fast(
    image_path: str | Path,
    *,
    locale: str = "pl",
    reference_fingerprint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """img2nl fast pass: features, scene_class, fingerprint, llm_hint."""
    from img2nl import analyze_image
    from img2vql.metadata import img2nl_metadata_slice

    result = analyze_image(
        image_path,
        skip_thumbnail=False,
        locale=locale,
        speed="fast",
        reference_fingerprint=reference_fingerprint,
    )
    if not result.ok:
        return {"level": "L1_img2nl", "ok": False, "error": result.error, "path": str(image_path)}

    meta_slice = img2nl_metadata_slice(image_path, locale=locale)
    return {
        "level": "L1_img2nl",
        "ok": True,
        "path": result.path,
        "text": result.text,
        "width": result.width,
        "height": result.height,
        "locale": result.locale,
        "llm_hint": result.llm_hint,
        "metadata": meta_slice,
        "features": {
            "scene": result.features.get("scene", {}),
            "colors": result.features.get("colors", {}),
            "special_hits": result.features.get("special_hits", {}),
            "fingerprint": result.features.get("fingerprint", {}),
            "similarity": result.features.get("similarity", {}),
        },
        "thumbnail": result.thumbnail,
    }


def level2_ui_detect(image_path: str | Path, *, detect_buttons: bool = True) -> dict[str, Any]:
    from img2vql.detect import detect_ui_elements

    payload = detect_ui_elements(image_path, detect_buttons=detect_buttons)
    payload["level"] = "L2_detect"
    return payload


def level3_adopt_program(
    image_path: str | Path,
    *,
    method: AdoptMethod = "auto",
    locale: str = "pl",
    grid: int = 12,
    include_grid: bool = False,
) -> dict[str, Any]:
    """Build base VQL program (grid / detect / imgl / auto via img2nl bridge)."""
    path = Path(image_path)
    if method == "grid":
        from vql.adopt.window import screenshot_to_program

        program = screenshot_to_program(path, grid=grid)
        return {
            "level": "L3_adopt",
            "ok": True,
            "method": "grid",
            "program": program.to_dict(),
            "object_count": program.object_count(),
        }

    if method == "detect":
        from img2vql.adopt import adopt_screenshot

        tmp = path.with_suffix(".pipeline.vql.json")
        payload = adopt_screenshot(path, out_program=tmp, locale=locale, include_grid=include_grid, grid=grid)
        if not payload.get("ok"):
            payload["level"] = "L3_adopt"
            return payload
        import json

        program = json.loads(tmp.read_text(encoding="utf-8"))
        payload["level"] = "L3_adopt"
        payload["method"] = "detect"
        payload["program"] = program
        return payload

    try:
        from img2nl.vql_bridge import adopt_vql_program

        out = path.with_suffix(".pipeline.vql.json")
        pick: AdoptMethod = method if method != "auto" else "auto"
        payload = adopt_vql_program(
            path,
            out,
            method=pick,  # type: ignore[arg-type]
            locale=locale,
            include_grid=include_grid,
            grid=grid,
        )
        if payload.get("ok"):
            import json

            program = json.loads(Path(payload["program"]).read_text(encoding="utf-8"))
            payload["level"] = "L3_adopt"
            payload["program"] = program
            return payload
    except ImportError:
        pass

    from vql.adopt.window import screenshot_to_program

    program = screenshot_to_program(path, grid=grid)
    return {
        "level": "L3_adopt",
        "ok": True,
        "method": "grid_fallback",
        "program": program.to_dict(),
        "object_count": program.object_count(),
    }


def level4_diagnose(
    image_path: str | Path,
    *,
    vql_program: str | Path | None = None,
    locale: str = "pl",
) -> dict[str, Any]:
    from img2vql.diagnose import diagnose_for_vql

    payload = diagnose_for_vql(image_path, vql_program=vql_program, locale=locale)
    payload["level"] = "L4_diagnose"
    return payload
