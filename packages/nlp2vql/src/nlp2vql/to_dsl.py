"""NL → VQL control DSL line (no side effects)."""

from __future__ import annotations

import re


def _intent(prompt: str) -> str:
    text = prompt.lower()
    if any(w in text for w in ("validate", "waliduj", "sprawdź", "sprawdz")):
        return "validate"
    if any(w in text for w in ("render", "wyrenderuj", "svg", "png", "eksportuj")):
        return "render"
    if any(w in text for w in ("generate", "wygeneruj", "stwórz", "stworz", "narysuj", "draw")):
        return "generate"
    if any(w in text for w in ("compile", "skompiluj", "parse", "parsuj")):
        return "compile"
    if any(w in text for w in ("query", "pokaż", "pokaz", "read", "show", "get")):
        return "query"
    return "generate"


def nl_to_dsl_line(prompt: str, *, file: str | None = None) -> str:
    intent = _intent(prompt)
    default = file or "app.vql.json"
    quoted = f'"{prompt}"' if " " in prompt else prompt

    if intent == "validate":
        return f"VALIDATE {default}"
    if intent == "render":
        return f"RENDER {default}"
    if intent == "compile":
        return f"COMPILE {quoted}"
    if intent == "query":
        return f'QUERY vql://program?file={default}'
    # generate
    out_flag = f" OUT {default}" if file else ""
    return f"GENERATE {quoted}{out_flag}"


def to_dsl(prompt: str, *, file: str | None = None) -> str:
    return nl_to_dsl_line(prompt, file=file)
