"""CLI for img2svg — raster → SVG / VQL."""

from __future__ import annotations

import argparse
import json
import sys

from img2svg.svg_emit import image_to_svg
from img2svg.to_vql import image_to_vql
from img2svg.trace import trace_contours_opencv, trace_image_regions, trace_vtracer


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="img2svg", description="Raster image → SVG / VQL")
    sub = parser.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("trace", help="Trace image to regions (JSON)")
    t.add_argument("image")
    t.add_argument("--grid", type=int, default=24)
    t.add_argument("--method", default="regions", choices=["regions", "contours", "vtracer"])

    s = sub.add_parser("svg", help="Convert image to SVG file")
    s.add_argument("image")
    s.add_argument("--out", default="")
    s.add_argument("--grid", type=int, default=24)
    s.add_argument("--method", default="regions", choices=["regions", "contours", "vtracer"])

    v = sub.add_parser("vql", help="Convert image to VQL program JSON")
    v.add_argument("image")
    v.add_argument("--out", default="")
    v.add_argument("--grid", type=int, default=24)
    v.add_argument("--method", default="regions", choices=["regions", "contours", "vtracer"])

    args = parser.parse_args(argv)

    if args.cmd == "trace":
        if args.method == "contours":
            payload = trace_contours_opencv(args.image)
        elif args.method == "vtracer":
            payload = trace_vtracer(args.image)
        else:
            payload = trace_image_regions(args.image, grid=args.grid)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload.get("ok") else 1

    if args.cmd == "svg":
        payload = image_to_svg(
            args.image,
            out_path=args.out or None,
            grid=args.grid,
            method=args.method,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload.get("ok") else 1

    if args.cmd == "vql":
        payload = image_to_vql(
            args.image,
            out_program=args.out or None,
            grid=args.grid,
            method=args.method,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload.get("ok") else 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
