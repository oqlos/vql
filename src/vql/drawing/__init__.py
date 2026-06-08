"""Drawing primitives for VQL — shapes, colors, commands, renderers."""

from vql.drawing.colors import ColorResolver
from vql.drawing.nl_parser import NLDrawingParser
from vql.drawing.shape_registry import ShapeRegistry
from vql.drawing.shapes import PointGroup, ShapeGenerator
from vql.drawing.svg_path_parser import parse_svg_path

__all__ = [
    "ColorResolver",
    "NLDrawingParser",
    "ShapeRegistry",
    "ShapeGenerator",
    "PointGroup",
    "parse_svg_path",
]
