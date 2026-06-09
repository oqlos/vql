"""Convert traced image regions to VQLProgram."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from img2svg.trace import trace_contours_opencv, trace_image_regions
from vql.schema.program import Layer, Object, Primitive, Scene, Style, VQLProgram


def trace_to_vql_program(trace: dict[str, Any], *, image_path: str | Path = "") -> VQLProgram:
    """Build VQL program from trace_image_regions() or trace_contours_opencv()."""
    if not trace.get("ok"):
        raise ValueError(trace.get("error", "trace failed"))

    w = float(trace.get("width", 1024))
    h = float(trace.get("height", 768))
    path = Path(image_path or trace.get("path", ""))
    objects: list[Object] = []

    if trace.get("method") == "opencv_contour":
        for p in trace.get("paths", []):
            cx = cy = 0.0
            objects.append(
                Object(
                    id=p.get("id", f"path_{len(objects)}"),
                    primitives=[Primitive(shape_type="path", params={"d": p["d"]})],
                    style=Style(color="#CCCCCC", fill=False, stroke_width=1.0),
                    center_x=cx,
                    center_y=cy,
                    metadata={"source": "img2svg_contour", "point_count": p.get("point_count", 0)},
                )
            )
    else:
        for i, reg in enumerate(trace.get("regions", [])):
            rw, rh = reg["width"], reg["height"]
            cx = reg["x"] + rw / 2
            cy = reg["y"] + rh / 2
            objects.append(
                Object(
                    id=f"region_{i:03d}",
                    primitives=[
                        Primitive(shape_type="rectangle", params={"width": rw, "height": rh})
                    ],
                    style=Style(color=reg["color"], fill=True, stroke_width=0.0),
                    center_x=cx,
                    center_y=cy,
                    metadata={"source": "img2svg_regions", "grid": reg.get("grid", [])},
                )
            )

    return VQLProgram(
        scene=Scene(
            width=w,
            height=h,
            app="raster_trace",
            url=f"file://{path.resolve()}" if path.is_file() else "",
            layers=[Layer(id="traced_regions", objects=objects)],
        ),
        metadata={
            "source": "img2svg",
            "method": trace.get("method", "color_grid_merge"),
            "image": str(path) if path else "",
            "region_count": len(objects),
            "analyzed_at": datetime.now(UTC).isoformat(),
        },
    )


def image_to_vql(
    image_path: str | Path,
    *,
    out_program: str | Path | None = None,
    grid: int = 24,
    method: str = "regions",
) -> dict[str, Any]:
    """Trace image and write VQL JSON program."""
    path = Path(image_path).expanduser()
    if method == "contours":
        trace = trace_contours_opencv(path)
    else:
        trace = trace_image_regions(path, grid=grid)
    if not trace.get("ok"):
        return trace

    program = trace_to_vql_program(trace, image_path=path)
    out = Path(out_program) if out_program else path.with_suffix(".vql.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(program.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "input": str(path),
        "program": str(out),
        "method": trace.get("method"),
        "object_count": program.object_count(),
        "scene": {"width": program.scene.width, "height": program.scene.height},
    }
