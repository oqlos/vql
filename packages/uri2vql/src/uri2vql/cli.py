"""CLI for uri2vql."""

from __future__ import annotations

import argparse
import json
import sys

from uri2vql.patch import patch_uri
from uri2vql.query import query_uri


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="uri2vql", description="vql:// URI query and patch")
    sub = parser.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("query", help="Query a vql:// URI")
    q.add_argument("uri")
    q.add_argument("--file", default="")
    q.add_argument("--format", default="json")

    p = sub.add_parser("patch", help="Patch via vql:// URI")
    p.add_argument("uri")
    p.add_argument("--with", dest="with_path", required=True)
    p.add_argument("--file", default="")

    r = sub.add_parser("run", help="Decode URI and dispatch via dsl2vql")
    r.add_argument("--uri", required=True)
    r.add_argument("--file", default="")

    s = sub.add_parser("resolve", help="Resolve NL prompt to vql:// URIs")
    s.add_argument("prompt")
    s.add_argument("--file", default="")
    s.add_argument("--monitor", type=int, default=1)
    s.add_argument("--grid", type=int, default=12)
    s.add_argument("--image", default="")

    c = sub.add_parser("capture-screen", help="Try desktop capture backends (debug)")
    c.add_argument("--out", default="/tmp/vql-screen.png")
    c.add_argument("--monitor", type=int, default=1)
    c.add_argument(
        "--interactive",
        action="store_true",
        help="Use xdg-desktop-portal interactive screenshot (GNOME/Wayland permission prompt)",
    )
    c.add_argument(
        "--diagnose",
        action="store_true",
        help="Show per-backend capture attempts (blank/denied/missing)",
    )

    w = sub.add_parser("analyze-window", help="Capture screen and adopt to VQL program")
    w.add_argument("--out", default="app.vql.json")
    w.add_argument("--monitor", type=int, default=1)
    w.add_argument("--grid", type=int, default=12)
    w.add_argument("--image", default="", help="Existing PNG instead of live capture")
    w.add_argument(
        "--interactive",
        action="store_true",
        help="GNOME/Wayland: xdg-portal screenshot with permission prompt (use when live capture is black)",
    )

    det = sub.add_parser("detect-window", help="Detect UI elements (windows, buttons) on screenshot")
    det.add_argument("--image", required=True)
    det.add_argument("--locale", default="pl")
    det.add_argument("--describe", action="store_true", default=True)

    ua = sub.add_parser("adopt-ui", help="Detect UI + write VQL program with ui_elements layer")
    ua.add_argument("--image", required=True)
    ua.add_argument("--out", default="ui.vql.json")
    ua.add_argument("--locale", default="pl")
    ua.add_argument("--with-grid", action="store_true")
    ua.add_argument("--grid", type=int, default=12)

    imgl_cmd = sub.add_parser("adopt-imgl", help="OCR + semantic UI layout via imgl → VQL program")
    imgl_cmd.add_argument("--image", required=True)
    imgl_cmd.add_argument("--out", default="layout.vql.json")
    imgl_cmd.add_argument("--lang", default="eng+pol")
    imgl_cmd.add_argument("--with-grid", action="store_true")
    imgl_cmd.add_argument("--grid", type=int, default=12)

    d = sub.add_parser("diagnose-window", help="img2nl-style diagnose: send capture to LLM?")
    d.add_argument("--image", required=True)
    d.add_argument("--vql-program", default="", help="Optional adopted VQL JSON for context")
    d.add_argument(
        "--locale",
        default="pl",
        help="Message language (European ISO 639-1: pl, en, de, fr, es, it, cs, uk, ...)",
    )
    d.add_argument(
        "--translate-mode",
        default="auto",
        choices=["auto", "catalog", "offline"],
        help="img2nl: auto=catalog+argostranslate; offline=require argos; catalog=JSON only",
    )
    d.add_argument(
        "--save",
        action="store_true",
        help="Persist diagnose metadata into --vql-program",
    )

    cmp = sub.add_parser("compare-window", help="Compare capture fingerprint vs VQL program baseline")
    cmp.add_argument("--image", required=True)
    cmp.add_argument("--vql-program", default="app.vql.json")

    ref = sub.add_parser("refresh-window", help="Refresh img2nl metadata in VQL program (no grid rebuild)")
    ref.add_argument("--image", default="", help="PNG path; default: metadata.image from program")
    ref.add_argument("--vql-program", default="app.vql.json")
    ref.add_argument("--locale", default="pl")

    ca = sub.add_parser(
        "capture-and-analyze",
        help="Interactive capture + analyze-window + optional diagnose",
    )
    ca.add_argument("--out", default="app.vql.json")
    ca.add_argument("--capture-out", default="", help="PNG path (default: /tmp/vql-capture.png)")
    ca.add_argument("--grid", type=int, default=12)
    ca.add_argument("--locale", default="pl")
    ca.add_argument("--diagnose", action="store_true", help="Run diagnose-window --save after analyze")
    ca.add_argument("--no-interactive", action="store_true", help="Disable xdg-portal interactive capture")

    args = parser.parse_args(argv)

    if args.cmd == "query":
        result = query_uri(args.uri, file=args.file or None, fmt=args.format)
        print(result.rendered or json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.ok else 1

    if args.cmd == "patch":
        content = open(args.with_path, encoding="utf-8").read()
        result = patch_uri(args.uri, content=content, file=args.file or None)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.ok else 1

    if args.cmd == "run":
        from dsl2vql import dispatch

        line = f'QUERY {args.uri}'
        if args.file:
            line += f" FILE {args.file}"
        result = dispatch(line, default_file=args.file or None)
        print(result.output or json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.ok else 1

    if args.cmd == "resolve":
        from uri2vql.nlp2uri import resolve_prompt_to_vql_uri

        hits = resolve_prompt_to_vql_uri(
            args.prompt,
            file=args.file or None,
            monitor=args.monitor,
            grid=args.grid,
            image=args.image or None,
        )
        print(json.dumps([hit.to_dict() for hit in hits], ensure_ascii=False, indent=2))
        return 0 if hits else 1

    if args.cmd == "capture-screen":
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

    if args.cmd == "analyze-window":
        from uri2vql.window import analyze_window_uri

        uri = f"vql://window/analyze?file={args.out}&monitor={args.monitor}&grid={args.grid}"
        if args.image:
            uri += f"&image={args.image}"
        result = analyze_window_uri(
            uri,
            file=args.out,
            monitor=args.monitor,
            grid=args.grid,
            image=args.image or None,
            interactive=args.interactive or None,
        )
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.ok else 1

    if args.cmd == "detect-window":
        from img2vql.detect import detect_ui_elements
        from img2vql.describe_ui import describe_ui_layout

        payload = detect_ui_elements(args.image)
        if args.describe and payload.get("ok"):
            payload["description"] = describe_ui_layout(payload, locale=args.locale)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload.get("ok") else 1

    if args.cmd == "adopt-ui":
        from img2vql.adopt import adopt_screenshot

        payload = adopt_screenshot(
            args.image,
            out_program=args.out,
            locale=args.locale,
            include_grid=args.with_grid,
            grid=args.grid,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload.get("ok") else 1

    if args.cmd == "adopt-imgl":
        try:
            from imgl import ImglConfig, analyze, write_vql_program
        except ImportError:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "error": "imgl not installed. Run: pip install -e /path/to/semcod/imgl",
                    },
                    indent=2,
                )
            )
            return 1

        scene = analyze(
            args.image,
            lang=args.lang,
            config=ImglConfig(use_img2vql=True),
        )
        out_path = write_vql_program(
            scene,
            args.out,
            include_grid=args.with_grid,
            grid=args.grid,
        )
        payload = {
            "ok": True,
            "path": args.image,
            "program": str(out_path),
            "element_count": scene.metadata.get("element_count", 0),
            "roles": scene.metadata.get("roles", {}),
            "detect_source": scene.metadata.get("detect_source", ""),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "diagnose-window":
        from uri2vql.window import diagnose_window_image

        payload = diagnose_window_image(
            args.image,
            vql_program=args.vql_program or None,
            locale=args.locale,
            translate_mode=args.translate_mode,
            save_to_program=args.save,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload.get("ok") else 1

    if args.cmd == "compare-window":
        from uri2vql.window import compare_window_image

        payload = compare_window_image(args.image, vql_program=args.vql_program)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload.get("ok") else 1

    if args.cmd == "refresh-window":
        from uri2vql.window import _resolve_window_image, refresh_window_metadata

        image = _resolve_window_image(args.vql_program, args.image or None)
        if not image:
            print(json.dumps({"ok": False, "error": "image missing; pass --image or set metadata.image"}, indent=2))
            return 1
        payload = refresh_window_metadata(
            image,
            vql_program=args.vql_program,
            locale=args.locale,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload.get("ok") else 1

    if args.cmd == "capture-and-analyze":
        from vql.adopt.window import CaptureError, capture_screen
        from uri2vql.window import analyze_window_uri, diagnose_window_image

        cap_path = args.capture_out or "/tmp/vql-capture.png"
        try:
            info = capture_screen(cap_path, interactive=not args.no_interactive)
        except (ImportError, CaptureError) as exc:
            print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
            return 1

        result = analyze_window_uri(
            f"vql://window/analyze?file={args.out}&grid={args.grid}&image={info.path}",
            file=args.out,
            grid=args.grid,
            image=info.path,
        )
        out: dict = {"capture": info.to_dict(), "analyze": result.to_dict()}
        if args.diagnose and result.ok:
            out["diagnose"] = diagnose_window_image(
                info.path,
                vql_program=args.out,
                locale=args.locale,
                save_to_program=True,
            )
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0 if result.ok else 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
