"""Adopt a desktop screenshot into a VQL program via vql://window/analyze."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WindowAnalyzeResult:
    ok: bool
    uri: str
    program: str
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "uri": self.uri,
            "program": self.program,
            "data": self.data,
            "error": self.error,
        }


def analyze_window_uri(
    uri: str,
    *,
    file: str = "app.vql.json",
    monitor: int = 1,
    grid: int = 12,
    image: str | None = None,
    interactive: bool | None = None,
) -> WindowAnalyzeResult:
    """
    Adopt a desktop screenshot into a VQL program file, addressable via URI.

    URI examples:
      vql://window/analyze?file=app.vql.json
      vql://window/analyze?file=app.vql.json&monitor=1&grid=16
    """
    from vql.adopt.window import analyze_screenshot

    try:
        if not uri.startswith("vql://window/"):
            return WindowAnalyzeResult(ok=False, uri=uri, program=file, error="not a window URI")
        data = analyze_screenshot(
            image,
            out_program=file,
            monitor=monitor,
            grid=grid,
            interactive=interactive,
        )
        ok = bool(data.get("ok", True))
        return WindowAnalyzeResult(
            ok=ok,
            uri=uri,
            program=file,
            data=data,
            error=None if ok else data.get("error"),
        )
    except Exception as exc:
        return WindowAnalyzeResult(ok=False, uri=uri, program=file, error=str(exc))
