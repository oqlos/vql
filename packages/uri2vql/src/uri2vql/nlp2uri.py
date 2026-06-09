"""NL hints → vql:// URI (for nlp2uri resolve layer)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from uri2vql.uri import (
    uri_for_imgl_click,
    uri_for_imgl_list,
    uri_for_imgl_type,
    uri_for_objects,
    uri_for_program,
    uri_for_scene,
    uri_for_window_analyze,
    uri_for_window_compare,
    uri_for_window_diagnose,
    uri_for_window_imgl,
    uri_for_window_refresh,
    uri_for_window_summary,
)


@dataclass(frozen=True)
class ResolvedVqlUri:
    uri: str
    confidence: float
    match_reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "uri": self.uri,
            "confidence": self.confidence,
            "match_reason": self.match_reason,
        }


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

    out_file = file or "app.vql.json"
    hits: list[ResolvedVqlUri] = []
    has_vql = any(h in normalized for h in ("vql", "vector", "adopt", "adoptuj"))
    has_describe = any(
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
    )
    has_capture = any(
        h in normalized
        for h in (
            "zrzut",
            "screenshot",
            "capture",
            "przechwyć",
            "przechwyc",
        )
    )
    has_click = any(
        h in normalized
        for h in ("kliknij", "click", "naciśnij", "nacisnij", "press", "tap")
    )
    has_type = any(
        h in normalized
        for h in ("wpisz", "type", "wprowadź", "wprowadz", "enter")
    )
    has_list = any(
        h in normalized
        for h in ("lista", "list", "elementy", "elements", "opcje", "options", "menu")
    )
    has_unchanged = any(
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
    )
    has_compare = any(
        h in normalized
        for h in ("porównaj", "porownaj", "compare", "fingerprint", "hash", "podobny")
    )
    has_diagnose = any(
        h in normalized
        for h in ("diagnose", "diagnoza", "diagnozuj", "llm", "miniatur", "thumbnail")
    )
    has_refresh = any(
        h in normalized
        for h in ("odśwież", "odswiez", "refresh", "metadata", "aktualizuj")
    )
    imgl_image = image or ""

    if has_list and any(h in normalized for h in ("element", "interaktyw", "imgl", "layout", "ekran")):
        hits.append(
            ResolvedVqlUri(
                uri=uri_for_imgl_list(file=out_file, image=imgl_image),
                confidence=0.91,
                match_reason="imgl:list",
            ),
        )

    if has_click:
        target = _extract_click_target(normalized)
        hits.append(
            ResolvedVqlUri(
                uri=uri_for_imgl_click(
                    file=out_file,
                    image=imgl_image,
                    text=target,
                ),
                confidence=0.9 if target else 0.7,
                match_reason="imgl:click",
            ),
        )

    if has_type:
        value, field = _extract_type_parts(normalized)
        if value:
            hits.append(
                ResolvedVqlUri(
                    uri=uri_for_imgl_type(
                        file=out_file,
                        image=imgl_image,
                        value=value,
                        label=field,
                    ),
                    confidence=0.89 if field else 0.72,
                    match_reason="imgl:type",
                ),
            )

    if any(h in normalized for h in ("imgl", "layout", "ui", "interfejs", "przycisk", "button", "input", "pole")):
        hits.append(
            ResolvedVqlUri(
                uri=uri_for_window_imgl(file=out_file, image=imgl_image),
                confidence=0.78,
                match_reason="imgl:analyze",
            ),
        )

    if has_describe and has_vql:
        hits.append(
            ResolvedVqlUri(
                uri=uri_for_window_summary(file=out_file),
                confidence=0.94,
                match_reason="window:summary",
            ),
        )

    if has_refresh and has_vql:
        hits.append(
            ResolvedVqlUri(
                uri=uri_for_window_refresh(file=out_file, image=image or ""),
                confidence=0.93,
                match_reason="window:refresh",
            ),
        )

    if (has_compare or has_unchanged) and has_vql:
        hits.append(
            ResolvedVqlUri(
                uri=uri_for_window_compare(file=out_file, image=image or ""),
                confidence=0.92 if has_compare else 0.88,
                match_reason="window:compare",
            ),
        )

    if has_diagnose and has_vql:
        hits.append(
            ResolvedVqlUri(
                uri=uri_for_window_diagnose(file=out_file, image=image or ""),
                confidence=0.9,
                match_reason="window:diagnose",
            ),
        )

    if has_capture and has_vql:
        hits.append(
            ResolvedVqlUri(
                uri=uri_for_window_analyze(
                    file=out_file,
                    monitor=monitor,
                    grid=grid,
                    image=image or "",
                ),
                confidence=0.92,
                match_reason="window:analyze+vql",
            ),
        )

    if any(h in normalized for h in ("analyze", "adopt", "adoptuj")) and "window" in normalized:
        hits.append(
            ResolvedVqlUri(
                uri=uri_for_window_analyze(
                    file=out_file,
                    monitor=monitor,
                    grid=grid,
                    image=image or "",
                ),
                confidence=0.86,
                match_reason="window:analyze",
            ),
        )

    if any(h in normalized for h in ("obiekty", "objects", "elementy", "elements", "cells", "komórki")):
        hits.append(
            ResolvedVqlUri(
                uri=uri_for_objects(file=out_file),
                confidence=0.84,
                match_reason="objects",
            ),
        )

    if any(h in normalized for h in ("scena", "scene", "layout", "układ", "uklad")):
        hits.append(
            ResolvedVqlUri(
                uri=uri_for_scene(file=out_file),
                confidence=0.82,
                match_reason="scene",
            ),
        )

    if any(
        h in normalized
        for h in ("program", "manifest", "pokaż program", "pokaz program", "show program")
    ):
        hits.append(
            ResolvedVqlUri(
                uri=uri_for_program(file=out_file),
                confidence=0.8,
                match_reason="program",
            ),
        )

    if any(h in normalized for h in ("vql", "vector", "narysuj", "render", "validate", "wygeneruj")):
        hits.append(
            ResolvedVqlUri(
                uri=uri_for_program(file=out_file),
                confidence=0.65,
                match_reason="vql:generic",
            ),
        )

    seen: set[str] = set()
    unique: list[ResolvedVqlUri] = []
    for hit in sorted(hits, key=lambda item: item.confidence, reverse=True):
        if hit.uri in seen:
            continue
        seen.add(hit.uri)
        unique.append(hit)
    return unique


def _extract_click_target(normalized: str) -> str:
    for prefix in ("kliknij ", "click ", "naciśnij ", "nacisnij ", "press ", "tap "):
        if prefix in normalized:
            return normalized.split(prefix, 1)[1].strip().strip('"\'')
    return ""


def _extract_type_parts(normalized: str) -> tuple[str, str]:
    for prefix in ("wpisz ", "type ", "wprowadź ", "wprowadz ", "enter "):
        if prefix not in normalized:
            continue
        rest = normalized.split(prefix, 1)[1].strip()
        for sep in (" w ", " in ", " do ", " into ", " pole ", " field "):
            if sep in rest:
                value, field = rest.split(sep, 1)
                return value.strip().strip('"\''), field.strip()
        return rest.strip().strip('"\''), ""
    return "", ""


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
