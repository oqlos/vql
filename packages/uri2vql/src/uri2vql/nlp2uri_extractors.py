"""Extract click/type targets from normalized NL prompts."""

from __future__ import annotations


def extract_click_target(normalized: str) -> str:
    for prefix in ("kliknij ", "click ", "naciśnij ", "nacisnij ", "press ", "tap "):
        if prefix in normalized:
            return normalized.split(prefix, 1)[1].strip().strip('"\'')
    return ""


def extract_type_parts(normalized: str) -> tuple[str, str]:
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
