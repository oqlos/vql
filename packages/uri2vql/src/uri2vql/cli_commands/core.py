"""Core uri2vql CLI commands: query, patch, run, resolve."""

from __future__ import annotations

import argparse
import json

from uri2vql.patch import patch_uri
from uri2vql.query import query_uri


def run_query(args: argparse.Namespace) -> int:
    result = query_uri(args.uri, file=args.file or None, fmt=args.format)
    print(result.rendered or json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0 if result.ok else 1


def run_patch(args: argparse.Namespace) -> int:
    content = open(args.with_path, encoding="utf-8").read()
    result = patch_uri(args.uri, content=content, file=args.file or None)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0 if result.ok else 1


def run_run(args: argparse.Namespace) -> int:
    from dsl2vql import dispatch

    line = f"QUERY {args.uri}"
    if args.file:
        line += f" FILE {args.file}"
    result = dispatch(line, default_file=args.file or None)
    print(result.output or json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0 if result.ok else 1


def run_resolve(args: argparse.Namespace) -> int:
    from uri2vql.nlp2uri import resolve_prompt_to_vql_uri

    hits = resolve_prompt_to_vql_uri(
        args.prompt,
        file=args.file or None,
        monitor=args.monitor,
        grid=args.grid,
        image=args.image or None,
    )
    print(json.dumps([hit.to_dict() for hit in hits], ensure_ascii=False, indent=2))
    return 0 if hits else 1
