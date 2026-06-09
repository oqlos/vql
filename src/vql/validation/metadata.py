"""Validate VQLProgram.metadata extensions (imgl desktop automation)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema" / "program_metadata_imgl.json"


@lru_cache(maxsize=1)
def _load_imgl_metadata_schema() -> dict[str, Any]:
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_program_metadata(metadata: dict[str, Any] | None) -> list[str]:
    """
    Validate imgl-specific metadata keys when present.

    Uses jsonschema when installed; otherwise performs minimal structural checks.
    Empty metadata is valid (generic VQL programs).
    """
    if not metadata:
        return []

    issues: list[str] = []
    capture = metadata.get("capture")
    if capture is not None and not isinstance(capture, dict):
        issues.append("metadata.capture must be an object")

    window_os = metadata.get("window_os")
    if window_os is not None:
        if not isinstance(window_os, dict):
            issues.append("metadata.window_os must be an object")
        else:
            for key, value in window_os.items():
                if not isinstance(value, dict):
                    issues.append(f"metadata.window_os.{key} must be an object")

    if issues:
        return issues

    try:
        import jsonschema
    except ImportError:
        return []

    try:
        jsonschema.validate(instance=metadata, schema=_load_imgl_metadata_schema())
    except jsonschema.ValidationError as exc:
        path = ".".join(str(p) for p in exc.absolute_path) or "metadata"
        return [f"{path}: {exc.message}"]
    except Exception as exc:
        return [str(exc)]
    return []
