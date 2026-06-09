"""Window analysis and adoption CLI commands."""

from __future__ import annotations

import argparse
import json


def run_analyze_window(args: argparse.Namespace) -> int:
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


def run_detect_window(args: argparse.Namespace) -> int:
    from img2vql.detect import detect_ui_elements
    from img2vql.describe_ui import describe_ui_layout

    payload = detect_ui_elements(args.image)
    if args.describe and payload.get("ok"):
        payload["description"] = describe_ui_layout(payload, locale=args.locale)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok") else 1


def run_adopt_ui(args: argparse.Namespace) -> int:
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


def run_adopt_imgl(args: argparse.Namespace) -> int:
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


def run_diagnose_window(args: argparse.Namespace) -> int:
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


def run_compare_window(args: argparse.Namespace) -> int:
    from uri2vql.window import compare_window_image

    payload = compare_window_image(args.image, vql_program=args.vql_program)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok") else 1


def run_refresh_window(args: argparse.Namespace) -> int:
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
