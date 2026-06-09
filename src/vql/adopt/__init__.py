"""Adopt external sources into VQL programs."""

from vql.adopt.window import (
    CaptureError,
    analyze_screenshot,
    capture_diagnose,
    capture_screen,
    image_stats,
    screenshot_to_program,
)

__all__ = [
    "CaptureError",
    "analyze_screenshot",
    "capture_diagnose",
    "capture_screen",
    "image_stats",
    "screenshot_to_program",
]
