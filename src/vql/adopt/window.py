"""Capture desktop/window screenshots and adopt them as VQL programs."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from vql.schema.program import Layer, Object, Primitive, Scene, Style, VQLProgram


class CaptureError(RuntimeError):
    """Raised when no capture backend produced a usable image."""


def _require_pillow() -> None:
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


def _session_type() -> str:
    return (os.environ.get("XDG_SESSION_TYPE") or "").strip().lower()


def _is_wayland() -> bool:
    return _session_type() == "wayland" or bool(os.environ.get("WAYLAND_DISPLAY"))


def _capture_interactive_mode() -> str:
    return (os.environ.get("VQL_CAPTURE_INTERACTIVE") or "auto").strip().lower()


def _should_use_interactive_portal() -> bool:
    mode = _capture_interactive_mode()
    if mode in {"1", "true", "yes", "interactive"}:
        return True
    if mode in {"0", "false", "no", "never"}:
        return False
    return sys.stdin.isatty() and sys.stdout.isatty()


def _portal_python() -> str:
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


def image_stats(path: str | Path, *, dark_threshold: int = 8) -> dict[str, Any]:
    """Return quick heuristics for a PNG/JPEG (blank detection, brightness, size)."""
    _require_pillow()
    from PIL import Image

    p = Path(path).expanduser()
    if not p.is_file():
        return {"ok": False, "path": str(p), "error": "file not found"}

    im = Image.open(p).convert("RGB")
    w, h = im.size
    small = im.resize((32, 32))
    pixels = list(small.get_flattened_data())
    unique = len(set(pixels))
    brightness = [int(0.299 * r + 0.587 * g + 0.114 * b) for r, g, b in pixels]
    b_min, b_max = min(brightness), max(brightness)
    b_avg = sum(brightness) // len(brightness)
    top = Counter(pixels).most_common(3)
    is_blank = _image_is_blank(p, dark_threshold=dark_threshold)
    return {
        "ok": True,
        "path": str(p),
        "width": w,
        "height": h,
        "bytes": p.stat().st_size,
        "unique_colors_sampled": unique,
        "brightness_min": b_min,
        "brightness_max": b_max,
        "brightness_avg": b_avg,
        "top_colors": [f"#{r:02X}{g:02X}{b:02X}" for (r, g, b), _ in top],
        "is_blank": is_blank,
    }


def _image_is_blank(path: Path, *, dark_threshold: int = 8) -> bool:
    """True when capture looks empty (all black / single dark color)."""
    _require_pillow()
    from PIL import Image

    im = Image.open(path).convert("RGB")
    if im.size[0] < 2 or im.size[1] < 2:
        return True
    small = im.resize((32, 32))
    pixels = list(small.get_flattened_data())
    if not pixels:
        return True
    unique = set(pixels)
    if len(unique) == 1 and max(unique.pop()) < dark_threshold:
        return True
    if all(max(px) < dark_threshold for px in pixels):
        return True
    return False


def _finalize_capture(out: Path, *, source: str, geometry: dict[str, int] | None = None) -> CaptureInfo:
    _require_pillow()
    from PIL import Image

    im = Image.open(out)
    return CaptureInfo(
        path=str(out),
        width=im.size[0],
        height=im.size[1],
        source=source,
        geometry=geometry,
    )


def _run_capture(
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
    if _image_is_blank(out):
        return None
    return _finalize_capture(out, source=source, geometry=geometry)


def _capture_with_gnome_shell(out: Path) -> CaptureInfo | None:
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

    return _run_capture(out, source="gnome-shell", runner=runner)


def _capture_with_grim(out: Path) -> CaptureInfo | None:
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

    return _run_capture(out, source="grim", runner=runner)


def _capture_with_gnome_screenshot(out: Path) -> CaptureInfo | None:
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

    return _run_capture(out, source="gnome-screenshot", runner=runner)


def _capture_with_portal(out: Path, *, interactive: bool) -> CaptureInfo | None:
    py = _portal_python()
    if not py:
        return None

    out.parent.mkdir(parents=True, exist_ok=True)
    if out.is_file():
        out.unlink()

    script = Path(__file__).with_name("portal_capture.py")
    cmd = [py, str(script), "--out", str(out)]
    if interactive:
        cmd.append("--interactive")

    portal_error = ""
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=45, check=False)
    except Exception as exc:
        portal_error = str(exc)
        return None

    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        portal_error = (proc.stderr or proc.stdout or "invalid portal json").strip()
        return None

    if not payload.get("ok"):
        portal_error = str(payload.get("error") or payload.get("hint") or "portal failed")
        return None
    if not out.is_file() or out.stat().st_size < 64:
        portal_error = "portal succeeded but output file missing"
        return None
    if _image_is_blank(out):
        return None
    return _finalize_capture(out, source="xdg-portal")


def _capture_with_scrot(out: Path) -> CaptureInfo | None:
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

    return _run_capture(out, source="scrot", runner=runner)


def _capture_with_mss(out: Path, *, monitor: int = 1) -> CaptureInfo | None:
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

    return _run_capture(out, source="mss", runner=runner, geometry=geometry)


def _capture_backends(
    *,
    monitor: int,
    interactive_portal: bool = False,
) -> list[tuple[str, Callable[[Path], CaptureInfo | None]]]:
    forced = (os.environ.get("VQL_CAPTURE_BACKEND") or "auto").strip().lower()
    backends: dict[str, Callable[[Path], CaptureInfo | None]] = {
        "portal": lambda out: _capture_with_portal(out, interactive=interactive_portal),
        "portal-interactive": lambda out: _capture_with_portal(out, interactive=True),
        "gnome-shell": _capture_with_gnome_shell,
        "grim": _capture_with_grim,
        "gnome-screenshot": _capture_with_gnome_screenshot,
        "scrot": _capture_with_scrot,
        "mss": lambda out: _capture_with_mss(out, monitor=monitor),
    }
    if forced != "auto" and forced in backends:
        return [(forced, backends[forced])]

    if _is_wayland():
        order = ("portal", "gnome-shell", "grim", "gnome-screenshot", "scrot", "mss")
        if interactive_portal:
            order = ("portal-interactive", "portal", "gnome-shell", "grim", "gnome-screenshot", "scrot", "mss")
    else:
        order = ("scrot", "gnome-screenshot", "grim", "gnome-shell", "mss", "portal")
    return [(name, backends[name]) for name in order]


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


def capture_diagnose(
    out: str | Path | None = None,
    *,
    monitor: int = 1,
    interactive_portal: bool | None = None,
) -> dict[str, Any]:
    """Try each capture backend and report why it failed (blank, denied, missing tool)."""
    _require_pillow()
    path = Path(out or Path("/tmp/vql-capture-diagnose.png"))
    interactive = _should_use_interactive_portal() if interactive_portal is None else interactive_portal
    attempts: list[CaptureAttempt] = []

    for name, backend in _capture_backends(monitor=monitor, interactive_portal=interactive):
        probe = path.with_name(f"{path.stem}.{name}{path.suffix}")
        info: CaptureInfo | None = None
        err = ""
        portal_payload: dict[str, Any] = {}
        try:
            if name.startswith("portal"):
                py = _portal_python()
                script = Path(__file__).with_name("portal_capture.py")
                if py and script.is_file():
                    cmd = [py, str(script), "--out", str(probe)]
                    if name == "portal-interactive" or interactive:
                        cmd.append("--interactive")
                    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=45, check=False)
                    try:
                        portal_payload = json.loads(proc.stdout or "{}")
                    except json.JSONDecodeError:
                        portal_payload = {"error": (proc.stderr or proc.stdout or "").strip()}
                    if portal_payload.get("ok") and probe.is_file() and not _image_is_blank(probe):
                        info = _finalize_capture(probe, source="xdg-portal")
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

        blank = probe.is_file() and _image_is_blank(probe)
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
        "session": _session_type() or "unknown",
        "wayland": _is_wayland(),
        "portal_python": _portal_python(),
        "interactive_portal": interactive,
        "attempts": [a.to_dict() for a in attempts],
        "hint": _capture_permission_hint(),
        "result": success.to_dict() if success else {},
    }


def _capture_permission_hint() -> str:
    if not _is_wayland():
        return "Install scrot or gnome-screenshot."
    return (
        "GNOME/Wayland: enable Settings → Privacy → Screen Recording for your terminal, "
        "then run: uri2vql capture-screen --interactive "
        "or gnome-screenshot (interactive). "
        "Black PNG with large size means capture ran without compositor permission."
    )


def _active_window_title() -> str:
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
    _require_pillow()
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path = Path(out or Path.home() / ".vql" / "captures" / f"screen_{ts}.png")
    use_interactive = _should_use_interactive_portal() if interactive is None else interactive
    tried: list[str] = []
    info: CaptureInfo | None = None
    for name, backend in _capture_backends(monitor=monitor, interactive_portal=use_interactive):
        tried.append(name)
        info = backend(path)
        if info is not None:
            break

    if info is None:
        session = _session_type() or "unknown"
        raise CaptureError(
            "screen capture produced a blank image or failed on all backends "
            f"(tried: {', '.join(tried)}; session={session}). "
            f"{_capture_permission_hint()} "
            "Try: uri2vql capture-screen --interactive "
            "or pass image= to vql://window/analyze."
        )

    info.window_title = _active_window_title()
    return info


def _hex_color(rgb: tuple[int, int, int]) -> str:
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


def _optional_fingerprint(image_path: Path) -> dict[str, Any]:
    """Best-effort fingerprint when img2nl is available without img2vql."""
    try:
        from PIL import Image
        from img2nl.features.fingerprint import analyze_fingerprint

        fp = analyze_fingerprint(Image.open(image_path))
        return {"fingerprint": fp} if fp.get("available") else {}
    except ImportError:
        return {}


def _enrich_program_metadata(base: dict[str, Any], path: Path) -> dict[str, Any]:
    try:
        from img2vql.metadata import merge_program_metadata

        return merge_program_metadata(base, path)
    except ImportError:
        meta = {
            **base,
            "analyzed_at": datetime.now(UTC).isoformat(),
            "image": str(path),
            **_optional_fingerprint(path),
        }
        return meta


def _merge_grid_colors(
    colors: list[list[tuple[int, int, int]]],
    *,
    grid: int,
) -> list[tuple[int, int, int, int, tuple[int, int, int]]]:
    """Return merged rectangles as (gx, gy, w_span, h_span, rgb)."""
    visited = [[False] * grid for _ in range(grid)]
    merged: list[tuple[int, int, int, int, tuple[int, int, int]]] = []

    for gy in range(grid):
        for gx in range(grid):
            if visited[gy][gx]:
                continue
            base = colors[gy][gx]
            w_span = 1
            while gx + w_span < grid and not visited[gy][gx + w_span] and colors[gy][gx + w_span] == base:
                w_span += 1
            h_span = 1
            while gy + h_span < grid:
                ok = True
                for dx in range(w_span):
                    if visited[gy + h_span][gx + dx] or colors[gy + h_span][gx + dx] != base:
                        ok = False
                        break
                if not ok:
                    break
                h_span += 1
            for dy in range(h_span):
                for dx in range(w_span):
                    visited[gy + dy][gx + dx] = True
            merged.append((gx, gy, w_span, h_span, base))
    return merged


def screenshot_to_program(
    image_path: str | Path,
    *,
    grid: int = 12,
    min_region_px: int = 40,
    capture: CaptureInfo | None = None,
    merge_regions: bool = True,
) -> VQLProgram:
    """
    Adopt a screenshot into a VQL program.

    Uses a coarse color grid to emit rectangle primitives — a vector-ish summary
    of the window/screen layout (regions + dominant colors).
    Adjacent same-color cells are merged when ``merge_regions=True``.
    """
    _require_pillow()
    from PIL import Image

    path = Path(image_path)
    im = Image.open(path).convert("RGB")
    w, h = im.size
    cell_w = max(1, w // grid)
    cell_h = max(1, h // grid)
    small = im.resize((grid, grid))

    colors: list[list[tuple[int, int, int]]] = []
    for gy in range(grid):
        row: list[tuple[int, int, int]] = []
        for gx in range(grid):
            rgb = small.getpixel((gx, gy))
            if isinstance(rgb, int):
                rgb = (rgb, rgb, rgb)
            row.append(rgb)
        colors.append(row)

    objects: list[Object] = []
    if merge_regions:
        regions = _merge_grid_colors(colors, grid=grid)
        for idx, (gx, gy, w_span, h_span, rgb) in enumerate(regions):
            rw, rh = w_span * cell_w, h_span * cell_h
            if rw < min_region_px and rh < min_region_px:
                continue
            cx = (gx + w_span / 2) * cell_w
            cy = (gy + h_span / 2) * cell_h
            color = _hex_color(rgb)
            objects.append(
                Object(
                    id=f"region_{idx:03d}",
                    primitives=[
                        Primitive(
                            shape_type="rectangle",
                            params={"width": float(rw), "height": float(rh)},
                        )
                    ],
                    style=Style(color=color, fill=True, stroke_width=0.0),
                    center_x=cx,
                    center_y=cy,
                    metadata={
                        "grid": [gx, gy],
                        "span": [w_span, h_span],
                        "rgb": list(rgb),
                        "source": "merged_region",
                    },
                )
            )
    else:
        idx = 0
        for gy in range(grid):
            for gx in range(grid):
                rgb = colors[gy][gx]
                cx = (gx + 0.5) * cell_w
                cy = (gy + 0.5) * cell_h
                color = _hex_color(rgb)
                objects.append(
                    Object(
                        id=f"cell_{idx:03d}",
                        primitives=[
                            Primitive(
                                shape_type="rectangle",
                                params={"width": cell_w, "height": cell_h},
                            )
                        ],
                        style=Style(color=color, fill=True, stroke_width=0.0),
                        center_x=cx,
                        center_y=cy,
                        metadata={"grid": [gx, gy], "rgb": list(rgb)},
                    )
                )
                idx += 1

    # Global palette from downsampled image
    palette = Counter(small.get_flattened_data()).most_common(8)
    dominant_colors = [_hex_color(c) for c, _ in palette]

    meta = _enrich_program_metadata(
        {
            "source": "screenshot_adopt",
            "grid": grid,
            "merge_regions": merge_regions,
            "region_count": len(objects),
            "dominant_colors": dominant_colors,
        },
        path,
    )
    if capture:
        meta["capture"] = capture.to_dict()

    return VQLProgram(
        scene=Scene(
            width=float(w),
            height=float(h),
            app="desktop",
            url=f"file://{path.resolve()}",
            layers=[Layer(id="screen_regions", objects=objects)],
        ),
        metadata=meta,
    )


def analyze_screenshot(
    image_path: str | Path | None = None,
    *,
    out_program: str | Path = "app.vql.json",
    monitor: int = 1,
    grid: int = 12,
    interactive: bool | None = None,
    skip_if_unchanged: bool = True,
    locale: str = "pl",
) -> dict[str, Any]:
    """Capture (if needed) + adopt screenshot → VQL JSON program."""
    capture: CaptureInfo | None = None
    if image_path is not None:
        path = Path(image_path).expanduser()
        if not path.is_file():
            raise FileNotFoundError(
                f"image not found: {path}. "
                "On GNOME/Wayland grim often fails; try: "
                "uri2vql capture-screen --interactive "
                "or gnome-screenshot and use ~/Pictures/Screenshots/*.png"
            )
        image_path = path
    else:
        capture = capture_screen(monitor=monitor, interactive=interactive)
        image_path = capture.path

    stats = image_stats(image_path)
    if stats.get("is_blank"):
        return {
            "ok": False,
            "program": str(out_program),
            "image": str(image_path),
            "error": "screenshot is blank (all black) — GNOME blocked capture without permission",
            "image_stats": stats,
            "hint": _capture_permission_hint(),
            "recommendation": "skip_llm_blank_capture",
        }

    out = Path(out_program).expanduser()
    if skip_if_unchanged and out.is_file():
        try:
            from img2vql.fingerprint import compare_with_program
            from img2vql.metadata import refresh_program_metadata

            cmp = compare_with_program(image_path, out)
            if cmp.get("ok") and cmp.get("match"):
                refreshed = refresh_program_metadata(out, image_path, locale=locale)
                if refreshed.get("ok"):
                    from vql.schema.program import VQLProgram

                    data = json.loads(out.read_text(encoding="utf-8"))
                    program = VQLProgram.from_dict(data)
                    meta = refreshed.get("metadata", {})
                    return {
                        "ok": True,
                        "program": str(out),
                        "image": str(image_path),
                        "unchanged": True,
                        "skipped_adopt": True,
                        "object_count": program.object_count(),
                        "dominant_colors": meta.get("dominant_colors", []),
                        "fingerprint": meta.get("fingerprint", {}),
                        "special_hits": meta.get("special_hits", {}),
                        "scene_class": meta.get("scene_class", ""),
                        "similarity": meta.get("similarity", cmp.get("similarity", {})),
                        "scene": {"width": program.scene.width, "height": program.scene.height},
                        "window_title": capture.window_title if capture else "",
                        "image_stats": stats,
                        "recommendation": "skip_unchanged_screen",
                    }
        except ImportError:
            pass

    program = screenshot_to_program(image_path, grid=grid, capture=capture)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(program.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    payload: dict[str, Any] = {
        "ok": True,
        "program": str(out),
        "image": str(image_path),
        "object_count": program.object_count(),
        "dominant_colors": program.metadata.get("dominant_colors", []),
        "fingerprint": program.metadata.get("fingerprint", {}),
        "special_hits": program.metadata.get("special_hits", {}),
        "scene_class": program.metadata.get("scene_class", ""),
        "similarity": program.metadata.get("similarity", {}),
        "scene": {"width": program.scene.width, "height": program.scene.height},
        "window_title": capture.window_title if capture else "",
        "image_stats": stats,
    }
    if stats.get("unique_colors_sampled", 0) <= 2:
        payload["warning"] = "very low color diversity — verify capture is not a failed Wayland grab"
    return payload
