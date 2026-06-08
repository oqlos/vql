"""CLI for rest2vql."""

from __future__ import annotations

import argparse


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rest2vql", description="REST API for VQL control DSL")
    parser.add_argument("serve", nargs="?", default="serve")
    parser.add_argument("--port", type=int, default=8216)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args(argv)

    import uvicorn

    from rest2vql.app import create_app

    uvicorn.run(create_app(), host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
