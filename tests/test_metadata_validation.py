"""Tests for imgl desktop metadata validation."""

from __future__ import annotations

import pytest

from vql.validation.metadata import validate_program_metadata


def test_empty_metadata_valid() -> None:
    assert validate_program_metadata({}) == []
    assert validate_program_metadata(None) == []


def test_valid_imgl_metadata() -> None:
    meta = {
        "source": "imgl",
        "image": "/tmp/screen.png",
        "capture": {"method": "mirror", "display": ":0", "monitor": 1},
        "window_os": {
            "win-1": {"app_label": "Firefox", "window_id": "0xabc", "vision_iou": 0.85},
        },
    }
    assert validate_program_metadata(meta) == []


def test_invalid_capture_type() -> None:
    issues = validate_program_metadata({"capture": "bad"})
    assert any("capture" in issue for issue in issues)


@pytest.mark.parametrize(
    "meta",
    [
        {"window_os": {"win-1": "not-an-object"}},
    ],
)
def test_invalid_window_os(meta: dict) -> None:
    issues = validate_program_metadata(meta)
    assert issues
