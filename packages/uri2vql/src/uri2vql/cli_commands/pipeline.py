"""Multi-step capture + analyze CLI pipeline."""

from __future__ import annotations

import argparse
import json


def run_capture_and_analyze(args: argparse.Namespace) -> int:
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
