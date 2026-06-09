"""Capture desktop/window screenshots and adopt them as VQL programs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from vql.adopt.capture_diagnose import capture_diagnose
from vql.adopt.capture_image import image_is_blank, image_stats
from vql.adopt.capture_policy import capture_permission_hint
from vql.adopt.capture_screen import capture_screen
from vql.adopt.capture_types import CaptureAttempt, CaptureError, CaptureInfo, require_pillow
from vql.adopt.program_grid import screenshot_to_program

# Backward-compatible private aliases.
_image_is_blank = image_is_blank
_capture_permission_hint = capture_permission_hint
_require_pillow = require_pillow

__all__ = [
    "CaptureAttempt",
    "CaptureError",
    "CaptureInfo",
    "analyze_screenshot",
    "capture_diagnose",
    "capture_screen",
    "image_stats",
    "screenshot_to_program",
]


def analyze_screenshot(
    image_path: str | Path | None = None,
    *,
    out_program: str | Path = "app.vql.json",
    monitor: int = 1,
    grid: int = 12,
    interactive: bool | None = None,
    skip_if_unchanged: bool = True,
    locale: str = "pl",
) -> dict[str, Any]:
    """Capture (if needed) + adopt screenshot → VQL JSON program."""
    capture: CaptureInfo | None = None
    if image_path is not None:
        path = Path(image_path).expanduser()
        if not path.is_file():
            raise FileNotFoundError(
                f"image not found: {path}. "
                "On GNOME/Wayland grim often fails; try: "
                "uri2vql capture-screen --interactive "
                "or gnome-screenshot and use ~/Pictures/Screenshots/*.png"
            )
        image_path = path
    else:
        capture = capture_screen(monitor=monitor, interactive=interactive)
        image_path = capture.path

    stats = image_stats(image_path)
    if stats.get("is_blank"):
        return {
            "ok": False,
            "program": str(out_program),
            "image": str(image_path),
            "error": "screenshot is blank (all black) — GNOME blocked capture without permission",
            "image_stats": stats,
            "hint": capture_permission_hint(),
            "recommendation": "skip_llm_blank_capture",
        }

    out = Path(out_program).expanduser()
    if skip_if_unchanged and out.is_file():
        try:
            from img2vql.fingerprint import compare_with_program
            from img2vql.metadata import refresh_program_metadata

            cmp = compare_with_program(image_path, out)
            if cmp.get("ok") and cmp.get("match"):
                refreshed = refresh_program_metadata(out, image_path, locale=locale)
                if refreshed.get("ok"):
                    from vql.schema.program import VQLProgram

                    data = json.loads(out.read_text(encoding="utf-8"))
                    program = VQLProgram.from_dict(data)
                    meta = refreshed.get("metadata", {})
                    return {
                        "ok": True,
                        "program": str(out),
                        "image": str(image_path),
                        "unchanged": True,
                        "skipped_adopt": True,
                        "object_count": program.object_count(),
                        "dominant_colors": meta.get("dominant_colors", []),
                        "fingerprint": meta.get("fingerprint", {}),
                        "special_hits": meta.get("special_hits", {}),
                        "scene_class": meta.get("scene_class", ""),
                        "similarity": meta.get("similarity", cmp.get("similarity", {})),
                        "scene": {"width": program.scene.width, "height": program.scene.height},
                        "window_title": capture.window_title if capture else "",
                        "image_stats": stats,
                        "recommendation": "skip_unchanged_screen",
                    }
        except ImportError:
            pass

    program = screenshot_to_program(image_path, grid=grid, capture=capture)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(program.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    payload: dict[str, Any] = {
        "ok": True,
        "program": str(out),
        "image": str(image_path),
        "object_count": program.object_count(),
        "dominant_colors": program.metadata.get("dominant_colors", []),
        "fingerprint": program.metadata.get("fingerprint", {}),
        "special_hits": program.metadata.get("special_hits", {}),
        "scene_class": program.metadata.get("scene_class", ""),
        "similarity": program.metadata.get("similarity", {}),
        "scene": {"width": program.scene.width, "height": program.scene.height},
        "window_title": capture.window_title if capture else "",
        "image_stats": stats,
    }
    if stats.get("unique_colors_sampled", 0) <= 2:
        payload["warning"] = "very low color diversity — verify capture is not a failed Wayland grab"
    return payload
