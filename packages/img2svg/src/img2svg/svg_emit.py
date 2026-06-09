"""Emit SVG from traced regions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from img2svg.trace import trace_image_regions


def regions_to_svg(
    trace: dict[str, Any],
    *,
    stroke: bool = False,
) -> str:
    """Build SVG XML string from trace_image_regions() output."""
    if not trace.get("ok"):
        raise ValueError(trace.get("error", "trace failed"))

    w = trace.get("width", 100)
    h = trace.get("height", 100)
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'  <rect width="{w}" height="{h}" fill="#000000"/>',
    ]
    for i, reg in enumerate(trace.get("regions", [])):
        x, y = reg["x"], reg["y"]
        rw, rh = reg["width"], reg["height"]
        color = reg["color"]
        stroke_attr = f' stroke="#333" stroke-width="0.5"' if stroke else ""
        lines.append(
            f'  <rect id="r{i}" x="{x:.1f}" y="{y:.1f}" '
            f'width="{rw:.1f}" height="{rh:.1f}" fill="{color}"{stroke_attr}/>'
        )
    lines.append("</svg>")
    return "\n".join(lines)


def paths_to_svg(trace: dict[str, Any], *, stroke: str = "#CCCCCC", fill: str = "none") -> str:
    """Build SVG from OpenCV contour paths."""
    if not trace.get("ok"):
        raise ValueError(trace.get("error", "trace failed"))
    w = trace.get("width", 100)
    h = trace.get("height", 100)
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'  <rect width="{w}" height="{h}" fill="#000000"/>',
    ]
    for p in trace.get("paths", []):
        lines.append(
            f'  <path id="{p["id"]}" d="{p["d"]}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
        )
    lines.append("</svg>")
    return "\n".join(lines)


def image_to_svg(
    image_path: str | Path,
    *,
    out_path: str | Path | None = None,
    grid: int = 24,
    method: str = "regions",
) -> dict[str, Any]:
    """
    Convert raster image to SVG file.

    Methods:
      - regions (default): merged color rectangles — fast, good for UI screenshots
      - contours: OpenCV edge contours — requires img2svg[opencv]
    """
    path = Path(image_path).expanduser()
    if method == "contours":
        from img2svg.trace import trace_contours_opencv

        trace = trace_contours_opencv(path)
        if not trace.get("ok"):
            return trace
        svg = paths_to_svg(trace)
    else:
        trace = trace_image_regions(path, grid=grid)
        if not trace.get("ok"):
            return trace
        svg = regions_to_svg(trace)

    out = Path(out_path) if out_path else path.with_suffix(".svg")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")
    return {
        "ok": True,
        "input": str(path),
        "output": str(out),
        "method": trace.get("method", method),
        "region_count": trace.get("region_count", trace.get("path_count", 0)),
        "width": trace.get("width"),
        "height": trace.get("height"),
        "svg_bytes": len(svg.encode("utf-8")),
    }
