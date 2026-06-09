"""Tests for img2vql diagnose."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PIL")
pytest.importorskip("img2nl")

from img2vql import diagnose_for_vql


def test_diagnose_blank_vs_rich(tmp_path: Path) -> None:
    from PIL import Image, ImageDraw

    black = tmp_path / "black.png"
    Image.new("RGB", (100, 100), (0, 0, 0)).save(black)
    rich = tmp_path / "rich.png"
    im = Image.new("RGB", (200, 150), (40, 40, 50))
    d = ImageDraw.Draw(im)
    d.rectangle([10, 10, 90, 70], fill=(200, 0, 0))
    im.save(rich)

    d_black = diagnose_for_vql(black)
    d_rich = diagnose_for_vql(rich)
    assert d_black["ok"] and d_rich["ok"]
    assert d_black["recommendation"] == "skip_llm_blank_capture"
    assert d_rich["recommendation"] in {"send_thumbnail_to_llm", "use_vql_grid_only"}
