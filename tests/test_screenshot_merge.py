"""Tests for merged region adopt in screenshot_to_program."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PIL")

from vql.adopt.window import screenshot_to_program


def test_screenshot_merge_reduces_object_count(tmp_path: Path) -> None:
    from PIL import Image, ImageDraw

    img = tmp_path / "blocks.png"
    im = Image.new("RGB", (240, 160), (20, 20, 20))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 120, 80], fill=(200, 0, 0))
    d.rectangle([120, 80, 240, 160], fill=(0, 180, 0))
    im.save(img)

    merged = screenshot_to_program(img, grid=12, merge_regions=True)
    flat = screenshot_to_program(img, grid=12, merge_regions=False)

    assert merged.object_count() < flat.object_count()
    assert merged.metadata.get("merge_regions") is True
    assert merged.metadata.get("region_count", 0) >= 2
    assert merged.scene.layers[0].objects[0].id.startswith("region_")
