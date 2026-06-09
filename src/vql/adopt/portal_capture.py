"""Capture screenshot via xdg-desktop-portal (GNOME/Wayland).

Run with system Python (python3-dbus, python3-gi) when venv lacks dbus/gi:

    python3 -m vql.adopt.portal_capture --out /tmp/screen.png --interactive
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


def capture_via_portal(
    out: str | Path,
    *,
    interactive: bool = True,
    timeout_s: float = 30.0,
) -> dict:
    try:
        import dbus
        from dbus.mainloop.glib import DBusGMainLoop
        from gi.repository import GLib
    except ImportError as exc:
        return {
            "ok": False,
            "error": f"portal capture needs system python3-dbus and python3-gi: {exc}",
            "hint": "sudo apt install python3-dbus python3-gi gir1.2-glib-2.0",
        }

    out_path = Path(out).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result: dict = {"ok": False, "response": -1, "uri": ""}

    def on_response(response, results) -> None:
        result["response"] = int(response)
        if int(response) == 0:
            result["uri"] = str(results.get("uri", ""))
            result["ok"] = True
        elif int(response) == 1:
            result["error"] = "user cancelled portal screenshot"
        elif int(response) == 2:
            result["error"] = (
                "portal screenshot denied (Screen Recording permission missing). "
                "GNOME: Settings → Privacy → Screen Recording → enable Terminal/Cursor, "
                "or run with --interactive once to grant access."
            )
        else:
            result["error"] = f"portal screenshot failed with response={response}"
        loop.quit()

    DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    token = "vql_capture"
    unique = bus.get_unique_name()[1:].replace(".", "_")
    request_path = f"/org/freedesktop/portal/desktop/request/{unique}/{token}"
    bus.add_signal_receiver(
        on_response,
        dbus_interface="org.freedesktop.portal.Request",
        path=request_path,
    )
    proxy = bus.get_object("org.freedesktop.portal.Desktop", "/org/freedesktop/portal/desktop")
    iface = dbus.Interface(proxy, dbus_interface="org.freedesktop.portal.Screenshot")
    iface.Screenshot(
        "",
        {
            "interactive": dbus.Boolean(interactive),
            "handle_token": token,
        },
    )

    loop = GLib.MainLoop()
    GLib.timeout_add_seconds(int(timeout_s), loop.quit)
    loop.run()

    if not result.get("ok"):
        return result

    src = Path(unquote(urlparse(result["uri"]).path))
    if not src.is_file():
        return {"ok": False, "error": f"portal uri missing file: {result['uri']}"}

    shutil.copy2(src, out_path)
    return {
        "ok": True,
        "path": str(out_path),
        "source": "xdg-portal",
        "interactive": interactive,
        "uri": result["uri"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="xdg-desktop-portal screenshot helper")
    parser.add_argument("--out", required=True)
    parser.add_argument("--interactive", action="store_true", default=False)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args(argv)
    payload = capture_via_portal(args.out, interactive=args.interactive, timeout_s=args.timeout)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
