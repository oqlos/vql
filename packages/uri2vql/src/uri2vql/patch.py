"""Patch VQL program files via vql:// URIs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from uri2vql.uri import parse_vql_uri


@dataclass
class PatchResult:
    ok: bool
    uri: str
    file: str
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "uri": self.uri, "file": self.file, "error": self.error}


def patch_uri(uri: str, *, content: str, file: str | None = None) -> PatchResult:
    try:
        parsed = parse_vql_uri(uri, default_file=file or "app.vql.json")
        path = Path(parsed.file).expanduser()
        base = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        patch = json.loads(content)
        if parsed.selector in {"program", ""}:
            merged = {**base, **patch}
        elif parsed.selector == "scene":
            merged = {**base, "scene": {**base.get("scene", {}), **patch}}
        else:
            merged = {**base, **patch}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
        return PatchResult(ok=True, uri=uri, file=str(path))
    except Exception as exc:
        return PatchResult(ok=False, uri=uri, file=file or "", error=str(exc))
