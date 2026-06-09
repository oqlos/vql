"""program/scene/objects intent handlers."""

from __future__ import annotations

from uri2vql.nlp2uri_types import IntentContext, IntentHandler, ResolvedVqlUri
from uri2vql.uri import uri_for_objects, uri_for_program, uri_for_scene


def _match_objects(ctx: IntentContext) -> bool:
    return any(
        h in ctx.normalized for h in ("obiekty", "objects", "elementy", "elements", "cells", "komórki")
    )


def _resolve_objects(ctx: IntentContext) -> ResolvedVqlUri:
    return ResolvedVqlUri(
        uri=uri_for_objects(file=ctx.file),
        confidence=0.84,
        match_reason="objects",
    )


def _match_scene(ctx: IntentContext) -> bool:
    return any(h in ctx.normalized for h in ("scena", "scene", "layout", "układ", "uklad"))


def _resolve_scene(ctx: IntentContext) -> ResolvedVqlUri:
    return ResolvedVqlUri(
        uri=uri_for_scene(file=ctx.file),
        confidence=0.82,
        match_reason="scene",
    )


def _match_program(ctx: IntentContext) -> bool:
    return any(
        h in ctx.normalized
        for h in ("program", "manifest", "pokaż program", "pokaz program", "show program")
    )


def _resolve_program(ctx: IntentContext) -> ResolvedVqlUri:
    return ResolvedVqlUri(
        uri=uri_for_program(file=ctx.file),
        confidence=0.8,
        match_reason="program",
    )


def _match_vql_generic(ctx: IntentContext) -> bool:
    return any(h in ctx.normalized for h in ("vql", "vector", "narysuj", "render", "validate", "wygeneruj"))


def _resolve_vql_generic(ctx: IntentContext) -> ResolvedVqlUri:
    return ResolvedVqlUri(
        uri=uri_for_program(file=ctx.file),
        confidence=0.65,
        match_reason="vql:generic",
    )


PROGRAM_HANDLERS: list[IntentHandler] = [
    IntentHandler(name="objects", match=_match_objects, resolve=_resolve_objects),
    IntentHandler(name="scene", match=_match_scene, resolve=_resolve_scene),
    IntentHandler(name="program", match=_match_program, resolve=_resolve_program),
    IntentHandler(name="vql:generic", match=_match_vql_generic, resolve=_resolve_vql_generic),
]
