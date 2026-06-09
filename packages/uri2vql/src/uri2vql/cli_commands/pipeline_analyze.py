"""CLI commands for multi-level img2nl→LLM→VQL pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _import_image_to_vql():
    from uri2vql._bootstrap import ensure_img2vql

    ensure_img2vql()
    try:
        from img2vql.pipeline import image_to_vql, roundtrip_compare

        return image_to_vql, roundtrip_compare
    except ImportError as exc:
        hint = (
            "img2vql/img2nl not importable. From repo root:\n"
            "  bash install-dev.sh\n"
            "Or:\n"
            "  pip install -e ../../wronai/img2nl[analyze,similarity]\n"
            "  pip install -e packages/img2vql\n"
            "  pip install -e packages/uri2vql"
        )
        raise ImportError(f"{exc}\n{hint}") from exc


def run_pipeline_analyze(args: argparse.Namespace) -> int:
    try:
        image_to_vql, _ = _import_image_to_vql()
    except ImportError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    run_llm: bool | None = None
    if args.llm:
        run_llm = True
    elif getattr(args, "no_llm", False):
        run_llm = False

    payload = image_to_vql(
        args.image,
        out_program=args.out,
        locale=args.locale,
        grid=args.grid,
        adopt_method=args.method,
        run_llm=run_llm,
        render_out=args.render or None,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok") else 1


def run_vql_to_image(args: argparse.Namespace) -> int:
    """VQL → PNG uses core vql renderers (no img2vql required)."""
    try:
        from vql.renderers import render_to_png
        from vql.schema.program import VQLProgram
    except ImportError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    prog_path = Path(args.program)
    if not prog_path.is_file():
        print(json.dumps({"ok": False, "error": f"program not found: {prog_path}"}, indent=2))
        return 1

    try:
        program = VQLProgram.from_dict(json.loads(prog_path.read_text(encoding="utf-8")))
        out = render_to_png(program, args.out, scale=args.scale)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps({"ok": True, "program": str(prog_path), "render": out}, ensure_ascii=False, indent=2))
    return 0


def run_roundtrip(args: argparse.Namespace) -> int:
    try:
        _, roundtrip_compare = _import_image_to_vql()
    except ImportError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    payload = roundtrip_compare(
        args.image,
        out_program=args.out,
        out_render=args.render,
        locale=args.locale,
        run_llm=args.llm,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok") else 1
