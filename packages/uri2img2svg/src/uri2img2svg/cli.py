"""CLI for uri2img2svg."""

from __future__ import annotations

import argparse
import json
import sys

from uri2img2svg.query import query_uri


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="uri2img2svg", description="img2svg:// URI query")
    sub = parser.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("query", help="Query img2svg:// URI")
    q.add_argument("uri")

    args = parser.parse_args(argv)
    if args.cmd == "query":
        result = query_uri(args.uri)
        print(result.rendered or json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.ok else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
