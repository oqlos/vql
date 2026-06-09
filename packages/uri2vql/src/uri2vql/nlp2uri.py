"""NL hints → vql:// URI (for nlp2uri resolve layer)."""

from __future__ import annotations

import re

from uri2vql.nlp2uri_intents import INTENT_HANDLERS
from uri2vql.nlp2uri_types import IntentContext, ResolvedVqlUri

# Re-export for backward compatibility.
__all__ = [
    "IntentContext",
    "ResolvedVqlUri",
    "best_uri",
    "nlp2uri",
    "resolve_prompt_to_vql_uri",
]


def build_intent_context(
    normalized: str,
    *,
    file: str,
    monitor: int,
    grid: int,
    image: str | None,
) -> IntentContext:
    return IntentContext(
        normalized=normalized,
        file=file,
        monitor=monitor,
        grid=grid,
        image=image,
        imgl_image=image or "",
        has_vql=any(h in normalized for h in ("vql", "vector", "adopt", "adoptuj")),
        has_describe=any(
            h in normalized
            for h in (
                "opisz",
                "opis",
                "describe",
                "summary",
                "podsumowanie",
                "overview",
                "przeanalizuj",
                "analizuj",
            )
        ),
        has_capture=any(
            h in normalized
            for h in (
                "zrzut",
                "screenshot",
                "capture",
                "przechwyć",
                "przechwyc",
            )
        ),
        has_click=any(
            h in normalized for h in ("kliknij", "click", "naciśnij", "nacisnij", "press", "tap")
        ),
        has_type=any(h in normalized for h in ("wpisz", "type", "wprowadź", "wprowadz", "enter")),
        has_list=any(
            h in normalized for h in ("lista", "list", "elementy", "elements", "opcje", "options", "menu")
        ),
        has_unchanged=any(
            h in normalized
            for h in (
                "bez zmian",
                "unchanged",
                "ten sam",
                "same screen",
                "identyczny",
                "nie zmieni",
                "nie zmienił",
            )
        ),
        has_compare=any(
            h in normalized for h in ("porównaj", "porownaj", "compare", "fingerprint", "hash", "podobny")
        ),
        has_diagnose=any(
            h in normalized
            for h in ("diagnose", "diagnoza", "diagnozuj", "llm", "miniatur", "thumbnail")
        ),
        has_refresh=any(
            h in normalized for h in ("odśwież", "odswiez", "refresh", "metadata", "aktualizuj")
        ),
    )


def dedupe_by_uri(hits: list[ResolvedVqlUri]) -> list[ResolvedVqlUri]:
    seen: set[str] = set()
    unique: list[ResolvedVqlUri] = []
    for hit in sorted(hits, key=lambda item: item.confidence, reverse=True):
        if hit.uri in seen:
            continue
        seen.add(hit.uri)
        unique.append(hit)
    return unique


def resolve_prompt_to_vql_uri(
    prompt: str,
    *,
    file: str | None = None,
    monitor: int = 1,
    grid: int = 12,
    image: str | None = None,
) -> list[ResolvedVqlUri]:
    normalized = re.sub(r"\s+", " ", prompt.lower().strip())
    if not normalized:
        return []

    ctx = build_intent_context(
        normalized,
        file=file or "app.vql.json",
        monitor=monitor,
        grid=grid,
        image=image,
    )
    hits = [handler.resolve(ctx) for handler in INTENT_HANDLERS if handler.match(ctx)]
    return dedupe_by_uri(hits)


def nlp2uri(
    prompt: str,
    *,
    file: str | None = None,
    monitor: int = 1,
    grid: int = 12,
    image: str | None = None,
) -> list[ResolvedVqlUri]:
    """Map natural language to ranked vql:// URIs."""
    return resolve_prompt_to_vql_uri(
        prompt,
        file=file,
        monitor=monitor,
        grid=grid,
        image=image,
    )


def best_uri(
    prompt: str,
    *,
    file: str | None = None,
    monitor: int = 1,
    grid: int = 12,
    image: str | None = None,
) -> ResolvedVqlUri | None:
    hits = nlp2uri(
        prompt,
        file=file,
        monitor=monitor,
        grid=grid,
        image=image,
    )
    return hits[0] if hits else None
