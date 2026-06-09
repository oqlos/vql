"""imgl OCR enrichment in program metadata."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

from img2vql.metadata import imgl_ocr_special_hits, merge_program_metadata, refresh_program_metadata

pytest.importorskip("pytesseract")


def _text_image(path: Path, text: str = "Settings Username Save") -> Path:
    img = Image.new("RGB", (400, 120), (240, 240, 240))
    draw = ImageDraw.Draw(img)
    draw.text((20, 40), text, fill=(20, 20, 20))
    img.save(path)
    return path


def test_imgl_ocr_special_hits_finds_text(tmp_path: Path) -> None:
    img = _text_image(tmp_path / "ui.png")
    hits = imgl_ocr_special_hits(img)
    assert hits.get("has_text") is True
    assert "Settings" in hits.get("ocr", {}).get("text_preview", "")


def test_merge_program_metadata_uses_imgl_when_img2nl_misses(tmp_path: Path) -> None:
    img = _text_image(tmp_path / "screen.png")
    meta = merge_program_metadata({}, img, locale="en")
    special = meta.get("special_hits", {})
    assert special.get("has_text") is True
    assert special.get("ocr_preview")


def test_refresh_program_metadata_persists_imgl_ocr(tmp_path: Path) -> None:
    img = _text_image(tmp_path / "screen.png")
    prog = tmp_path / "app.vql.json"
    prog.write_text(
        json.dumps({"metadata": {}, "scene": {"width": 400, "height": 120, "layers": []}}),
        encoding="utf-8",
    )
    result = refresh_program_metadata(prog, img, locale="en")
    assert result.get("ok") is True
    assert result.get("special_hits", {}).get("has_text") is True
