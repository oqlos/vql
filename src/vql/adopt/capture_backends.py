"""Desktop screenshot capture backends."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Callable

from vql.adopt.capture_image import image_is_blank
from vql.adopt.capture_policy import is_wayland, portal_python
from vql.adopt.capture_types import CaptureInfo, require_pillow

PORTAL_CAPTURE_SCRIPT = Path(__file__).resolve().with_name("portal_capture.py")


def finalize_capture(out: Path, *, source: str, geometry: dict[str, int] | None = None) -> CaptureInfo:
    require_pillow()
    from PIL import Image

    im = Image.open(out)
    return CaptureInfo(
        path=str(out),
        width=im.size[0],
        height=im.size[1],
        source=source,
        geometry=geometry,
    )


def run_capture(
    out: Path,
    *,
    source: str,
    runner: Callable[[Path], bool],
    geometry: dict[str, int] | None = None,
) -> CaptureInfo | None:
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.is_file():
        out.unlink()
    try:
        if not runner(out):
            return None
    except Exception:
        return None
    if not out.is_file() or out.stat().st_size < 64:
        return None
    if image_is_blank(out):
        return None
    return finalize_capture(out, source=source, geometry=geometry)


def capture_with_gnome_shell(out: Path) -> CaptureInfo | None:
    if not shutil.which("gdbus"):
        return None

    def runner(path: Path) -> bool:
        proc = subprocess.run(
            [
                "gdbus",
                "call",
                "--session",
                "--dest",
                "org.gnome.Shell.Screenshot",
                "--object-path",
                "/org/gnome/Shell/Screenshot",
                "--method",
                "org.gnome.Shell.Screenshot.Screenshot",
                "false",
                "false",
                str(path),
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        return proc.returncode == 0

    return run_capture(out, source="gnome-shell", runner=runner)


def capture_with_grim(out: Path) -> CaptureInfo | None:
    if not shutil.which("grim"):
        return None

    def runner(path: Path) -> bool:
        proc = subprocess.run(
            ["grim", str(path)],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        return proc.returncode == 0

    return run_capture(out, source="grim", runner=runner)


def capture_with_gnome_screenshot(out: Path) -> CaptureInfo | None:
    if not shutil.which("gnome-screenshot"):
        return None

    def runner(path: Path) -> bool:
        proc = subprocess.run(
            ["gnome-screenshot", "-f", str(path)],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        return proc.returncode == 0

    return run_capture(out, source="gnome-screenshot", runner=runner)


def capture_with_portal(out: Path, *, interactive: bool) -> CaptureInfo | None:
    py = portal_python()
    if not py:
        return None

    out.parent.mkdir(parents=True, exist_ok=True)
    if out.is_file():
        out.unlink()

    cmd = [py, str(PORTAL_CAPTURE_SCRIPT), "--out", str(out)]
    if interactive:
        cmd.append("--interactive")

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=45, check=False)
    except Exception:
        return None

    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return None

    if not payload.get("ok"):
        return None
    if not out.is_file() or out.stat().st_size < 64:
        return None
    if image_is_blank(out):
        return None
    return finalize_capture(out, source="xdg-portal")


def capture_with_scrot(out: Path) -> CaptureInfo | None:
    if not shutil.which("scrot"):
        return None

    def runner(path: Path) -> bool:
        proc = subprocess.run(
            ["scrot", str(path)],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        return proc.returncode == 0

    return run_capture(out, source="scrot", runner=runner)


def capture_with_mss(out: Path, *, monitor: int = 1) -> CaptureInfo | None:
    try:
        from mss import MSS
        from PIL import Image
    except ImportError:
        return None

    def runner(path: Path) -> bool:
        with MSS() as sct:
            idx = monitor if monitor < len(sct.monitors) else 1
            mon = sct.monitors[idx]
            shot = sct.grab(mon)
            im = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
            im.save(path)
        return True

    geometry: dict[str, int] | None = None
    try:
        from mss import MSS

        with MSS() as sct:
            idx = monitor if monitor < len(sct.monitors) else 1
            mon = sct.monitors[idx]
            geometry = {
                "left": mon["left"],
                "top": mon["top"],
                "width": mon["width"],
                "height": mon["height"],
            }
    except Exception:
        geometry = None

    return run_capture(out, source="mss", runner=runner, geometry=geometry)


def capture_backends(
    *,
    monitor: int,
    interactive_portal: bool = False,
) -> list[tuple[str, Callable[[Path], CaptureInfo | None]]]:
    forced = (os.environ.get("VQL_CAPTURE_BACKEND") or "auto").strip().lower()
    backends: dict[str, Callable[[Path], CaptureInfo | None]] = {
        "portal": lambda out: capture_with_portal(out, interactive=interactive_portal),
        "portal-interactive": lambda out: capture_with_portal(out, interactive=True),
        "gnome-shell": capture_with_gnome_shell,
        "grim": capture_with_grim,
        "gnome-screenshot": capture_with_gnome_screenshot,
        "scrot": capture_with_scrot,
        "mss": lambda out: capture_with_mss(out, monitor=monitor),
    }
    if forced != "auto" and forced in backends:
        return [(forced, backends[forced])]

    if is_wayland():
        order = ("portal", "gnome-shell", "grim", "gnome-screenshot", "scrot", "mss")
        if interactive_portal:
            order = ("portal-interactive", "portal", "gnome-shell", "grim", "gnome-screenshot", "scrot", "mss")
    else:
        order = ("scrot", "gnome-screenshot", "grim", "gnome-shell", "mss", "portal")
    return [(name, backends[name]) for name in order]
