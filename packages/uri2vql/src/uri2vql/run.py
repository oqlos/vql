"""Execute vql:// URIs programmatically."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from uri2vql.uri import is_vql_uri, parse_vql_uri


@dataclass
class RunResult:
    ok: bool
    uri: str
    selector: str
    output: str = ""
    data: dict[str, Any] | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "uri": self.uri,
            "selector": self.selector,
            "output": self.output,
            "data": self.data,
            "error": self.error,
        }


def run_uri(uri: str, *, file: str | None = None) -> RunResult:
    """Dispatch a vql:// URI via dsl2vql QUERY handler."""
    if not is_vql_uri(uri):
        return RunResult(ok=False, uri=uri, selector="", error=f"not a vql uri: {uri}")

    parsed = parse_vql_uri(uri, default_file=file or "app.vql.json")
    try:
        from dsl2vql import dispatch

        line = f"QUERY {uri}"
        if file:
            line += f" FILE {file}"
        result = dispatch(line, default_file=file)
        data = result.data if isinstance(result.data, dict) else None
        return RunResult(
            ok=result.ok,
            uri=uri,
            selector=parsed.selector,
            output=result.output or "",
            data=data,
            error=result.error,
        )
    except Exception as exc:
        return RunResult(
            ok=False,
            uri=uri,
            selector=parsed.selector,
            error=str(exc),
        )


def run_uri_json(uri: str, *, file: str | None = None) -> str:
    return json.dumps(run_uri(uri, file=file).to_dict(), ensure_ascii=False, indent=2)
