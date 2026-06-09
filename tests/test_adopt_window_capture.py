"""Tests for screenshot capture helpers."""

from __future__ import annotations

from pathlib import Path

from vql.adopt.window import _image_is_blank, image_stats


def test_image_is_blank_detects_black(tmp_path: Path) -> None:
    from PIL import Image

    path = tmp_path / "black.png"
    Image.new("RGB", (120, 80), color=(0, 0, 0)).save(path)
    assert _image_is_blank(path) is True


def test_image_is_blank_accepts_colored(tmp_path: Path) -> None:
    from PIL import Image

    path = tmp_path / "color.png"
    im = Image.new("RGB", (120, 80), color=(32, 64, 128))
    im.putpixel((10, 10), (200, 100, 50))
    im.save(path)
    assert _image_is_blank(path) is False


def test_image_stats_reports_blank(tmp_path: Path) -> None:
    from PIL import Image

    path = tmp_path / "black.png"
    Image.new("RGB", (64, 48), color=(0, 0, 0)).save(path)
    stats = image_stats(path)
    assert stats["ok"] is True
    assert stats["is_blank"] is True
    assert stats["brightness_max"] == 0
