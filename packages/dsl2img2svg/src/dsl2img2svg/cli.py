"""CLI for dsl2img2svg."""

from __future__ import annotations

import argparse
import sys

from dsl2img2svg.dispatch import dispatch


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dsl2img2svg")
    parser.add_argument("-c", "--command", required=True, help='e.g. VECTORIZE PATH img.png OUT out.svg')
    args = parser.parse_args(argv)
    result = dispatch(args.command)
    print(result.output or result.error or "")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
