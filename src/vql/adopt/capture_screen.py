"""Capture the primary screen to PNG."""

from __future__ import annotations

import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from vql.adopt.capture_backends import capture_backends
from vql.adopt.capture_policy import capture_permission_hint, session_type, should_use_interactive_portal
from vql.adopt.capture_types import CaptureError, CaptureInfo, require_pillow


def active_window_title() -> str:
    if not shutil.which("xdotool"):
        return ""
    try:
        proc = subprocess.run(
            ["xdotool", "getactivewindow", "getwindowname"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        return (proc.stdout or "").strip()
    except Exception:
        return ""


def capture_screen(
    out: str | Path | None = None,
    *,
    monitor: int = 1,
    interactive: bool | None = None,
) -> CaptureInfo:
    """Capture the primary screen (or monitor index) to PNG."""
    require_pillow()
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path = Path(out or Path.home() / ".vql" / "captures" / f"screen_{ts}.png")
    use_interactive = should_use_interactive_portal() if interactive is None else interactive
    tried: list[str] = []
    info: CaptureInfo | None = None
    for name, backend in capture_backends(monitor=monitor, interactive_portal=use_interactive):
        tried.append(name)
        info = backend(path)
        if info is not None:
            break

    if info is None:
        session = session_type() or "unknown"
        raise CaptureError(
            "screen capture produced a blank image or failed on all backends "
            f"(tried: {', '.join(tried)}; session={session}). "
            f"{capture_permission_hint()} "
            "Try: uri2vql capture-screen --interactive "
            "or pass image= to vql://window/analyze."
        )

    info.window_title = active_window_title()
    return info
