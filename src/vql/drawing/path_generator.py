"""SVG path primitive — renders ``d`` attribute via :func:`parse_svg_path`."""

from __future__ import annotations

from typing import Any

from vql.drawing.shape_generator import ShapeGenerator
from vql.drawing.svg_path_parser import parse_svg_path

PointGroup = list[tuple[float, float]]


class PathGenerator(ShapeGenerator):
    name = "path"

    def generate(self, cx: float, cy: float, size: float, **params: Any) -> list[PointGroup]:
        d = params.get("d", "")
        if not d:
            return []
        tx = float(params.get("tx", 0.0))
        ty = float(params.get("ty", 0.0))
        groups = parse_svg_path(str(d), center=False)
        if not groups:
            return []
        return [[(x + tx, y + ty) for x, y in group] for group in groups]
