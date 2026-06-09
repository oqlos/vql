"""CLI for img2vql — diagnose and UI detection."""

from __future__ import annotations

import argparse
import json
import sys

from img2vql.adopt import adopt_screenshot
from img2vql.describe_ui import describe_ui_layout
from img2vql.detect import detect_ui_elements
from img2vql.diagnose import diagnose_for_vql, diagnose_image


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="img2vql",
        description="Screenshot → VQL: diagnose, detect UI elements, adopt program",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("diagnose", help="img2nl diagnose for VQL capture")
    d.add_argument("image")
    d.add_argument("--vql-program", default="")
    d.add_argument("--locale", default="pl")
    d.add_argument("--translate-mode", default="auto", choices=["auto", "catalog", "offline"])
    d.add_argument("--save", action="store_true", help="Persist diagnose metadata into --vql-program")

    det = sub.add_parser("detect", help="Detect windows, panels, buttons on screenshot")
    det.add_argument("image")
    det.add_argument("--no-buttons", action="store_true")
    det.add_argument("--grid", type=int, default=48)
    det.add_argument("--locale", default="pl", help="Description language")
    det.add_argument("--describe", action="store_true", help="Include NL layout description")

    a = sub.add_parser("adopt", help="Detect UI + write VQL program JSON")
    a.add_argument("image")
    a.add_argument("--out", default="ui.vql.json")
    a.add_argument("--locale", default="pl")
    a.add_argument("--grid", type=int, default=12, help="Optional background color grid")
    a.add_argument("--with-grid", action="store_true", help="Add screen_regions color grid layer")
    a.add_argument("--no-buttons", action="store_true")

    args = parser.parse_args(argv)

    if args.cmd == "diagnose":
        if args.vql_program:
            payload = diagnose_for_vql(
                args.image,
                vql_program=args.vql_program,
                locale=args.locale,
                translate_mode=args.translate_mode,
                save_to_program=args.save,
            )
        else:
            payload = diagnose_image(args.image, locale=args.locale, translate_mode=args.translate_mode)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload.get("ok") else 1

    if args.cmd == "detect":
        payload = detect_ui_elements(
            args.image,
            detect_buttons=not args.no_buttons,
            grid=args.grid,
        )
        if args.describe and payload.get("ok"):
            payload["description"] = describe_ui_layout(payload, locale=args.locale)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload.get("ok") else 1

    if args.cmd == "adopt":
        payload = adopt_screenshot(
            args.image,
            out_program=args.out,
            locale=args.locale,
            include_grid=args.with_grid,
            grid=args.grid,
            detect_buttons=not args.no_buttons,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload.get("ok") else 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
