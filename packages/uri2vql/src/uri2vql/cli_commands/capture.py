"""Desktop capture CLI commands."""

from __future__ import annotations

import argparse
import json


def run_capture_screen(args: argparse.Namespace) -> int:
    from vql.adopt.window import CaptureError, capture_diagnose, capture_screen

    try:
        if args.diagnose:
            payload = capture_diagnose(
                args.out,
                monitor=args.monitor,
                interactive_portal=args.interactive or None,
            )
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0 if payload.get("ok") else 1

        info = capture_screen(
            args.out,
            monitor=args.monitor,
            interactive=args.interactive or None,
        )
        print(
            json.dumps(
                {
                    "ok": True,
                    "source": info.source,
                    "path": info.path,
                    "width": info.width,
                    "height": info.height,
                    "window_title": info.window_title,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    except ImportError as exc:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": str(exc),
                    "hint": "pip install 'vql[desktop]' pillow mss",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1
    except CaptureError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
