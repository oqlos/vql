"""Types for desktop screenshot capture."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class CaptureError(RuntimeError):
    """Raised when no capture backend produced a usable image."""


def require_pillow() -> None:
    try:
        from PIL import Image  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "Pillow is required for screen capture and window analysis. "
            "Install with: pip install 'vql[desktop]' or pip install pillow"
        ) from exc


@dataclass
class CaptureInfo:
    path: str
    width: int
    height: int
    source: str
    window_title: str = ""
    geometry: dict[str, int] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "width": self.width,
            "height": self.height,
            "source": self.source,
            "window_title": self.window_title,
            "geometry": self.geometry,
        }


@dataclass
class CaptureAttempt:
    backend: str
    ok: bool
    blank: bool = False
    error: str = ""
    source: str = ""
    stats: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "backend": self.backend,
            "ok": self.ok,
            "blank": self.blank,
            "error": self.error,
            "source": self.source,
            "stats": self.stats,
        }
