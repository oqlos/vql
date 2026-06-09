"""Per-backend capture diagnostics."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from vql.adopt.capture_backends import PORTAL_CAPTURE_SCRIPT, capture_backends, finalize_capture
from vql.adopt.capture_image import image_is_blank, image_stats
from vql.adopt.capture_policy import (
    capture_permission_hint,
    is_wayland,
    portal_python,
    session_type,
    should_use_interactive_portal,
)
from vql.adopt.capture_types import CaptureAttempt, CaptureInfo, require_pillow


def capture_diagnose(
    out: str | Path | None = None,
    *,
    monitor: int = 1,
    interactive_portal: bool | None = None,
) -> dict[str, Any]:
    """Try each capture backend and report why it failed (blank, denied, missing tool)."""
    require_pillow()
    path = Path(out or Path("/tmp/vql-capture-diagnose.png"))
    interactive = should_use_interactive_portal() if interactive_portal is None else interactive_portal
    attempts: list[CaptureAttempt] = []

    for name, backend in capture_backends(monitor=monitor, interactive_portal=interactive):
        probe = path.with_name(f"{path.stem}.{name}{path.suffix}")
        info: CaptureInfo | None = None
        err = ""
        portal_payload: dict[str, Any] = {}
        try:
            if name.startswith("portal"):
                py = portal_python()
                if py and PORTAL_CAPTURE_SCRIPT.is_file():
                    cmd = [py, str(PORTAL_CAPTURE_SCRIPT), "--out", str(probe)]
                    if name == "portal-interactive" or interactive:
                        cmd.append("--interactive")
                    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=45, check=False)
                    try:
                        portal_payload = json.loads(proc.stdout or "{}")
                    except json.JSONDecodeError:
                        portal_payload = {"error": (proc.stderr or proc.stdout or "").strip()}
                    if portal_payload.get("ok") and probe.is_file() and not image_is_blank(probe):
                        info = finalize_capture(probe, source="xdg-portal")
                    elif portal_payload.get("error"):
                        err = str(portal_payload["error"])
                else:
                    err = "portal python (python3-dbus, python3-gi) not found"
            else:
                info = backend(probe)
        except Exception as exc:
            err = str(exc)

        if info is not None:
            attempts.append(
                CaptureAttempt(
                    backend=name,
                    ok=True,
                    source=info.source,
                    stats=image_stats(probe),
                )
            )
            break

        blank = probe.is_file() and image_is_blank(probe)
        if blank:
            err = err or "image saved but all black (GNOME Screen Recording permission?)"
        elif probe.is_file():
            err = err or "image saved but rejected"
        elif not err:
            err = "backend unavailable or produced no file"

        stats = image_stats(probe) if probe.is_file() else {}
        if portal_payload:
            stats = {**stats, "portal": portal_payload}
        attempts.append(CaptureAttempt(backend=name, ok=False, blank=blank, error=err, stats=stats))
        if probe.is_file():
            probe.unlink(missing_ok=True)

    success = next((a for a in attempts if a.ok), None)
    return {
        "ok": success is not None,
        "session": session_type() or "unknown",
        "wayland": is_wayland(),
        "portal_python": portal_python(),
        "interactive_portal": interactive,
        "attempts": [a.to_dict() for a in attempts],
        "hint": capture_permission_hint(),
        "result": success.to_dict() if success else {},
    }
