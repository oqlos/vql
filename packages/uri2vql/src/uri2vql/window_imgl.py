"""vql://window/imgl handler."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from uri2vql.query import QueryResult
from uri2vql.window_utils import query_bool, resolve_image_param


def query_window_imgl(
    *,
    uri: str,
    selector: str,
    out_file: str,
    qs: dict[str, list[str]],
    fmt: str,
) -> QueryResult:
    """Handle vql://window/imgl?action=analyze|list|click|type."""
    image_raw = (qs.get("image") or [""])[0] or None
    image, image_error = resolve_image_param(image_raw)
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
    with_grid = query_bool((qs.get("with_grid") or ["0"])[0])

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
        refresh = action_name == "analyze" or query_bool((qs.get("refresh") or ["0"])[0])
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
        payload: dict[str, Any] = {
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
