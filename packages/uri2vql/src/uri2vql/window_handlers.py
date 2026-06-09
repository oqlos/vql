"""Per-selector handlers for vql://window/* URIs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from uri2vql.query import QueryResult
from uri2vql.window_analyze import analyze_window_uri
from uri2vql.window_compare import compare_window_image
from uri2vql.window_diagnose import diagnose_window_image
from uri2vql.window_imgl import query_window_imgl
from uri2vql.window_metadata import refresh_window_metadata
from uri2vql.window_utils import payload_result, query_bool, resolve_window_image


def handle_analyze(
    *,
    uri: str,
    selector: str,
    out_file: str,
    qs: dict[str, list[str]],
    fmt: str,
) -> QueryResult:
    monitor = int((qs.get("monitor") or ["1"])[0])
    grid = int((qs.get("grid") or ["12"])[0])
    image = (qs.get("image") or [""])[0] or None
    interactive_raw = (qs.get("interactive") or [""])[0].strip().lower()
    interactive = query_bool(interactive_raw) if interactive_raw else None
    result = analyze_window_uri(
        uri,
        file=out_file,
        monitor=monitor,
        grid=grid,
        image=image or None,
        interactive=interactive,
    )
    rendered = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    return QueryResult(
        ok=result.ok,
        uri=uri,
        selector=selector,
        file=out_file,
        data=result.to_dict(),
        rendered=rendered,
        format=fmt,
        error=result.error,
    )


def handle_detect(
    *,
    uri: str,
    selector: str,
    out_file: str,
    qs: dict[str, list[str]],
    fmt: str,
) -> QueryResult:
    image = (qs.get("image") or [""])[0] or None
    if not image or not Path(str(image)).is_file():
        return QueryResult(
            ok=False,
            uri=uri,
            selector=selector,
            file=out_file,
            error="image= query param required",
        )
    locale = (qs.get("locale") or ["pl"])[0]
    try:
        from img2vql.detect import detect_ui_elements
        from img2vql.describe_ui import describe_ui_layout

        payload = detect_ui_elements(image)
        if payload.get("ok"):
            payload["description"] = describe_ui_layout(payload, locale=locale)
    except ImportError:
        return QueryResult(
            ok=False,
            uri=uri,
            selector=selector,
            file=out_file,
            error="img2vql not installed: pip install -e packages/img2vql",
        )
    return payload_result(
        ok=bool(payload.get("ok")),
        uri=uri,
        selector=selector,
        out_file=out_file,
        payload=payload,
        fmt=fmt,
    )


def handle_adopt(
    *,
    uri: str,
    selector: str,
    out_file: str,
    qs: dict[str, list[str]],
    fmt: str,
) -> QueryResult:
    image = (qs.get("image") or [""])[0] or None
    if not image or not Path(str(image)).is_file():
        return QueryResult(
            ok=False,
            uri=uri,
            selector=selector,
            file=out_file,
            error="image= query param required",
        )
    locale = (qs.get("locale") or ["pl"])[0]
    grid = int((qs.get("grid") or ["12"])[0])
    with_grid = query_bool((qs.get("with_grid") or ["0"])[0])
    try:
        from img2vql.adopt import adopt_screenshot

        payload = adopt_screenshot(
            image,
            out_program=out_file,
            locale=locale,
            include_grid=with_grid,
            grid=grid,
        )
    except ImportError:
        return QueryResult(
            ok=False,
            uri=uri,
            selector=selector,
            file=out_file,
            error="img2vql not installed: pip install -e packages/img2vql",
        )
    return payload_result(
        ok=bool(payload.get("ok")),
        uri=uri,
        selector=selector,
        out_file=out_file,
        payload=payload,
        fmt=fmt,
    )


def handle_diagnose(
    *,
    uri: str,
    selector: str,
    out_file: str,
    qs: dict[str, list[str]],
    fmt: str,
) -> QueryResult:
    image = resolve_window_image(out_file, (qs.get("image") or [""])[0] or None)
    if not image:
        return QueryResult(
            ok=False,
            uri=uri,
            selector=selector,
            file=out_file,
            error="image missing; run analyze first or pass image= query param",
        )
    locale = (qs.get("locale") or ["pl"])[0]
    translate_mode = (qs.get("translate_mode") or ["auto"])[0]
    save_to_program = query_bool((qs.get("save") or [""])[0])
    payload = diagnose_window_image(
        image,
        vql_program=out_file if Path(out_file).is_file() else None,
        locale=locale,
        translate_mode=translate_mode,
        save_to_program=save_to_program,
    )
    return payload_result(
        ok=bool(payload.get("ok")),
        uri=uri,
        selector=selector,
        out_file=out_file,
        payload=payload,
        fmt=fmt,
    )


def handle_compare(
    *,
    uri: str,
    selector: str,
    out_file: str,
    qs: dict[str, list[str]],
    fmt: str,
) -> QueryResult:
    image = (qs.get("image") or [""])[0] or None
    if not image or not Path(str(image)).is_file():
        return QueryResult(
            ok=False,
            uri=uri,
            selector=selector,
            file=out_file,
            error="image= query param required",
        )
    if not Path(out_file).is_file():
        return QueryResult(
            ok=False,
            uri=uri,
            selector=selector,
            file=out_file,
            error="program file missing; run analyze first",
        )
    payload = compare_window_image(image, vql_program=out_file)
    return payload_result(
        ok=bool(payload.get("ok")),
        uri=uri,
        selector=selector,
        out_file=out_file,
        payload=payload,
        fmt=fmt,
    )


def handle_refresh(
    *,
    uri: str,
    selector: str,
    out_file: str,
    qs: dict[str, list[str]],
    fmt: str,
) -> QueryResult:
    image = resolve_window_image(out_file, (qs.get("image") or [""])[0] or None)
    if not image:
        return QueryResult(
            ok=False,
            uri=uri,
            selector=selector,
            file=out_file,
            error="image missing; pass image= or ensure program metadata.image exists",
        )
    if not Path(out_file).is_file():
        return QueryResult(
            ok=False,
            uri=uri,
            selector=selector,
            file=out_file,
            error="program file missing; run analyze first",
        )
    locale = (qs.get("locale") or ["pl"])[0]
    payload = refresh_window_metadata(image, vql_program=out_file, locale=locale)
    return payload_result(
        ok=bool(payload.get("ok")),
        uri=uri,
        selector=selector,
        out_file=out_file,
        payload=payload,
        fmt=fmt,
    )


def handle_summary(
    *,
    uri: str,
    selector: str,
    out_file: str,
    qs: dict[str, list[str]],
    fmt: str,
) -> QueryResult:
    if not Path(out_file).is_file():
        return QueryResult(
            ok=False,
            uri=uri,
            selector=selector,
            file=out_file,
            error="program file missing; run analyze first",
        )
    if query_bool((qs.get("live") or [""])[0]):
        image = resolve_window_image(out_file, (qs.get("image") or [""])[0] or None)
        if image:
            locale = (qs.get("locale") or ["pl"])[0]
            refresh_window_metadata(image, vql_program=out_file, locale=locale)
    prog = json.loads(Path(out_file).read_text(encoding="utf-8"))
    summary = {
        "scene": prog.get("scene", {}),
        "object_count": sum(len(layer.get("objects", [])) for layer in prog.get("scene", {}).get("layers", [])),
        "dominant_colors": prog.get("metadata", {}).get("dominant_colors", []),
        "fingerprint": prog.get("metadata", {}).get("fingerprint", {}),
        "special_hits": prog.get("metadata", {}).get("special_hits", {}),
        "scene_class": prog.get("metadata", {}).get("scene_class", ""),
        "llm_hint": prog.get("metadata", {}).get("llm_hint", {}),
        "similarity": prog.get("metadata", {}).get("similarity", {}),
        "diagnose_recommendation": prog.get("metadata", {}).get("diagnose_recommendation", ""),
        "diagnosed_at": prog.get("metadata", {}).get("diagnosed_at", ""),
        "window_title": prog.get("metadata", {}).get("capture", {}).get("window_title", ""),
        "image": prog.get("metadata", {}).get("image", ""),
        "analyzed_at": prog.get("metadata", {}).get("analyzed_at", ""),
    }
    return QueryResult(
        ok=True,
        uri=uri,
        selector=selector,
        file=out_file,
        data=summary,
        rendered=json.dumps(summary, ensure_ascii=False, indent=2),
        format=fmt,
    )


def handle_imgl(
    *,
    uri: str,
    selector: str,
    out_file: str,
    qs: dict[str, list[str]],
    fmt: str,
) -> QueryResult:
    return query_window_imgl(uri=uri, selector=selector, out_file=out_file, qs=qs, fmt=fmt)


Handler = Callable[..., QueryResult]

WINDOW_HANDLERS: dict[str, Handler] = {
    "window/analyze": handle_analyze,
    "analyze": handle_analyze,
    "window/detect": handle_detect,
    "detect": handle_detect,
    "window/adopt": handle_adopt,
    "adopt": handle_adopt,
    "window/imgl": handle_imgl,
    "imgl": handle_imgl,
    "window/diagnose": handle_diagnose,
    "diagnose": handle_diagnose,
    "window/compare": handle_compare,
    "compare": handle_compare,
    "window/refresh": handle_refresh,
    "refresh": handle_refresh,
    "window/summary": handle_summary,
    "summary": handle_summary,
}
