"""Build VQLProgram from UI detections."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from vql.schema.program import Layer, Object, Primitive, Relation, Scene, Style, VQLProgram

from img2vql.metadata import merge_program_metadata


def _role_style(role: str) -> Style:
    styles = {
        "window": Style(color="#4A90D9", fill=False, stroke_width=2.0, opacity=0.9),
        "panel": Style(color="#7B68EE", fill=False, stroke_width=1.5, opacity=0.85),
        "titlebar": Style(color="#FFD700", fill=True, stroke_width=1.0, opacity=0.35),
        "toolbar": Style(color="#20B2AA", fill=False, stroke_width=1.5, opacity=0.8),
        "button": Style(color="#FF6B6B", fill=True, stroke_width=1.0, opacity=0.55),
        "icon_button": Style(color="#FFA500", fill=True, stroke_width=1.0, opacity=0.6),
    }
    return styles.get(role, Style(color="#888888", fill=False, stroke_width=1.0))


def elements_to_vql_program(
    detection: dict[str, Any],
    *,
    image_path: str | Path | None = None,
    include_grid: bool = False,
    grid: int = 12,
) -> VQLProgram:
    """Convert detect_ui_elements() output into a VQL program."""
    if not detection.get("ok"):
        raise ValueError(detection.get("error", "detection failed"))

    w = float(detection.get("width", 1024))
    h = float(detection.get("height", 768))
    path = Path(image_path or detection.get("path", ""))
    elements = detection.get("elements", [])

    ui_objects: list[Object] = []
    for el in elements:
        x0, y0, x1, y1 = el.get("bbox", [0, 0, 0, 0])[:4]
        bw, bh = max(1.0, x1 - x0), max(1.0, y1 - y0)
        cx, cy = x0 + bw / 2, y0 + bh / 2
        role = el.get("role", "panel")
        ui_objects.append(
            Object(
                id=el.get("id", f"ui_{len(ui_objects)}"),
                primitives=[
                    Primitive(
                        shape_type="rectangle",
                        params={"width": bw, "height": bh},
                    )
                ],
                style=_role_style(role),
                center_x=cx,
                center_y=cy,
                metadata={
                    "role": role,
                    "label": el.get("label", ""),
                    "location": el.get("location", ""),
                    "bbox": [x0, y0, x1, y1],
                    "bbox_norm": el.get("bbox_norm", []),
                    "confidence": el.get("confidence", 0),
                    "color": el.get("color", ""),
                    "source": "img2vql_detect",
                },
            )
        )

    layers: list[Layer] = []
    if include_grid and path.is_file():
        from vql.adopt.window import screenshot_to_program

        grid_prog = screenshot_to_program(path, grid=grid)
        for layer in grid_prog.scene.layers:
            layers.append(layer)
    if ui_objects:
        layers.append(Layer(id="ui_elements", objects=ui_objects))

    relations = _build_contains_relations(ui_objects)

    meta_base = {
        "source": "img2vql_detect",
        "element_count": len(ui_objects),
        "by_role": detection.get("by_role", {}),
    }
    metadata = (
        merge_program_metadata(meta_base, path)
        if path.is_file()
        else {**meta_base, "image": str(path) if path else ""}
    )

    return VQLProgram(
        scene=Scene(
            width=w,
            height=h,
            app="desktop",
            url=f"file://{path.resolve()}" if path.is_file() else "",
            layers=layers,
            relations=relations,
        ),
        metadata=metadata,
    )


def _bbox_contains(outer: list[int], inner: list[int]) -> bool:
    ox0, oy0, ox1, oy1 = outer[:4]
    ix0, iy0, ix1, iy1 = inner[:4]
    return ox0 <= ix0 and oy0 <= iy0 and ox1 >= ix1 and oy1 >= iy1


def _build_contains_relations(objects: list[Object]) -> list[Relation]:
    """Infer contains relations from bbox nesting (window > panel > button)."""
    role_rank = {"window": 0, "panel": 1, "titlebar": 1, "toolbar": 2, "button": 3, "icon_button": 3}
    relations: list[Relation] = []
    for parent in objects:
        p_role = parent.metadata.get("role", "")
        p_bbox = parent.metadata.get("bbox", [])
        if not p_bbox:
            continue
        for child in objects:
            if parent.id == child.id:
                continue
            c_role = child.metadata.get("role", "")
            c_bbox = child.metadata.get("bbox", [])
            if not c_bbox:
                continue
            if role_rank.get(p_role, 9) >= role_rank.get(c_role, 9):
                continue
            if _bbox_contains(p_bbox, c_bbox):
                relations.append(
                    Relation(
                        kind="contains",
                        source=parent.id,
                        target=child.id,
                        args={"parent_role": p_role, "child_role": c_role},
                    )
                )
    return relations
