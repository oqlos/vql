"""Read-only query handlers for VQL control DSL."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dsl2vql.result import DslResult


def _load_program(path: str):
    from vql.schema.program import VQLProgram

    data = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    return VQLProgram.from_dict(data)


def handle_query(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from uri2vql.query import query_uri

    uri = cmd.get("target", "")
    file_param = cmd.get("file") or default_file
    fmt = (cmd.get("format") or "json").lower()
    result = query_uri(uri, file=file_param, fmt=fmt)
    return DslResult(
        ok=result.ok,
        command=line,
        action="query",
        output=result.rendered or json.dumps(result.data, ensure_ascii=False, indent=2),
        data=result.to_dict(),
        error=result.error,
    )


def handle_validate(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from vql import validate_program

    path = cmd.get("path") or default_file or "app.vql.json"
    try:
        program = _load_program(path)
        structural = program.validate()
        report = validate_program(program)
        ok = not structural and report.passed
        payload = {
            "ok": ok,
            "path": path,
            "structural_errors": structural,
            "report": report.to_dict(),
            "object_count": program.object_count(),
        }
        return DslResult(
            ok=ok,
            command=line,
            action="validate",
            output=json.dumps(payload, ensure_ascii=False, indent=2),
            data=payload,
            error=None if ok else "; ".join(structural + report.issues),
        )
    except Exception as exc:
        return DslResult(ok=False, command=line, action="validate", error=str(exc))


def handle_render(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from vql import render_to_png, render_to_svg

    path = cmd.get("path") or default_file or "app.vql.json"
    fmt = (cmd.get("format") or "svg").lower()
    out = cmd.get("out")
    try:
        program = _load_program(path)
        if fmt == "png":
            if not out:
                return DslResult(ok=False, command=line, action="render", error="RENDER png requires OUT <path>")
            output_path = render_to_png(program, out)
            return DslResult(
                ok=True,
                command=line,
                action="render",
                output=output_path,
                data={"path": path, "out": output_path, "format": "png"},
            )
        svg = render_to_svg(program)
        if out:
            Path(out).expanduser().write_text(svg, encoding="utf-8")
        return DslResult(
            ok=True,
            command=line,
            action="render",
            output=svg if not out else out,
            data={"path": path, "format": "svg", "bytes": len(svg)},
        )
    except Exception as exc:
        return DslResult(ok=False, command=line, action="render", error=str(exc))


def handle_resolve(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from nlp2vql.to_dsl import nl_to_dsl_line

    prompt = cmd.get("text", "")
    dsl_line = nl_to_dsl_line(prompt, file=cmd.get("file") or default_file)
    return DslResult(
        ok=bool(dsl_line),
        command=line,
        action="resolve",
        output=dsl_line,
        data={"dsl": dsl_line, "text": prompt},
        error=None if dsl_line else "could not resolve NL to DSL",
    )
