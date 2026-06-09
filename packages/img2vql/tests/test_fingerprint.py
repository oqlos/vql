"""Tests for img2vql fingerprint integration."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("PIL")
pytest.importorskip("img2nl")

try:
    import imagehash as _imagehash

    HAS_IMAGEHASH = True
except ImportError:
    HAS_IMAGEHASH = False

from img2vql import compare_with_program, diagnose_for_vql, fingerprint_for_image, load_program_fingerprint
from vql.adopt.window import screenshot_to_program


def _solid(path: Path, color: tuple[int, int, int], size: tuple[int, int] = (120, 80)) -> Path:
    from PIL import Image

    Image.new("RGB", size, color=color).save(path)
    return path


@pytest.mark.skipif(not HAS_IMAGEHASH, reason="imagehash not installed")
def test_screenshot_to_program_stores_fingerprint(tmp_path: Path) -> None:
    img = _solid(tmp_path / "screen.png", (40, 80, 120))
    program = screenshot_to_program(img, grid=8)
    fp = program.metadata.get("fingerprint", {})
    assert fp.get("available") is True
    assert fp.get("phash")


@pytest.mark.skipif(not HAS_IMAGEHASH, reason="imagehash not installed")
def test_diagnose_uses_program_fingerprint(tmp_path: Path) -> None:
    img = _solid(tmp_path / "screen.png", (40, 80, 120))
    program_path = tmp_path / "app.vql.json"
    program = screenshot_to_program(img, grid=8)
    program_path.write_text(json.dumps(program.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    diag = diagnose_for_vql(img, vql_program=program_path)
    assert diag["ok"]
    assert diag["recommendation"] == "skip_unchanged_screen"
    assert diag.get("similarity", {}).get("match")


@pytest.mark.skipif(not HAS_IMAGEHASH, reason="imagehash not installed")
def test_analyze_skips_adopt_when_unchanged(tmp_path: Path) -> None:
    from vql.adopt.window import analyze_screenshot

    img = _solid(tmp_path / "screen.png", (40, 80, 120))
    program_path = tmp_path / "app.vql.json"
    first = analyze_screenshot(img, out_program=program_path, skip_if_unchanged=False)
    assert first["ok"]
    assert not first.get("skipped_adopt")

    second = analyze_screenshot(img, out_program=program_path, skip_if_unchanged=True)
    assert second["ok"]
    assert second.get("skipped_adopt") is True
    assert second.get("recommendation") == "skip_unchanged_screen"
    assert second.get("fingerprint", {}).get("available")


@pytest.mark.skipif(not HAS_IMAGEHASH, reason="imagehash not installed")
def test_screenshot_stores_special_hits_metadata(tmp_path: Path) -> None:
    img = _solid(tmp_path / "screen.png", (40, 80, 120))
    program = screenshot_to_program(img, grid=8)
    assert "special_hits" in program.metadata
    assert "scene_class" in program.metadata


@pytest.mark.skipif(not HAS_IMAGEHASH, reason="imagehash not installed")
def test_compare_with_program(tmp_path: Path) -> None:
    img = _solid(tmp_path / "a.png", (10, 20, 30))
    program_path = tmp_path / "base.vql.json"
    fp = fingerprint_for_image(img)
    assert fp is not None
    program_path.write_text(
        json.dumps({"metadata": {"fingerprint": fp}, "scene": {"width": 120, "height": 80, "layers": []}}),
        encoding="utf-8",
    )
    loaded = load_program_fingerprint(program_path)
    assert loaded is not None
    result = compare_with_program(img, program_path)
    assert result["ok"]
    assert result["match"]
