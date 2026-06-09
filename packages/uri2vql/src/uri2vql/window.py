"""vql://window/... URI handlers for desktop screenshot analysis."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from uri2vql.query import QueryResult, query_uri


def _resolve_image_param(image: str | None) -> tuple[str | None, str | None]:
    if not image:
        return None, "image= query param required"
    path = Path(image).expanduser()
    if path.is_file():
        return str(path.resolve()), None
    candidates = [path]
    if not path.is_absolute():
        candidates.append(Path.cwd() / path)
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate.resolve()), None
    return (
        None,
        f"image file not found: {image} (cwd={Path.cwd()}). "
        "Capture first: imgl capture -o screen.png",
    )


def _normalize_locale(locale: str) -> str:
    try:
        from img2nl.i18n import normalize_locale

        return normalize_locale(locale)
    except ImportError:
        loc = (locale or "pl").strip().lower()
        return "en" if loc.startswith("en") else "pl"


def _diagnose_fallback(
    image: str | Path,
    *,
    vql_program: str | Path | None = None,
    locale: str = "pl",
) -> dict[str, Any]:
    """Lightweight diagnose when img2vql/img2nl is not installed."""
    from vql.adopt.window import image_stats

    stats = image_stats(image)
    if not stats.get("ok"):
        return {"ok": False, "path": str(image), "error": stats.get("error", "image_stats failed")}

    unique = int(stats.get("unique_colors_sampled", 0))
    b_avg = int(stats.get("brightness_avg", 0))
    is_blank = bool(stats.get("is_blank"))

    loc = _normalize_locale(locale)
    w, h = stats.get("width"), stats.get("height")
    b_min, b_max = stats.get("brightness_min"), stats.get("brightness_max")

    try:
        from img2nl.i18n import t as i18n_t
    except ImportError:
        i18n_t = None

    if is_blank:
        recommendation = "skip_llm_blank_capture"
        send = False
        text = (
            i18n_t("diag_blank", loc, w=w, h=h)
            if i18n_t
            else f"Image {w}×{h} px looks blank/black."
        )
    elif unique >= 8 and b_avg >= 20:
        recommendation = "send_thumbnail_to_llm"
        send = True
        text = (
            i18n_t("diag_send_llm", loc, w=w, h=h, unique=unique, b_min=b_min, b_max=b_max)
            if i18n_t
            else f"Image {w}×{h} px, ~{unique} colors."
        )
    else:
        recommendation = "use_vql_grid_only"
        send = False
        text = (
            i18n_t("diag_grid_only", loc, w=w, h=h, unique=unique)
            if i18n_t
            else f"Image {w}×{h} px, ~{unique} colors."
        )

    out: dict[str, Any] = {
        "ok": True,
        "path": str(image),
        "text": text,
        "locale": loc,
        "recommendation": recommendation,
        "llm_hint": {
            "send_to_llm": send,
            "confidence": 0.6 if send else 0.4,
            "reasons": ["vql_image_stats_fallback"],
            "recommendation": "send" if send else "skip_or_use_thumbnail_only",
        },
        "image_stats": stats,
        "source": "vql-fallback",
        "vql_program": str(vql_program) if vql_program else "",
    }
    if vql_program and Path(vql_program).is_file():
        try:
            from vql.schema.program import VQLProgram

            data = json.loads(Path(vql_program).read_text(encoding="utf-8"))
            program = VQLProgram.from_dict(data)
            out["vql_object_count"] = program.object_count()
            out["vql_dominant_colors"] = program.metadata.get("dominant_colors", [])
        except Exception as exc:
            out["vql_error"] = str(exc)
    return out


def _resolve_window_image(out_file: str, image: str | None) -> str | None:
    if image and Path(str(image)).is_file():
        return str(image)
    prog_path = Path(out_file)
    if prog_path.is_file():
        try:
            prog = json.loads(prog_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        candidate = prog.get("metadata", {}).get("image") or prog.get("metadata", {}).get("capture", {}).get("path")
        if candidate and Path(str(candidate)).is_file():
            return str(candidate)
    return None


def refresh_window_metadata(
    image: str | Path,
    *,
    vql_program: str | Path,
    locale: str = "pl",
) -> dict[str, Any]:
    """Refresh img2nl metadata in program without rebuilding VQL layers."""
    try:
        from img2vql.metadata import refresh_program_metadata

        payload = refresh_program_metadata(vql_program, image, locale=locale)
    except ImportError:
        return {
            "ok": False,
            "error": "img2vql/img2nl not installed for metadata refresh",
        }
    payload["vql_program"] = str(vql_program)
    return payload


def compare_window_image(
    image: str | Path,
    *,
    vql_program: str | Path,
) -> dict[str, Any]:
    """Compare capture fingerprint against stored VQL program baseline."""
    try:
        from img2vql.fingerprint import compare_with_program

        payload = compare_with_program(image, vql_program)
    except ImportError:
        return {
            "ok": False,
            "error": "img2vql/img2nl not installed for fingerprint compare",
            "match": False,
        }
    payload["path"] = str(image)
    payload["vql_program"] = str(vql_program)
    return payload


def diagnose_window_image(
    image: str | Path,
    *,
    vql_program: str | Path | None = None,
    locale: str = "pl",
    translate_mode: str = "auto",
    save_to_program: bool = False,
) -> dict[str, Any]:
    """Run img2vql diagnose or fall back to vql image_stats heuristics."""
    loc = _normalize_locale(locale)
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
        payload = _diagnose_fallback(image, vql_program=vql_program, locale=loc)
        payload["hint"] = "Install full diagnose: pip install -e ../../wronai/img2nl -e packages/img2vql"
        return payload


def _query_window_imgl(
    *,
    uri: str,
    selector: str,
    out_file: str,
    qs: dict[str, list[str]],
    fmt: str,
) -> QueryResult:
    """Handle vql://window/imgl?action=analyze|list|click|type."""
    image_raw = (qs.get("image") or [""])[0] or None
    image, image_error = _resolve_image_param(image_raw)
    if image_error:
        return QueryResult(
            ok=False,
            uri=uri,
            selector=selector,
            file=out_file,
            error=image_error,
        )
    lang_raw = (qs.get("lang") or ["eng+pol"])[0]
    try:
        from imgl.ocr.lang import normalize_ocr_lang

        lang = normalize_ocr_lang(lang_raw)
    except ImportError:
        lang = lang_raw.replace(" ", "+")
    action_name = (qs.get("action") or ["analyze"])[0].strip().lower()
    grid = int((qs.get("grid") or ["12"])[0])
    with_grid = (qs.get("with_grid") or ["0"])[0].strip().lower() in {"1", "true", "yes"}

    try:
        from imgl import ImglConfig, write_vql_program
        from imgl.catalog import build_interactive_catalog
        from imgl.interact import InteractSession, resolve_imgl_uri
        from imgl.scene_cache import load_or_analyze, save_scene_cache
    except ImportError:
        return QueryResult(
            ok=False,
            uri=uri,
            selector=selector,
            file=out_file,
            error="imgl not installed: pip install imgl",
        )

    try:
        refresh = action_name == "analyze" or (qs.get("refresh") or ["0"])[0].strip().lower() in {
            "1",
            "true",
            "yes",
        }
        if action_name in {"list", "click", "type", "annotate", "map", "numbered"}:
            scene = load_or_analyze(
                image,
                vql_file=out_file,
                lang=lang,
                config=ImglConfig(use_img2vql=True),
                refresh=refresh,
            )
            if not Path(out_file).is_file():
                write_vql_program(scene, out_file, include_grid=with_grid, grid=grid)
                save_scene_cache(scene, out_file)
            session = InteractSession(
                image_path=image,
                vql_file=out_file,
                lang=lang,
                scene=scene,
                catalog=build_interactive_catalog(
                    scene,
                    image_path=image,
                    vql_file=out_file,
                    lang=lang,
                ),
            )
            payload = resolve_imgl_uri(uri, session)
            ok = bool(payload.get("ok"))
            return QueryResult(
                ok=ok,
                uri=uri,
                selector=selector,
                file=out_file,
                data=payload,
                rendered=json.dumps(payload, ensure_ascii=False, indent=2),
                format=fmt,
                error=None if ok else payload.get("error"),
            )

        scene = load_or_analyze(
            image,
            vql_file=out_file,
            lang=lang,
            config=ImglConfig(use_img2vql=True),
            refresh=refresh,
        )
        out_path = write_vql_program(
            scene,
            out_file,
            include_grid=with_grid,
            grid=grid,
        )
        save_scene_cache(scene, out_file)
        payload = {
            "ok": True,
            "action": "analyze",
            "path": str(image),
            "program": str(out_path),
            "element_count": scene.metadata.get("element_count", 0),
            "roles": scene.metadata.get("roles", {}),
            "detect_source": scene.metadata.get("detect_source", ""),
            "windows": [window.id for window in scene.windows],
        }
    except Exception as exc:
        return QueryResult(
            ok=False,
            uri=uri,
            selector=selector,
            file=out_file,
            error=str(exc),
        )
    return QueryResult(
        ok=True,
        uri=uri,
        selector=selector,
        file=out_file,
        data=payload,
        rendered=json.dumps(payload, ensure_ascii=False, indent=2),
        format=fmt,
    )


@dataclass
class WindowAnalyzeResult:
    ok: bool
    uri: str
    program: str
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "uri": self.uri,
            "program": self.program,
            "data": self.data,
            "error": self.error,
        }


def analyze_window_uri(
    uri: str,
    *,
    file: str = "app.vql.json",
    monitor: int = 1,
    grid: int = 12,
    image: str | None = None,
    interactive: bool | None = None,
) -> WindowAnalyzeResult:
    """
    Adopt a desktop screenshot into a VQL program file, addressable via URI.

    URI examples:
      vql://window/analyze?file=app.vql.json
      vql://window/analyze?file=app.vql.json&monitor=1&grid=16
    """
    from vql.adopt.window import analyze_screenshot

    try:
        if not uri.startswith("vql://window/"):
            return WindowAnalyzeResult(ok=False, uri=uri, program=file, error="not a window URI")
        data = analyze_screenshot(
            image,
            out_program=file,
            monitor=monitor,
            grid=grid,
            interactive=interactive,
        )
        ok = bool(data.get("ok", True))
        return WindowAnalyzeResult(
            ok=ok,
            uri=uri,
            program=file,
            data=data,
            error=None if ok else data.get("error"),
        )
    except Exception as exc:
        return WindowAnalyzeResult(ok=False, uri=uri, program=file, error=str(exc))


def query_window(uri: str, *, file: str | None = None, fmt: str = "json") -> QueryResult:
    """Handle vql://window/* URIs (analyze + query adopted program)."""
    from urllib.parse import parse_qs, urlparse

    parsed = urlparse(uri)
    qs = parse_qs(parsed.query)
    out_file = (qs.get("file") or [""])[0] or file or "app.vql.json"
    selector = (parsed.netloc + parsed.path).strip("/")

    if selector in {"window/analyze", "analyze"}:
        monitor = int((qs.get("monitor") or ["1"])[0])
        grid = int((qs.get("grid") or ["12"])[0])
        image = (qs.get("image") or [""])[0] or None
        interactive_raw = (qs.get("interactive") or [""])[0].strip().lower()
        interactive = interactive_raw in {"1", "true", "yes"} if interactive_raw else None
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

    if selector in {"window/detect", "detect"}:
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
        ok = bool(payload.get("ok"))
        return QueryResult(
            ok=ok,
            uri=uri,
            selector=selector,
            file=out_file,
            data=payload,
            rendered=json.dumps(payload, ensure_ascii=False, indent=2),
            format=fmt,
            error=None if ok else payload.get("error"),
        )

    if selector in {"window/adopt", "adopt"}:
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
        with_grid = (qs.get("with_grid") or ["0"])[0].strip().lower() in {"1", "true", "yes"}
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
        ok = bool(payload.get("ok"))
        return QueryResult(
            ok=ok,
            uri=uri,
            selector=selector,
            file=out_file,
            data=payload,
            rendered=json.dumps(payload, ensure_ascii=False, indent=2),
            format=fmt,
            error=None if ok else payload.get("error"),
        )

    if selector in {"window/imgl", "imgl"}:
        return _query_window_imgl(
            uri=uri,
            selector=selector,
            out_file=out_file,
            qs=qs,
            fmt=fmt,
        )

    if selector in {"window/diagnose", "diagnose"}:
        image = _resolve_window_image(out_file, (qs.get("image") or [""])[0] or None)
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
        save_raw = (qs.get("save") or [""])[0].strip().lower()
        save_to_program = save_raw in {"1", "true", "yes"}
        payload = diagnose_window_image(
            image,
            vql_program=out_file if Path(out_file).is_file() else None,
            locale=locale,
            translate_mode=translate_mode,
            save_to_program=save_to_program,
        )
        ok = bool(payload.get("ok"))
        return QueryResult(
            ok=ok,
            uri=uri,
            selector=selector,
            file=out_file,
            data=payload,
            rendered=json.dumps(payload, ensure_ascii=False, indent=2),
            format=fmt,
            error=None if ok else payload.get("error"),
        )

    if selector in {"window/compare", "compare"}:
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
        ok = bool(payload.get("ok"))
        return QueryResult(
            ok=ok,
            uri=uri,
            selector=selector,
            file=out_file,
            data=payload,
            rendered=json.dumps(payload, ensure_ascii=False, indent=2),
            format=fmt,
            error=None if ok else payload.get("error"),
        )

    if selector in {"window/refresh", "refresh"}:
        image = _resolve_window_image(out_file, (qs.get("image") or [""])[0] or None)
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
        ok = bool(payload.get("ok"))
        return QueryResult(
            ok=ok,
            uri=uri,
            selector=selector,
            file=out_file,
            data=payload,
            rendered=json.dumps(payload, ensure_ascii=False, indent=2),
            format=fmt,
            error=None if ok else payload.get("error"),
        )

    if selector in {"window/summary", "summary"}:
        if not Path(out_file).is_file():
            return QueryResult(ok=False, uri=uri, selector=selector, file=out_file, error="program file missing; run analyze first")
        live_raw = (qs.get("live") or [""])[0].strip().lower()
        if live_raw in {"1", "true", "yes"}:
            image = _resolve_window_image(out_file, (qs.get("image") or [""])[0] or None)
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

    # After analyze, delegate object/scene queries to standard query_uri
    if Path(out_file).is_file():
        sub = uri.replace("vql://window/", "vql://").replace("vql://analyze/", "vql://")
        if sub.startswith("vql://objects") or sub.startswith("vql://scene") or sub.startswith("vql://program"):
            return query_uri(sub if "?" in sub else f"{sub}?file={out_file}", file=out_file, fmt=fmt)

    return QueryResult(ok=False, uri=uri, selector=selector, file=out_file, error=f"unknown window selector: {selector}")
