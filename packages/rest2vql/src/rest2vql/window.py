"""REST handlers for vql window/* operations."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class WindowImageBody(BaseModel):
    image: str = ""
    file: str = "app.vql.json"
    locale: str = "pl"
    grid: int = 12
    translate_mode: str = "auto"
    save: bool = False
    with_grid: bool = False
    live: bool = False
    interactive: bool | None = None


def window_detect(image: str, *, locale: str = "pl") -> dict[str, Any]:
    from img2vql.describe_ui import describe_ui_layout
    from img2vql.detect import detect_ui_elements

    payload = detect_ui_elements(image)
    if payload.get("ok"):
        payload["description"] = describe_ui_layout(payload, locale=locale)
    return payload


def window_compare(image: str, *, file: str) -> dict[str, Any]:
    from img2vql.fingerprint import compare_with_program

    payload = compare_with_program(image, file)
    payload["vql_program"] = file
    return payload


def window_refresh(image: str, *, file: str, locale: str = "pl") -> dict[str, Any]:
    from img2vql.metadata import refresh_program_metadata

    payload = refresh_program_metadata(file, image, locale=locale)
    payload["vql_program"] = file
    return payload


def window_diagnose(
    image: str,
    *,
    file: str = "",
    locale: str = "pl",
    translate_mode: str = "auto",
    save: bool = False,
) -> dict[str, Any]:
    from img2vql.diagnose import diagnose_for_vql

    return diagnose_for_vql(
        image,
        vql_program=file or None,
        locale=locale,
        translate_mode=translate_mode,
        save_to_program=save,
    )


def window_analyze(
    image: str,
    *,
    file: str = "app.vql.json",
    grid: int = 12,
    interactive: bool | None = None,
) -> dict[str, Any]:
    from vql.adopt.window import analyze_screenshot

    return analyze_screenshot(
        image,
        out_program=file,
        grid=grid,
        interactive=interactive,
    )


def window_adopt(
    image: str,
    *,
    file: str = "ui.vql.json",
    locale: str = "pl",
    with_grid: bool = False,
    grid: int = 12,
) -> dict[str, Any]:
    from img2vql.adopt import adopt_screenshot

    return adopt_screenshot(
        image,
        out_program=file,
        locale=locale,
        include_grid=with_grid,
        grid=grid,
    )


def window_summary(
    *,
    file: str,
    image: str = "",
    live: bool = False,
    locale: str = "pl",
) -> dict[str, Any]:
    from pathlib import Path

    from uri2vql.window import query_window

    uri = f"vql://window/summary?file={file}"
    if live:
        uri += "&live=1"
    if image:
        uri += f"&image={image}"
    if locale:
        uri += f"&locale={locale}"
    result = query_window(uri, file=file)
    if not result.ok:
        return {"ok": False, "error": result.error or "summary failed"}
    return {"ok": True, "file": file, **(result.data or {})}
