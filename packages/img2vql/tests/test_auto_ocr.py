"""Tests for auto-OCR fallback in metadata."""

from __future__ import annotations

from unittest.mock import patch

from img2vql.metadata import _text_likely, auto_ocr_special_hits


def test_text_likely_when_edges_suggest_text() -> None:
    features = {
        "edges": {"text_likelihood": True},
        "scene": {"scene_class": "ui_blocks"},
        "special_hits": {"has_text": False, "ocr": {"skipped": True}},
    }
    assert _text_likely(features, features["special_hits"]) is True


def test_text_likely_false_when_has_text() -> None:
    features = {
        "edges": {"text_likelihood": True},
        "special_hits": {"has_text": True},
    }
    assert _text_likely(features, features["special_hits"]) is False


def test_auto_ocr_uses_rapidocr_when_available(tmp_path) -> None:
    from PIL import Image

    img = tmp_path / "texty.png"
    Image.new("RGB", (40, 40), (200, 200, 200)).save(img)
    features = {
        "edges": {"text_likelihood": True},
        "scene": {"scene_class": "ui_with_text"},
        "special_hits": {"has_text": False, "ocr": {"skipped": True}},
    }
    fake = {
        "has_text": True,
        "ocr": {"text_preview": "OK", "has_text": True, "source": "rapidocr"},
    }
    with patch("img2vql.metadata.rapidocr_special_hits", return_value=fake):
        out = auto_ocr_special_hits(img, features)
    assert out.get("has_text") is True
    assert out["ocr"]["source"] == "rapidocr"
