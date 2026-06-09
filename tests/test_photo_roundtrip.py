"""Roundtrip tests: image → VQL → rendered image."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for sub in ("src", "packages/img2svg/src"):
    p = ROOT / sub
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

pytest.importorskip("PIL")


def _flat_shapes_image(path: Path) -> Path:
    from PIL import Image, ImageDraw

    im = Image.new("RGB", (200, 150), (240, 235, 220))
    d = ImageDraw.Draw(im)
    d.rectangle([20, 20, 90, 80], fill=(220, 50, 50))
    d.rectangle([110, 40, 180, 120], fill=(50, 100, 200))
    im.save(path)
    return path


def test_nl_drawing_roundtrip(tmp_path: Path) -> None:
    from vql import nl_to_program, render_to_svg

    program = nl_to_program("narysuj czerwone koło", width=200, height=200)
    svg = render_to_svg(program)
    assert svg.startswith("<svg")
    assert program.object_count() >= 1
    assert "circle" in svg or "path" in svg


def test_img2svg_sets_scene_background(tmp_path: Path) -> None:
    from img2svg import image_to_vql
    from vql import VQLProgram

    img = _flat_shapes_image(tmp_path / "flat.png")
    out = tmp_path / "flat.vql.json"
    result = image_to_vql(img, out_program=out, grid=12)
    assert result["ok"]

    program = VQLProgram.from_dict(json.loads(out.read_text(encoding="utf-8")))
    assert program.scene.background == "#F0EBDC"
    assert program.object_count() >= 2


def test_img2svg_vql_render_roundtrip(tmp_path: Path) -> None:
    from img2svg import image_to_vql
    from vql import VQLProgram, render_to_png, render_to_svg

    pytest.importorskip("cairosvg")

    img = _flat_shapes_image(tmp_path / "roundtrip.png")
    out = tmp_path / "roundtrip.vql.json"
    assert image_to_vql(img, out_program=out, grid=12)["ok"]

    program = VQLProgram.from_dict(json.loads(out.read_text(encoding="utf-8")))
    svg = render_to_svg(program)
    assert program.scene.background in svg

    png_out = tmp_path / "roundtrip_recon.png"
    render_to_png(program, str(png_out))
    assert png_out.stat().st_size > 100


def test_vtracer_roundtrip_when_installed(tmp_path: Path) -> None:
    vtracer = pytest.importorskip("vtracer", reason="vtracer optional")
    del vtracer
    pytest.importorskip("cairosvg")
    from img2svg.trace import trace_vtracer
    from img2svg.to_vql import trace_to_vql_program
    from vql import render_to_png

    img = _flat_shapes_image(tmp_path / "vtracer.png")
    trace = trace_vtracer(img)
    assert trace["ok"], trace
    program = trace_to_vql_program(trace, image_path=img)
    png_out = tmp_path / "vtracer_recon.png"
    render_to_png(program, str(png_out))
    assert png_out.stat().st_size > 100
    assert program.object_count() >= 2


def test_metadata_only_program_renders_background_only(tmp_path: Path) -> None:
    pytest.importorskip("cairosvg")
    from vql import VQLProgram, render_to_png
    from vql.schema.program import Layer, Scene

    program = VQLProgram(
        scene=Scene(width=100, height=80, background="#E8E8E8", layers=[Layer(id="empty")]),
        metadata={"exif": {"ISO": 400}, "semantic_description": "test scene"},
    )
    assert program.object_count() == 0
    out = tmp_path / "meta_only.png"
    render_to_png(program, str(out))
    assert out.stat().st_size > 50


def test_trace_contours_graceful_without_opencv(tmp_path: Path) -> None:
    from img2svg.trace import trace_contours_opencv

    img = _flat_shapes_image(tmp_path / "contour.png")
    trace = trace_contours_opencv(img)
    if trace.get("ok"):
        assert trace.get("path_count", 0) >= 0
    else:
        assert "opencv" in trace.get("error", "").lower()
