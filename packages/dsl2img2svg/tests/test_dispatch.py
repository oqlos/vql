"""Tests for dsl2img2svg dispatch."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PIL")

from dsl2img2svg import dispatch


def test_vectorize(tmp_path: Path) -> None:
    from PIL import Image

    img = tmp_path / "x.png"
    out = tmp_path / "x.svg"
    Image.new("RGB", (48, 48), (90, 90, 90)).save(img)
    result = dispatch(f"VECTORIZE PATH {img} OUT {out} GRID 8")
    assert result.ok
    assert out.is_file()


def test_query_uri(tmp_path: Path) -> None:
    from PIL import Image

    img = tmp_path / "y.png"
    Image.new("RGB", (32, 32), (10, 20, 30)).save(img)
    result = dispatch(f"QUERY img2svg://vectorize?path={img}&grid=8")
    assert result.ok
