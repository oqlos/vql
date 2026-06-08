"""cli2vql — shell REPL / exec over VQL control DSL."""

from __future__ import annotations

import argparse
import json
import sys

from dsl2vql import dispatch, execute_dsl


def _repl(default_file: str | None) -> int:
    print("cli2vql shell — type DSL lines (Ctrl-D to exit)")
    while True:
        try:
            line = input("vql> ").strip()
        except EOFError:
            print()
            return 0
        if not line:
            continue
        result = dispatch(line, default_file=default_file)
        if result.error:
            print(f"error: {result.error}", file=sys.stderr)
        if result.output:
            print(result.output.rstrip())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cli2vql", description="VQL control DSL shell")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("shell", help="Interactive REPL")
    e = sub.add_parser("exec", help="Execute single DSL command")
    e.add_argument("command")
    r = sub.add_parser("run", help="Run DSL script file")
    r.add_argument("script")

    parser.add_argument("--file", default="", help="Default app.vql.json")
    args, rest = parser.parse_known_args(argv)

    default_file = args.file or None

    if args.cmd == "shell" or (not args.cmd and not rest):
        return _repl(default_file)
    if args.cmd == "exec":
        cmd = rest[0] if rest else getattr(args, "command", "")
        result = dispatch(cmd, default_file=default_file)
        print(result.output or json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.ok else 1
    if args.cmd == "run":
        from pathlib import Path

        text = Path(rest[0] if rest else args.script).read_text(encoding="utf-8")
        exit_code = 0
        for result in execute_dsl(text, default_file=default_file):
            if result.output:
                print(result.output.rstrip())
            if not result.ok:
                exit_code = 1
        return exit_code

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
