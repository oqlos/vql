"""
VQL public API.

This is the *only* module other packages (notably ``nlp2cmd`` adapters) should
import from. Internal modules — generators, event store, SVG markup helpers,
correction engine internals — stay private to the ``vql`` package.
"""

from __future__ import annotations

from vql.compiler import (
    commands_to_program,
    compile_to_events,
    nl_to_program,
    program_to_commands,
)
from vql.facade import VQLFacade, VQLResult
from vql.library import ColorResolver, ShapeRegistry
from vql.renderers import render_program, render_to_png, render_to_svg
from vql.schema import (
    RenderTarget,
    Scene,
    Style,
    ValidationSpec,
    VQLProgram,
)
from vql.validation import VQLValidationReport, validate_program

__all__ = [
    # Facade
    "VQLFacade",
    "VQLResult",
    # Schema (public IR)
    "VQLProgram",
    "Scene",
    "Style",
    "ValidationSpec",
    "RenderTarget",
    # Compiler
    "nl_to_program",
    "program_to_commands",
    "commands_to_program",
    "compile_to_events",
    # Renderers
    "render_to_svg",
    "render_to_png",
    "render_program",
    # Library (shape/color primitives)
    "ColorResolver",
    "ShapeRegistry",
    # Validation
    "validate_program",
    "VQLValidationReport",
]
