"""imgl-related intent handlers."""

from __future__ import annotations

from uri2vql.nlp2uri_extractors import extract_click_target, extract_type_parts
from uri2vql.nlp2uri_types import IntentContext, IntentHandler, ResolvedVqlUri
from uri2vql.uri import (
    uri_for_imgl_click,
    uri_for_imgl_list,
    uri_for_imgl_type,
    uri_for_window_imgl,
)


def _match_imgl_list(ctx: IntentContext) -> bool:
    return ctx.has_list and any(
        h in ctx.normalized for h in ("element", "interaktyw", "imgl", "layout", "ekran")
    )


def _resolve_imgl_list(ctx: IntentContext) -> ResolvedVqlUri:
    return ResolvedVqlUri(
        uri=uri_for_imgl_list(file=ctx.file, image=ctx.imgl_image),
        confidence=0.91,
        match_reason="imgl:list",
    )


def _match_imgl_click(ctx: IntentContext) -> bool:
    return ctx.has_click


def _resolve_imgl_click(ctx: IntentContext) -> ResolvedVqlUri:
    target = extract_click_target(ctx.normalized)
    return ResolvedVqlUri(
        uri=uri_for_imgl_click(file=ctx.file, image=ctx.imgl_image, text=target),
        confidence=0.9 if target else 0.7,
        match_reason="imgl:click",
    )


def _match_imgl_type(ctx: IntentContext) -> bool:
    if not ctx.has_type:
        return False
    value, _ = extract_type_parts(ctx.normalized)
    return bool(value)


def _resolve_imgl_type(ctx: IntentContext) -> ResolvedVqlUri:
    value, field = extract_type_parts(ctx.normalized)
    return ResolvedVqlUri(
        uri=uri_for_imgl_type(file=ctx.file, image=ctx.imgl_image, value=value, label=field),
        confidence=0.89 if field else 0.72,
        match_reason="imgl:type",
    )


def _match_imgl_analyze(ctx: IntentContext) -> bool:
    return any(
        h in ctx.normalized
        for h in ("imgl", "layout", "ui", "interfejs", "przycisk", "button", "input", "pole")
    )


def _resolve_imgl_analyze(ctx: IntentContext) -> ResolvedVqlUri:
    return ResolvedVqlUri(
        uri=uri_for_window_imgl(file=ctx.file, image=ctx.imgl_image),
        confidence=0.78,
        match_reason="imgl:analyze",
    )


IMGL_HANDLERS: list[IntentHandler] = [
    IntentHandler(name="imgl:list", match=_match_imgl_list, resolve=_resolve_imgl_list),
    IntentHandler(name="imgl:click", match=_match_imgl_click, resolve=_resolve_imgl_click),
    IntentHandler(name="imgl:type", match=_match_imgl_type, resolve=_resolve_imgl_type),
    IntentHandler(name="imgl:analyze", match=_match_imgl_analyze, resolve=_resolve_imgl_analyze),
]
