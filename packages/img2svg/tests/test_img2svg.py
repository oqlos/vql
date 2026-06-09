"""Tests for img2svg."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PIL")

from img2svg import image_to_svg, image_to_vql, trace_image_regions


def test_trace_regions(tmp_path: Path) -> None:
    from PIL import Image, ImageDraw

    img = tmp_path / "blocks.png"
    im = Image.new("RGB", (120, 80), (20, 20, 20))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 60, 40], fill=(200, 0, 0))
    d.rectangle([60, 40, 120, 80], fill=(0, 180, 0))
    im.save(img)

    trace = trace_image_regions(img, grid=12)
    assert trace["ok"]
    assert trace["region_count"] >= 2


def test_image_to_svg(tmp_path: Path) -> None:
    from PIL import Image

    img = tmp_path / "flat.png"
    Image.new("RGB", (64, 64), (100, 120, 140)).save(img)
    out = tmp_path / "flat.svg"
    result = image_to_svg(img, out_path=out, grid=8)
    assert result["ok"]
    assert out.is_file()
    text = out.read_text(encoding="utf-8")
    assert "<svg" in text
    assert "<rect" in text


def test_image_to_vql(tmp_path: Path) -> None:
    from PIL import Image, ImageDraw

    img = tmp_path / "ui.png"
    im = Image.new("RGB", (100, 60), (30, 30, 30))
    ImageDraw.Draw(im).rectangle([10, 10, 50, 40], fill=(255, 0, 0))
    im.save(img)
    out = tmp_path / "ui.vql.json"
    result = image_to_vql(img, out_program=out, grid=10)
    assert result["ok"]
    assert out.is_file()
    assert result["object_count"] >= 1
