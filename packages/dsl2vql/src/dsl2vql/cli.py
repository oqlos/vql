"""CLI for VQL control DSL."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SUBCOMMANDS = frozenset({"validate-schema", "encode", "decode", "replay"})


def _main_legacy(argv: list[str]) -> int:
    from dsl2vql.engine import execute_dsl, execute_dsl_line

    parser = argparse.ArgumentParser(
        prog="dsl2vql",
        description="Control VQL programs via DSL (QUERY, VALIDATE, RENDER, GENERATE, ...)",
    )
    parser.add_argument("script", nargs="?", help="Optional .dsl script file")
    parser.add_argument("-c", "--command", help="Execute single DSL command")
    parser.add_argument("--file", help="Default app.vql.json path")
    parser.add_argument("--json", action="store_true", help="Print JSON results")
    args = parser.parse_args(argv)

    if args.command:
        results = [execute_dsl_line(args.command, default_file=args.file)]
    elif args.script:
        text = Path(args.script).read_text(encoding="utf-8")
        results = execute_dsl(text, default_file=args.file)
    else:
        text = sys.stdin.read()
        if not text.strip():
            parser.print_help()
            return 1
        results = execute_dsl(text, default_file=args.file)

    exit_code = 0
    for result in results:
        if args.json:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            if result.error:
                print(f"error: {result.error}", file=sys.stderr)
            if result.output:
                print(result.output.rstrip())
        if not result.ok:
            exit_code = 1
    return exit_code


def _main_subcommand(argv: list[str]) -> int:
    cmd = argv[0]
    if cmd == "validate-schema":
        from dsl2vql.schema_registry import validate_schema_registry

        errors = validate_schema_registry()
        if errors:
            for e in errors:
                print(e, file=sys.stderr)
            return 1
        print("schema registry OK")
        return 0
    if cmd == "encode":
        from dsl2vql.codec import encode_protobuf

        line = argv[1] if len(argv) > 1 else sys.stdin.read().strip()
        sys.stdout.buffer.write(encode_protobuf(line))
        return 0
    if cmd == "decode":
        from dsl2vql.codec import decode_protobuf

        data = sys.stdin.buffer.read()
        print(decode_protobuf(data))
        return 0
    if cmd == "replay":
        from dsl2vql.events import EventStore

        parser = argparse.ArgumentParser()
        parser.add_argument("--file", default="app.vql.json")
        args = parser.parse_args(argv[1:])
        store = EventStore(Path(args.file).with_suffix(".events.pb"))
        for event in store.replay():
            print(json.dumps(event.to_dict(), ensure_ascii=False))
        return 0
    return 1


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    if argv and argv[0] in _SUBCOMMANDS:
        return _main_subcommand(argv)
    return _main_legacy(argv)


if __name__ == "__main__":
    raise SystemExit(main())
