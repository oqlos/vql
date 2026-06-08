"""Write command handlers for VQL control DSL."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dsl2vql.result import DslResult


def _read_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).expanduser().read_text(encoding="utf-8"))


def handle_generate(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from vql import nl_to_program

    text = cmd.get("text", "")
    out = cmd.get("out") or default_file or "app.vql.json"
    try:
        program = nl_to_program(text)
        Path(out).expanduser().write_text(
            json.dumps(program.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return DslResult(
            ok=True,
            command=line,
            action="generate",
            output=out,
            data={"out": out, "object_count": program.object_count()},
        )
    except Exception as exc:
        return DslResult(ok=False, command=line, action="generate", error=str(exc))


def handle_compile(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from vql import nl_to_program

    text = cmd.get("text", "")
    width = float(cmd.get("width") or 1024)
    height = float(cmd.get("height") or 768)
    try:
        program = nl_to_program(text, width=width, height=height)
        payload = program.to_dict()
        return DslResult(
            ok=True,
            command=line,
            action="compile",
            output=json.dumps(payload, ensure_ascii=False, indent=2),
            data=payload,
        )
    except Exception as exc:
        return DslResult(ok=False, command=line, action="compile", error=str(exc))


def handle_patch(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from uri2vql.patch import patch_uri

    with_path = cmd.get("with_path")
    if not with_path:
        return DslResult(ok=False, command=line, action="patch", error="PATCH requires WITH <fragment-file>")
    content = Path(with_path).expanduser().read_text(encoding="utf-8")
    result = patch_uri(cmd.get("target", ""), content=content, file=cmd.get("file") or default_file)
    return DslResult(
        ok=result.ok,
        command=line,
        action="patch",
        output=json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
        data=result.to_dict(),
        error=result.error,
    )


def handle_export(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from vql import render_to_png, render_to_svg
    from vql.schema.program import VQLProgram

    path = cmd.get("path") or default_file or "app.vql.json"
    out = cmd.get("out")
    if not out:
        return DslResult(ok=False, command=line, action="export", error="EXPORT requires OUT <path>")
    fmt = (cmd.get("format") or "svg").lower()
    try:
        program = VQLProgram.from_dict(_read_json(path))
        if fmt == "png":
            output_path = render_to_png(program, out)
        else:
            svg = render_to_svg(program)
            Path(out).expanduser().write_text(svg, encoding="utf-8")
            output_path = out
        return DslResult(
            ok=True,
            command=line,
            action="export",
            output=output_path,
            data={"path": path, "out": output_path, "format": fmt},
        )
    except Exception as exc:
        return DslResult(ok=False, command=line, action="export", error=str(exc))


def handle_from_tokens(line: str, tokens: list[str], *, default_file: str | None) -> DslResult:
    from dsl2vql.grammar import parse_line

    cmd = parse_line(line) or {"verb": tokens[0].upper() if tokens else ""}
    verb = str(cmd.get("verb", "")).upper()

    if verb == "QUERY":
        from dsl2vql.handlers.query import handle_query
        return handle_query(cmd, line=line, default_file=default_file)
    if verb == "VALIDATE":
        from dsl2vql.handlers.query import handle_validate
        return handle_validate(cmd, line=line, default_file=default_file)
    if verb == "RENDER":
        from dsl2vql.handlers.query import handle_render
        return handle_render(cmd, line=line, default_file=default_file)
    if verb == "RESOLVE":
        from dsl2vql.handlers.query import handle_resolve
        return handle_resolve(cmd, line=line, default_file=default_file)
    if verb == "GENERATE":
        return handle_generate(cmd, line=line, default_file=default_file)
    if verb == "COMPILE":
        return handle_compile(cmd, line=line, default_file=default_file)
    if verb == "PATCH":
        return handle_patch(cmd, line=line, default_file=default_file)
    if verb == "EXPORT":
        return handle_export(cmd, line=line, default_file=default_file)
    return DslResult(ok=False, command=line, action=verb.lower(), error=f"unknown verb: {verb}")
