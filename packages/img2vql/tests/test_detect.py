"""Tests for img2vql UI detection."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PIL")
pytest.importorskip("img2nl")

from img2vql import adopt_screenshot, describe_ui_layout, detect_ui_elements


def _make_ui_fixture(path: Path) -> None:
    from PIL import Image, ImageDraw

    im = Image.new("RGB", (400, 300), (30, 32, 36))
    d = ImageDraw.Draw(im)
    # titlebar
    d.rectangle([0, 0, 400, 28], fill=(45, 48, 55))
    # main window
    d.rectangle([20, 40, 380, 280], fill=(50, 52, 58), outline=(80, 85, 95))
    # buttons
    d.rectangle([30, 50, 90, 72], fill=(70, 130, 200))
    d.rectangle([100, 50, 160, 72], fill=(70, 130, 200))
    d.rectangle([170, 50, 230, 72], fill=(70, 130, 200))
    d.rectangle([300, 250, 370, 275], fill=(200, 60, 60))
    im.save(path)


def test_detect_finds_titlebar_and_buttons(tmp_path: Path) -> None:
    img = tmp_path / "ui.png"
    _make_ui_fixture(img)
    result = detect_ui_elements(img)
    assert result["ok"]
    roles = {e["role"] for e in result["elements"]}
    assert "titlebar" in roles
    assert "button" in roles or "icon_button" in roles
    assert result["element_count"] >= 3


def test_describe_ui_polish(tmp_path: Path) -> None:
    img = tmp_path / "ui.png"
    _make_ui_fixture(img)
    det = detect_ui_elements(img)
    text = describe_ui_layout(det, locale="pl")
    assert "px" in text
    assert "element" in text.lower() or "wykryto" in text


def test_adopt_writes_contains_relations(tmp_path: Path) -> None:
    img = tmp_path / "ui.png"
    out = tmp_path / "rel.vql.json"
    _make_ui_fixture(img)
    payload = adopt_screenshot(img, out_program=out, locale="en")
    assert payload["ok"]
    data = out.read_text(encoding="utf-8")
    assert '"relations"' in data
    assert '"contains"' in data


def test_adopt_writes_vql_program(tmp_path: Path) -> None:
    img = tmp_path / "ui.png"
    out = tmp_path / "out.vql.json"
    _make_ui_fixture(img)
    payload = adopt_screenshot(img, out_program=out, locale="en")
    assert payload["ok"]
    assert out.is_file()
    assert payload["element_count"] >= 3
    assert "description" in payload
    data = out.read_text(encoding="utf-8")
    assert "ui_elements" in data
    assert '"role"' in data
