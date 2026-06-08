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

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
