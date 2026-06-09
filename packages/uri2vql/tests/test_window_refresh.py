"""Tests for window/refresh URI and diagnose save."""

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

from img2vql import diagnose_for_vql, save_diagnose_to_program
from uri2vql import query_window, uri_for_window_refresh


def _solid(path: Path, color: tuple[int, int, int], size: tuple[int, int] = (120, 80)) -> Path:
    from PIL import Image

    Image.new("RGB", size, color=color).save(path)
    return path


@pytest.mark.skipif(not HAS_IMAGEHASH, reason="imagehash not installed")
def test_diagnose_save_to_program(tmp_path: Path) -> None:
    from vql.adopt.window import screenshot_to_program

    img = _solid(tmp_path / "screen.png", (40, 80, 120))
    program_path = tmp_path / "app.vql.json"
    program = screenshot_to_program(img, grid=8)
    program_path.write_text(json.dumps(program.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    diag = diagnose_for_vql(img, vql_program=program_path, save_to_program=True)
    assert diag["ok"]
    assert diag.get("saved_to_program") is True

    saved = json.loads(program_path.read_text(encoding="utf-8"))
    meta = saved["metadata"]
    assert meta.get("diagnose_recommendation")
    assert meta.get("diagnosed_at")
    assert meta.get("scene_class")


@pytest.mark.skipif(not HAS_IMAGEHASH, reason="imagehash not installed")
def test_save_diagnose_to_program_helper(tmp_path: Path) -> None:
    img = _solid(tmp_path / "screen.png", (10, 30, 50))
    program_path = tmp_path / "base.vql.json"
    program_path.write_text(
        json.dumps({"metadata": {"source": "test"}, "scene": {"width": 120, "height": 80, "layers": []}}),
        encoding="utf-8",
    )
    diag = diagnose_for_vql(img)
    assert diag["ok"]
    result = save_diagnose_to_program(program_path, diag)
    assert result["ok"]
    assert result["saved"] is True


@pytest.mark.skipif(not HAS_IMAGEHASH, reason="imagehash not installed")
def test_window_refresh_uri(tmp_path: Path) -> None:
    from vql.adopt.window import analyze_screenshot

    img = _solid(tmp_path / "screen.png", (40, 80, 120))
    program_path = tmp_path / "app.vql.json"
    analyze_screenshot(img, out_program=program_path, skip_if_unchanged=False)

    uri = uri_for_window_refresh(file=str(program_path), image=str(img), locale="pl")
    result = query_window(uri)
    assert result.ok
    assert result.data.get("scene_class")
    assert result.data.get("fingerprint", {}).get("available")
