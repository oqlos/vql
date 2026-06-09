"""Parse and run VECTORIZE / TO_VQL / QUERY img2svg:// lines."""

from __future__ import annotations

import json
import shlex
from dataclasses import dataclass
from typing import Any


@dataclass
class DispatchResult:
    ok: bool
    verb: str
    output: str = ""
    data: dict[str, Any] | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "verb": self.verb,
            "output": self.output,
            "data": self.data,
            "error": self.error,
        }


def _parse_kv_args(tokens: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    i = 0
    while i < len(tokens):
        key = tokens[i].upper()
        if key in {"PATH", "OUT", "FILE", "GRID", "METHOD"} and i + 1 < len(tokens):
            out[key.lower()] = tokens[i + 1]
            i += 2
        else:
            i += 1
    return out


def dispatch(line: str) -> DispatchResult:
    """Dispatch a single DSL line for img2svg."""
    line = line.strip()
    if not line:
        return DispatchResult(ok=False, verb="", error="empty line")

    if line.upper().startswith("QUERY "):
        uri = line[6:].strip()
        from uri2img2svg.query import query_uri

        result = query_uri(uri)
        rendered = result.rendered or json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
        return DispatchResult(
            ok=result.ok,
            verb="QUERY",
            output=rendered,
            data=result.to_dict(),
            error=result.error,
        )

    tokens = shlex.split(line)
    verb = tokens[0].upper()
    args = _parse_kv_args(tokens[1:])

    if verb == "VECTORIZE":
        path = args.get("path", "")
        if not path:
            return DispatchResult(ok=False, verb=verb, error="PATH required")
        grid = int(args.get("grid", "24"))
        method = args.get("method", "regions")
        out = args.get("out", "")
        if out:
            from img2svg.svg_emit import image_to_svg

            payload = image_to_svg(path, out_path=out, grid=grid, method=method)
        else:
            from img2svg.trace import trace_contours_opencv, trace_image_regions

            payload = (
                trace_contours_opencv(path)
                if method == "contours"
                else trace_image_regions(path, grid=grid)
            )
        ok = bool(payload.get("ok"))
        return DispatchResult(
            ok=ok,
            verb=verb,
            output=json.dumps(payload, ensure_ascii=False, indent=2),
            data=payload,
            error=None if ok else payload.get("error"),
        )

    if verb in {"TO_VQL", "TOVQL"}:
        path = args.get("path", "")
        if not path:
            return DispatchResult(ok=False, verb=verb, error="PATH required")
        from img2svg.to_vql import image_to_vql

        payload = image_to_vql(
            path,
            out_program=args.get("out") or args.get("file") or None,
            grid=int(args.get("grid", "24")),
            method=args.get("method", "regions"),
        )
        ok = bool(payload.get("ok"))
        return DispatchResult(
            ok=ok,
            verb=verb,
            output=json.dumps(payload, ensure_ascii=False, indent=2),
            data=payload,
            error=None if ok else payload.get("error"),
        )

    return DispatchResult(ok=False, verb=verb, error=f"unknown verb: {verb}")
