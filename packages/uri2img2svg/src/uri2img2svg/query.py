"""Query images via img2svg:// URIs."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from uri2img2svg.uri import parse_img2svg_uri


@dataclass
class QueryResult:
    ok: bool
    uri: str
    selector: str
    path: str
    data: Any = None
    rendered: str = ""
    error: str | None = None
    keys: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "uri": self.uri,
            "selector": self.selector,
            "path": self.path,
            "data": self.data,
            "rendered": self.rendered,
            "keys": self.keys,
            "error": self.error,
        }


def query_uri(uri: str) -> QueryResult:
    try:
        parsed = parse_img2svg_uri(uri)
        if not parsed.path:
            return QueryResult(
                ok=False,
                uri=uri,
                selector=parsed.selector,
                path="",
                error="missing path= query parameter",
            )
        if not Path(parsed.path).expanduser().is_file():
            return QueryResult(
                ok=False,
                uri=uri,
                selector=parsed.selector,
                path=parsed.path,
                error=f"image not found: {parsed.path}",
            )

        if parsed.selector in {"vectorize", "trace", ""}:
            from img2svg.trace import trace_contours_opencv, trace_image_regions

            if parsed.method == "contours":
                payload = trace_contours_opencv(parsed.path)
            else:
                payload = trace_image_regions(parsed.path, grid=parsed.grid)
            if not payload.get("ok"):
                return QueryResult(
                    ok=False,
                    uri=uri,
                    selector=parsed.selector,
                    path=parsed.path,
                    error=payload.get("error", "trace failed"),
                )
            return QueryResult(
                ok=True,
                uri=uri,
                selector=parsed.selector,
                path=parsed.path,
                data=payload,
                rendered=json.dumps(payload, ensure_ascii=False, indent=2),
                keys=["region_count", "path_count", "method", "width", "height"],
            )

        if parsed.selector == "svg":
            from img2svg.svg_emit import image_to_svg

            out = parsed.out or None
            payload = image_to_svg(
                parsed.path,
                out_path=out,
                grid=parsed.grid,
                method=parsed.method,
            )
            if not payload.get("ok"):
                return QueryResult(
                    ok=False,
                    uri=uri,
                    selector=parsed.selector,
                    path=parsed.path,
                    error=payload.get("error", "svg failed"),
                )
            return QueryResult(
                ok=True,
                uri=uri,
                selector=parsed.selector,
                path=parsed.path,
                data=payload,
                rendered=json.dumps(payload, ensure_ascii=False, indent=2),
            )

        if parsed.selector == "vql":
            from img2svg.to_vql import image_to_vql

            out = parsed.out or None
            payload = image_to_vql(
                parsed.path,
                out_program=out,
                grid=parsed.grid,
                method=parsed.method,
            )
            if not payload.get("ok"):
                return QueryResult(
                    ok=False,
                    uri=uri,
                    selector=parsed.selector,
                    path=parsed.path,
                    error=payload.get("error", "vql failed"),
                )
            return QueryResult(
                ok=True,
                uri=uri,
                selector=parsed.selector,
                path=parsed.path,
                data=payload,
                rendered=json.dumps(payload, ensure_ascii=False, indent=2),
            )

        return QueryResult(
            ok=False,
            uri=uri,
            selector=parsed.selector,
            path=parsed.path,
            error=f"unknown selector: {parsed.selector}",
        )
    except Exception as exc:
        return QueryResult(ok=False, uri=uri, selector="", path="", error=str(exc))
