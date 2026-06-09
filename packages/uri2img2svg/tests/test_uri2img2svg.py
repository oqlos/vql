"""Tests for uri2img2svg."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PIL")

from uri2img2svg import query_uri, uri_for_vectorize
from uri2img2svg.uri import parse_img2svg_uri


def test_parse_uri() -> None:
    p = parse_img2svg_uri("img2svg://vectorize?path=/tmp/x.png&grid=16&method=regions")
    assert p.path == "/tmp/x.png"
    assert p.grid == 16
    assert p.method == "regions"


def test_vectorize(tmp_path: Path) -> None:
    from PIL import Image

    img = tmp_path / "flat.png"
    Image.new("RGB", (80, 60), (40, 80, 120)).save(img)
    uri = uri_for_vectorize(str(img), grid=8)
    result = query_uri(uri)
    assert result.ok
    assert result.data.get("region_count", 0) >= 1


def test_svg_uri(tmp_path: Path) -> None:
    from PIL import Image

    img = tmp_path / "a.png"
    out = tmp_path / "a.svg"
    Image.new("RGB", (64, 64), (100, 100, 100)).save(img)
    result = query_uri(f"img2svg://svg?path={img}&out={out}")
    assert result.ok
    assert out.is_file()
