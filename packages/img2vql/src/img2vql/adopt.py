"""High-level: detect UI → describe → VQL program."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from img2vql.describe_ui import describe_ui_layout
from img2vql.detect import detect_ui_elements
from img2vql.program import elements_to_vql_program


def adopt_screenshot(
    image_path: str | Path,
    *,
    out_program: str | Path = "ui.vql.json",
    locale: str = "pl",
    include_grid: bool = False,
    grid: int = 12,
    detect_buttons: bool = True,
) -> dict[str, Any]:
    """
    Detect UI elements on a screenshot and write a VQL program.

    Layers:
      - ui_elements: windows, panels, buttons, titlebar, toolbar
      - screen_regions (optional): coarse color grid from vql.adopt.window
    """
    detection = detect_ui_elements(
        image_path,
        detect_buttons=detect_buttons,
    )
    if not detection.get("ok"):
        return detection

    program = elements_to_vql_program(
        detection,
        image_path=image_path,
        include_grid=include_grid,
        grid=grid,
    )
    out = Path(out_program).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(program.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    description = describe_ui_layout(detection, locale=locale)
    meta = program.metadata
    return {
        "ok": True,
        "path": str(image_path),
        "program": str(out),
        "element_count": detection.get("element_count", 0),
        "by_role": detection.get("by_role", {}),
        "description": description,
        "elements": detection.get("elements", []),
        "object_count": program.object_count(),
        "scene": {"width": program.scene.width, "height": program.scene.height},
        "fingerprint": meta.get("fingerprint", {}),
        "special_hits": meta.get("special_hits", {}),
        "scene_class": meta.get("scene_class", ""),
        "llm_hint": meta.get("llm_hint", {}),
    }
