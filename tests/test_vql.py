"""Unit tests for the VQL (Visual Query Language) IR package."""

from __future__ import annotations

import pytest

from vql import (
    RenderTarget,
    Scene,
    Style,
    VQLFacade,
    VQLProgram,
    commands_to_program,
    compile_to_events,
    nl_to_program,
    program_to_commands,
    render_to_svg,
    validate_program,
)
from vql.schema.program import Layer, Object, Primitive


# ── Schema ───────────────────────────────────────────────────────────────────

def test_empty_program_is_structurally_valid():
    program = VQLProgram(scene=Scene(width=800, height=600))
    assert program.is_valid()
    assert program.validate() == []


def test_invalid_scene_dimensions_fail():
    program = VQLProgram(scene=Scene(width=0, height=-1))
    errors = program.validate()
    assert any("width" in e for e in errors)
    assert any("height" in e for e in errors)


def test_program_roundtrip_to_dict():
    program = VQLProgram(
        scene=Scene(
            width=640,
            height=480,
            layers=[
                Layer(
                    objects=[
                        Object(
                            id="o0",
                            primitives=[Primitive(shape_type="star", params={"points_count": 5})],
                            style=Style(color="#FF0000", fill=True),
                            center_x=320,
                            center_y=240,
                        )
                    ]
                )
            ],
        ),
        render_target=RenderTarget.SVG,
    )
    data = program.to_dict()
    restored = VQLProgram.from_dict(data)
    assert restored.to_dict() == data
    assert restored.object_count() == 1


# ── Compiler round-trip ────────────────────────────────────────────────────────

def test_commands_program_roundtrip_preserves_shapes_and_colors():
    program = nl_to_program("narysuj czerwone koło i niebieski trójkąt", width=800, height=600)
    shapes = [obj.primitives[0].shape_type for obj in program.scene.iter_objects()]
    colors = [obj.style.color for obj in program.scene.iter_objects()]
    assert "circle" in shapes
    assert "triangle" in shapes
    assert "#FF0000" in colors
    assert "#0000FF" in colors


def test_program_to_commands_starts_with_init_canvas():
    program = nl_to_program("narysuj koło", width=400, height=300)
    commands = program_to_commands(program)
    from vql.drawing.commands import InitCanvas

    assert isinstance(commands[0], InitCanvas)
    assert commands[0].width == 400
    assert commands[0].height == 300


def test_commands_to_program_is_inverse_of_program_to_commands():
    original = nl_to_program("narysuj zielony kwadrat", width=500, height=500)
    commands = program_to_commands(original)
    rebuilt = commands_to_program(commands, width=500, height=500)
    assert rebuilt.object_count() == original.object_count()
    assert [o.primitives[0].shape_type for o in rebuilt.scene.iter_objects()] == [
        o.primitives[0].shape_type for o in original.scene.iter_objects()
    ]


# ── Events / geometry parity ────────────────────────────────────────────────────

def test_compile_to_events_produces_shape_drawn():
    program = nl_to_program("narysuj koło", width=400, height=400)
    events = compile_to_events(program)
    assert len(events) >= 1
    assert events[0].shape_type == "circle"
    assert events[0].points  # geometry was generated


# ── Rendering ────────────────────────────────────────────────────────────────────

def test_render_to_svg_returns_markup():
    program = nl_to_program("narysuj czerwoną gwiazdę", width=400, height=400)
    svg = render_to_svg(program)
    assert svg.startswith("<svg")
    assert "path" in svg


def test_render_to_png_without_cairosvg_raises_clear_error(tmp_path):
    """If the 'vql' extra is missing, PNG export must fail with a helpful message."""
    try:
        import cairosvg  # noqa: F401
        has_cairo = True
    except ImportError:
        has_cairo = False

    from vql import render_to_png

    program = nl_to_program("narysuj koło", width=200, height=200)
    out = tmp_path / "out.png"

    if has_cairo:
        path = render_to_png(program, str(out))
        assert out.exists() and out.stat().st_size > 0
        # PNG magic bytes
        assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
        assert path == str(out)
    else:
        with pytest.raises(RuntimeError, match="vql"):
            render_to_png(program, str(out))


# ── Validation ─────────────────────────────────────────────────────────────────

def test_validate_program_passes_with_matching_spec():
    program = nl_to_program("narysuj czerwone koło", width=400, height=400)
    report = validate_program(program)
    assert report.passed
    assert "circle" in report.matched_shapes


def test_validate_program_reports_missing_shape():
    from vql.schema.program import ValidationSpec

    program = nl_to_program("narysuj koło", width=400, height=400)
    program.validation = ValidationSpec(expected_shapes=["dragon"])
    report = validate_program(program)
    assert not report.passed
    assert any("dragon" in issue for issue in report.issues)


# ── Facade ───────────────────────────────────────────────────────────────────────

def test_facade_run_full_pipeline():
    result = VQLFacade().run("narysuj niebieski kwadrat", width=400, height=400)
    assert isinstance(result.program, VQLProgram)
    assert result.report.passed
    assert result.svg and result.svg.startswith("<svg")


def test_facade_run_without_render_skips_svg():
    result = VQLFacade().run("narysuj koło", render=False)
    assert result.svg is None
    assert result.program.object_count() >= 1


# ── Step 6: NLDrawingParser VQL awareness ────────────────────────────────────────

def test_nl_parser_to_vql_returns_program():
    program = nl_to_program("narysuj czerwone koło", width=400, height=400)
    assert isinstance(program, VQLProgram)
    assert program.object_count() >= 1
    assert program.scene.iter_objects().__next__().primitives[0].shape_type == "circle"


def test_nl_parser_parse_still_returns_commands():
    """Backward-compat: parse() must keep returning DrawCommands."""
    from vql.drawing.commands import DrawCommand
    from vql.drawing.nl_parser import NLDrawingParser

    commands = NLDrawingParser().parse("narysuj koło")
    assert all(isinstance(c, DrawCommand) for c in commands)


# ── Library namespace ─────────────────────────────────────────────────────────────

def test_vql_library_exposes_primitives():
    from vql.library import (
        ColorResolver,
        ShapeRegistry,
        parse_svg_path,
    )

    assert ColorResolver().resolve("czerwony") == "#FF0000"
    assert "circle" in ShapeRegistry.available()
    groups = parse_svg_path("M 0 0 L 10 0 L 10 10 Z")
    assert groups and len(groups[0]) >= 2


# ── Playwright VQL renderer ───────────────────────────────────────────────────────

def test_playwright_vql_renderer_render_delegates_to_events():
    import asyncio

    from vql.renderers.playwright import PlaywrightVQLRenderer

    program = nl_to_program("narysuj koło", width=400, height=400)

    drawn: list = []

    renderer = PlaywrightVQLRenderer(page=object())

    async def fake_init_canvas(width, height, url="", app="generic"):
        return {"width": width, "height": height}

    async def fake_draw_shape(event):
        drawn.append(event)

    renderer.init_canvas = fake_init_canvas  # type: ignore[assignment]
    renderer.draw_shape = fake_draw_shape  # type: ignore[assignment]

    asyncio.run(renderer.render(program))

    assert len(drawn) >= 1
    assert drawn[0].shape_type == "circle"


def test_playwright_vql_renderer_is_renderer_subclass():
    from vql.drawing.renderers.base import Renderer
    from vql.renderers.playwright import PlaywrightVQLRenderer

    assert issubclass(PlaywrightVQLRenderer, Renderer)
    assert hasattr(PlaywrightVQLRenderer, "render")
