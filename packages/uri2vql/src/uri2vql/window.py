"""vql://window/... URI handlers for desktop screenshot analysis."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import parse_qs, urlparse

from uri2vql.query import QueryResult, query_uri
from uri2vql.window_analyze import WindowAnalyzeResult, analyze_window_uri
from uri2vql.window_compare import compare_window_image
from uri2vql.window_diagnose import diagnose_window_image
from uri2vql.window_handlers import WINDOW_HANDLERS
from uri2vql.window_metadata import refresh_window_metadata
from uri2vql.window_utils import (
    diagnose_fallback,
    normalize_locale,
    resolve_image_param,
    resolve_window_image,
)

# Backward-compatible private aliases (used by cli.py, mcp2vql/server.py).
_resolve_image_param = resolve_image_param
_normalize_locale = normalize_locale
_diagnose_fallback = diagnose_fallback
_resolve_window_image = resolve_window_image

__all__ = [
    "WindowAnalyzeResult",
    "analyze_window_uri",
    "compare_window_image",
    "diagnose_window_image",
    "query_window",
    "refresh_window_metadata",
]


def query_window(uri: str, *, file: str | None = None, fmt: str = "json") -> QueryResult:
    """Handle vql://window/* URIs (analyze + query adopted program)."""
    parsed = urlparse(uri)
    qs = parse_qs(parsed.query)
    out_file = (qs.get("file") or [""])[0] or file or "app.vql.json"
    selector = (parsed.netloc + parsed.path).strip("/")

    handler = WINDOW_HANDLERS.get(selector)
    if handler is not None:
        return handler(uri=uri, selector=selector, out_file=out_file, qs=qs, fmt=fmt)

    if Path(out_file).is_file():
        sub = uri.replace("vql://window/", "vql://").replace("vql://analyze/", "vql://")
        if sub.startswith("vql://objects") or sub.startswith("vql://scene") or sub.startswith("vql://program"):
            return query_uri(sub if "?" in sub else f"{sub}?file={out_file}", file=out_file, fmt=fmt)

    return QueryResult(ok=False, uri=uri, selector=selector, file=out_file, error=f"unknown window selector: {selector}")
