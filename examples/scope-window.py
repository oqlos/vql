#!/usr/bin/env python3
"""Crop a screenshot to the imgl focus window (most interactive UI region)."""

from __future__ import annotations

import argparse
import json
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", help="Full-screen screenshot PNG")
    parser.add_argument("-o", "--output", help="Output crop path (default: <image>.<window>.png)")
    parser.add_argument("--lang", default="eng+pol", help="OCR language(s)")
    parser.add_argument(
        "--window",
        type=int,
        default=0,
        help="Window index (1-based). 0 = auto-pick most interactive region",
    )
    parser.add_argument("--window-id", help="Window id/title instead of index")
    parser.add_argument("--json", action="store_true", help="Print JSON result")
    args = parser.parse_args()

    try:
        from imgl.window_scope import scope_image_to_focus_window
    except ImportError:
        print("imgl not installed", file=sys.stderr)
        return 1

    window_index = None if args.window == 0 else args.window
    result = scope_image_to_focus_window(
        args.image,
        lang=args.lang,
        window_index=window_index,
        window_id=args.window_id,
        output_path=args.output,
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif result.get("ok"):
        print(result["path"])
    elif result.get("skipped"):
        print(result.get("source_image", args.image))
    else:
        print(result.get("reason", "scope failed"), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
