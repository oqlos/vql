"""Environment and session policy for desktop capture."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def session_type() -> str:
    return (os.environ.get("XDG_SESSION_TYPE") or "").strip().lower()


def is_wayland() -> bool:
    return session_type() == "wayland" or bool(os.environ.get("WAYLAND_DISPLAY"))


def capture_interactive_mode() -> str:
    return (os.environ.get("VQL_CAPTURE_INTERACTIVE") or "auto").strip().lower()


def should_use_interactive_portal() -> bool:
    mode = capture_interactive_mode()
    if mode in {"1", "true", "yes", "interactive"}:
        return True
    if mode in {"0", "false", "no", "never"}:
        return False
    return sys.stdin.isatty() and sys.stdout.isatty()


def portal_python() -> str:
    candidates = [
        os.environ.get("VQL_PORTAL_PYTHON", ""),
        "/usr/bin/python3",
        shutil.which("python3") or "",
    ]
    for exe in candidates:
        if not exe or not Path(exe).is_file():
            continue
        try:
            proc = subprocess.run(
                [exe, "-c", "import dbus; from gi.repository import GLib"],
                capture_output=True,
                timeout=3,
                check=False,
            )
            if proc.returncode == 0:
                return exe
        except Exception:
            continue
    return ""


def capture_permission_hint() -> str:
    if not is_wayland():
        return "Install scrot or gnome-screenshot."
    return (
        "GNOME/Wayland: enable Settings → Privacy → Screen Recording for your terminal, "
        "then run: uri2vql capture-screen --interactive "
        "or gnome-screenshot (interactive). "
        "Black PNG with large size means capture ran without compositor permission."
    )
