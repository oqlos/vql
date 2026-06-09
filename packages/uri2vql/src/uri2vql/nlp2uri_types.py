"""Types for NL prompt → vql:// URI resolution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


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


@dataclass(frozen=True)
class IntentContext:
    normalized: str
    file: str
    monitor: int
    grid: int
    image: str | None
    imgl_image: str
    has_vql: bool
    has_describe: bool
    has_capture: bool
    has_click: bool
    has_type: bool
    has_list: bool
    has_unchanged: bool
    has_compare: bool
    has_diagnose: bool
    has_refresh: bool


@dataclass(frozen=True)
class IntentHandler:
    name: str
    match: Callable[[IntentContext], bool]
    resolve: Callable[[IntentContext], ResolvedVqlUri | None]
