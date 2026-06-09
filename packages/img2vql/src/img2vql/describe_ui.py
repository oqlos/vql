"""Natural-language descriptions of detected UI layout."""

from __future__ import annotations

from typing import Any


_ROLE_PL = {
    "window": "okno",
    "panel": "panel",
    "button": "przycisk",
    "icon_button": "przycisk ikony",
    "titlebar": "pasek tytułu",
    "toolbar": "pasek narzędzi",
}

_ROLE_EN = {
    "window": "window",
    "panel": "panel",
    "button": "button",
    "icon_button": "icon button",
    "titlebar": "title bar",
    "toolbar": "toolbar",
}

_LOC_PL = {
    "top": "u góry",
    "bottom": "na dole",
    "left": "po lewej",
    "right": "po prawej",
    "center": "na środku",
    "top-left": "u góry po lewej",
    "top-right": "u góry po prawej",
    "bottom-left": "na dole po lewej",
    "bottom-right": "na dole po prawej",
    "middle-left": "po lewej (środek)",
    "middle-right": "po prawej (środek)",
    "middle-center": "na środku",
}

_LOC_EN = {
    "top": "at the top",
    "bottom": "at the bottom",
    "left": "on the left",
    "right": "on the right",
    "center": "in the center",
    "top-left": "top-left",
    "top-right": "top-right",
    "bottom-left": "bottom-left",
    "bottom-right": "bottom-right",
    "middle-left": "middle-left",
    "middle-right": "middle-right",
    "middle-center": "center",
}


def _role_name(role: str, locale: str) -> str:
    table = _ROLE_PL if locale.startswith("pl") else _ROLE_EN
    return table.get(role, role)


def _loc_name(loc: str, locale: str) -> str:
    table = _LOC_PL if locale.startswith("pl") else _LOC_EN
    return table.get(loc, loc)


def describe_ui_layout(
    detection: dict[str, Any],
    *,
    locale: str = "pl",
    image_width: int | None = None,
    image_height: int | None = None,
) -> str:
    """Summarize detected UI elements in natural language."""
    if not detection.get("ok"):
        return detection.get("error", "detection failed")

    loc = (locale or "pl").strip().lower()
    w = image_width or detection.get("width", 0)
    h = image_height or detection.get("height", 0)
    elements = detection.get("elements", [])
    if not elements:
        if loc.startswith("pl"):
            return f"Zrzut {w}×{h} px — nie wykryto wyraźnych elementów UI."
        return f"Screenshot {w}×{h} px — no distinct UI elements detected."

    lines: list[str] = []
    if loc.startswith("pl"):
        lines.append(
            f"Zrzut {w}×{h} px — wykryto {len(elements)} elementów UI "
            f"({', '.join(f'{k}={v}' for k, v in sorted(detection.get('by_role', {}).items()))})."
        )
    else:
        lines.append(
            f"Screenshot {w}×{h} px — {len(elements)} UI elements "
            f"({', '.join(f'{k}={v}' for k, v in sorted(detection.get('by_role', {}).items()))})."
        )

    for el in elements[:12]:
        role = _role_name(el.get("role", ""), loc)
        location = _loc_name(el.get("location", ""), loc)
        bbox = el.get("bbox", [0, 0, 0, 0])
        x0, y0, x1, y1 = bbox[:4]
        bw, bh = x1 - x0, y1 - y0
        conf = el.get("confidence", 0)
        if loc.startswith("pl"):
            lines.append(
                f"- {role} {location}: ({x0},{y0})–({x1},{y1}), {bw}×{bh} px, kolor {el.get('color', '?')}, pewność {conf:.0%}"
            )
        else:
            lines.append(
                f"- {role} {location}: ({x0},{y0})–({x1},{y1}), {bw}×{bh} px, color {el.get('color', '?')}, confidence {conf:.0%}"
            )

    if len(elements) > 12:
        if loc.startswith("pl"):
            lines.append(f"- … i {len(elements) - 12} więcej")
        else:
            lines.append(f"- … and {len(elements) - 12} more")

    return "\n".join(lines)
