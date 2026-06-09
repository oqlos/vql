"""Bidirectional image ↔ VQL conversion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from vql.schema.program import VQLProgram


def vql_to_image(
    program: VQLProgram | dict[str, Any] | str | Path,
    out_path: str | Path,
    *,
    scale: float = 1.0,
) -> str:
    """Render VQL program to PNG (VQL → image)."""
    from vql.renderers import render_to_png

    if isinstance(program, (str, Path)) and Path(program).is_file():
        data = json.loads(Path(program).read_text(encoding="utf-8"))
        vql = VQLProgram.from_dict(data)
    elif isinstance(program, dict):
        vql = VQLProgram.from_dict(program)
    else:
        vql = program  # type: ignore[assignment]

    return render_to_png(vql, str(out_path), scale=scale)


def image_to_vql(
    image_path: str | Path,
    out_program: str | Path = "app.vql.json",
    *,
    locale: str = "pl",
    grid: int = 12,
    adopt_method: str = "auto",
    run_llm: bool | None = None,
    render_out: str | Path | None = None,
) -> dict[str, Any]:
    """Full multi-level pipeline wrapper (image → VQL [→ render PNG])."""
    from img2vql.pipeline.config import PipelineConfig
    from img2vql.pipeline.orchestrate import analyze_image_to_vql

    cfg = PipelineConfig.from_env(locale=locale, grid=grid, adopt_method=adopt_method)
    return analyze_image_to_vql(
        image_path,
        out_program=out_program,
        config=cfg,
        render_out=render_out,
        run_llm=run_llm,
    )


def roundtrip_compare(
    image_path: str | Path,
    *,
    out_program: str | Path = "roundtrip.vql.json",
    out_render: str | Path = "roundtrip.render.png",
    locale: str = "pl",
    run_llm: bool = False,
) -> dict[str, Any]:
    """image → VQL → PNG; returns paths and basic stats."""
    forward = image_to_vql(
        image_path,
        out_program=out_program,
        locale=locale,
        run_llm=run_llm,
        render_out=out_render,
    )
    if not forward.get("ok"):
        return forward

    from vql.adopt.window import image_stats

    src_stats = image_stats(image_path)
    dst_stats = image_stats(out_render) if Path(out_render).is_file() else {}
    return {
        **forward,
        "roundtrip": {
            "source": src_stats,
            "rendered": dst_stats,
            "render_path": str(out_render),
        },
    }
