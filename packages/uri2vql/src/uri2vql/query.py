"""Query VQL programs via vql:// URIs."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from uri2vql.uri import parse_vql_uri


@dataclass
class QueryResult:
    ok: bool
    uri: str
    selector: str
    file: str
    data: Any = None
    rendered: str = ""
    format: str = "json"
    error: str | None = None
    keys: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "uri": self.uri,
            "selector": self.selector,
            "file": self.file,
            "data": self.data,
            "rendered": self.rendered,
            "format": self.format,
            "keys": self.keys,
            "error": self.error,
        }


def _load_program(path: str):
    from vql.schema.program import VQLProgram

    data = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    return VQLProgram.from_dict(data)


def query_uri(uri: str, *, file: str | None = None, fmt: str = "json") -> QueryResult:
    try:
        parsed = parse_vql_uri(uri, default_file=file or "app.vql.json")
        program = _load_program(parsed.file)
        data = program.to_dict()

        if parsed.selector in {"program", ""}:
            payload = data
        elif parsed.selector == "scene":
            payload = data.get("scene", {})
        elif parsed.selector == "objects":
            payload = [
                obj.to_dict()
                for layer in program.scene.layers
                for obj in layer.objects
            ]
        elif parsed.selector.startswith("object/"):
            obj_id = parsed.selector.split("/", 1)[1]
            payload = next(
                (obj.to_dict() for obj in program.scene.iter_objects() if obj.id == obj_id),
                None,
            )
            if payload is None:
                return QueryResult(
                    ok=False,
                    uri=uri,
                    selector=parsed.selector,
                    file=parsed.file,
                    error=f"object not found: {obj_id}",
                )
        else:
            payload = data

        rendered = json.dumps(payload, ensure_ascii=False, indent=2)
        return QueryResult(
            ok=True,
            uri=uri,
            selector=parsed.selector,
            file=parsed.file,
            data=payload,
            rendered=rendered,
            format=fmt,
            keys=list(payload.keys()) if isinstance(payload, dict) else [],
        )
    except Exception as exc:
        return QueryResult(ok=False, uri=uri, selector="", file=file or "", error=str(exc))
