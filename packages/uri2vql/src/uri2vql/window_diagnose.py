"""Diagnose whether a capture should be sent to an LLM."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from uri2vql.window_utils import diagnose_fallback, normalize_locale


def diagnose_window_image(
    image: str | Path,
    *,
    vql_program: str | Path | None = None,
    locale: str = "pl",
    translate_mode: str = "auto",
    save_to_program: bool = False,
) -> dict[str, Any]:
    """Run img2vql diagnose or fall back to vql image_stats heuristics."""
    loc = normalize_locale(locale)
    try:
        from img2vql.diagnose import diagnose_for_vql

        return diagnose_for_vql(
            image,
            vql_program=vql_program,
            locale=loc,
            translate_mode=translate_mode,
            save_to_program=save_to_program,
        )
    except ImportError:
        payload = diagnose_fallback(image, vql_program=vql_program, locale=loc)
        payload["hint"] = "Install full diagnose: pip install -e ../../wronai/img2nl -e packages/img2vql"
        return payload
