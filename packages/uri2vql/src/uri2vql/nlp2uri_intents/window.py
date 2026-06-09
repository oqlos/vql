"""window/* intent handlers."""

from __future__ import annotations

from uri2vql.nlp2uri_types import IntentContext, IntentHandler, ResolvedVqlUri
from uri2vql.uri import (
    uri_for_window_analyze,
    uri_for_window_compare,
    uri_for_window_diagnose,
    uri_for_window_refresh,
    uri_for_window_summary,
)


def _match_window_summary(ctx: IntentContext) -> bool:
    return ctx.has_describe and ctx.has_vql


def _resolve_window_summary(ctx: IntentContext) -> ResolvedVqlUri:
    return ResolvedVqlUri(
        uri=uri_for_window_summary(file=ctx.file),
        confidence=0.94,
        match_reason="window:summary",
    )


def _match_window_refresh(ctx: IntentContext) -> bool:
    return ctx.has_refresh and ctx.has_vql


def _resolve_window_refresh(ctx: IntentContext) -> ResolvedVqlUri:
    return ResolvedVqlUri(
        uri=uri_for_window_refresh(file=ctx.file, image=ctx.image or ""),
        confidence=0.93,
        match_reason="window:refresh",
    )


def _match_window_compare(ctx: IntentContext) -> bool:
    return (ctx.has_compare or ctx.has_unchanged) and ctx.has_vql


def _resolve_window_compare(ctx: IntentContext) -> ResolvedVqlUri:
    return ResolvedVqlUri(
        uri=uri_for_window_compare(file=ctx.file, image=ctx.image or ""),
        confidence=0.92 if ctx.has_compare else 0.88,
        match_reason="window:compare",
    )


def _match_window_diagnose(ctx: IntentContext) -> bool:
    return ctx.has_diagnose and ctx.has_vql


def _resolve_window_diagnose(ctx: IntentContext) -> ResolvedVqlUri:
    return ResolvedVqlUri(
        uri=uri_for_window_diagnose(file=ctx.file, image=ctx.image or ""),
        confidence=0.9,
        match_reason="window:diagnose",
    )


def _match_window_analyze_vql(ctx: IntentContext) -> bool:
    return ctx.has_capture and ctx.has_vql


def _resolve_window_analyze_vql(ctx: IntentContext) -> ResolvedVqlUri:
    return ResolvedVqlUri(
        uri=uri_for_window_analyze(
            file=ctx.file,
            monitor=ctx.monitor,
            grid=ctx.grid,
            image=ctx.image or "",
        ),
        confidence=0.92,
        match_reason="window:analyze+vql",
    )


def _match_window_analyze(ctx: IntentContext) -> bool:
    return (
        any(h in ctx.normalized for h in ("analyze", "adopt", "adoptuj"))
        and "window" in ctx.normalized
    )


def _resolve_window_analyze(ctx: IntentContext) -> ResolvedVqlUri:
    return ResolvedVqlUri(
        uri=uri_for_window_analyze(
            file=ctx.file,
            monitor=ctx.monitor,
            grid=ctx.grid,
            image=ctx.image or "",
        ),
        confidence=0.86,
        match_reason="window:analyze",
    )


WINDOW_HANDLERS: list[IntentHandler] = [
    IntentHandler(name="window:summary", match=_match_window_summary, resolve=_resolve_window_summary),
    IntentHandler(name="window:refresh", match=_match_window_refresh, resolve=_resolve_window_refresh),
    IntentHandler(name="window:compare", match=_match_window_compare, resolve=_resolve_window_compare),
    IntentHandler(name="window:diagnose", match=_match_window_diagnose, resolve=_resolve_window_diagnose),
    IntentHandler(name="window:analyze+vql", match=_match_window_analyze_vql, resolve=_resolve_window_analyze_vql),
    IntentHandler(name="window:analyze", match=_match_window_analyze, resolve=_resolve_window_analyze),
]
