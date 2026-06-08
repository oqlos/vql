"""CLI for nlp2vql."""

from __future__ import annotations

import argparse
import json
import sys

from nlp2vql.apply import apply_nl
from nlp2vql.to_dsl import to_dsl


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nlp2vql", description="NL → VQL control DSL")
    sub = parser.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("to-dsl", help="Convert NL to DSL line only")
    t.add_argument("prompt")
    t.add_argument("--file", default="")

    a = sub.add_parser("apply", help="Convert NL and dispatch")
    a.add_argument("prompt")
    a.add_argument("--file", default="")

    g = sub.add_parser("generate", help="Generate VQL program from NL")
    g.add_argument("prompt")
    g.add_argument("--out", default="app.vql.json")

    args = parser.parse_args(argv)

    if args.cmd == "to-dsl":
        print(to_dsl(args.prompt, file=args.file or None))
        return 0

    if args.cmd == "apply":
        result = apply_nl(args.prompt, file=args.file or None)
        print(result.output or json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.ok else 1

    if args.cmd == "generate":
        from dsl2vql import dispatch

        out = args.out
        quoted = f'"{args.prompt}"' if " " in args.prompt else args.prompt
        result = dispatch(f"GENERATE {quoted} OUT {out}")
        print(result.output or json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.ok else 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
