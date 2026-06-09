"""Compile vql:// to OS actions (nlp2uri integration)."""

from __future__ import annotations

import shutil
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from uri2vql.uri import is_vql_uri


def _dsl_from_uri(uri: str) -> str | None:
    parsed = urlparse(uri)
    if (parsed.netloc + parsed.path).strip("/") != "dsl":
        return None
    line = (parse_qs(parsed.query).get("line") or [""])[0]
    return unquote(line) or None


def compile_vql_uri(uri: str, host: Any, *, dsl: str | None = None) -> list[Any]:
    """Return OSAction list that invokes uri2vql or dsl2vql."""
    try:
        from nlp2uri.models import OSAction
    except ImportError as exc:
        raise RuntimeError("compile_vql_uri requires nlp2uri") from exc

    dsl_line = dsl or _dsl_from_uri(uri)
    if dsl_line:
        runner = shutil.which("dsl2vql") or "dsl2vql"
        return [OSAction(host, runner, ["-c", dsl_line, "--json"])]

    if not is_vql_uri(uri):
        raise ValueError(f"not a vql uri: {uri}")

    runner = shutil.which("uri2vql") or "uri2vql"
    return [OSAction(host, runner, ["run", "--uri", uri])]
