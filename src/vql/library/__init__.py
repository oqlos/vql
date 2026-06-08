"""VQL library — shape templates, registry, color resolution, SVG-path parsing."""

from vql.drawing.colors import ColorResolver
from vql.drawing.shape_registry import ShapeRegistry
from vql.drawing.shapes import PointGroup, ShapeGenerator
from vql.drawing.svg_path_parser import parse_svg_path

__all__ = [
    "ColorResolver",
    "ShapeRegistry",
    "ShapeGenerator",
    "PointGroup",
    "parse_svg_path",
]
