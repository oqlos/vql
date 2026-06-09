"""Tests for multi-level img2nl pipeline (fast path, no LLM)."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PIL")
pytest.importorskip("img2nl")


def _solid(path: Path, color: tuple[int, int, int], size: tuple[int, int] = (160, 100)) -> Path:
    from PIL import Image

    Image.new("RGB", size, color=color).save(path)
    return path


def test_pipeline_fast_levels_without_llm(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("VQL_LLM_API_KEY", raising=False)
    monkeypatch.setenv("VQL_LLM_ENABLED", "0")

    img = _solid(tmp_path / "screen.png", (40, 90, 140))
    out = tmp_path / "app.vql.json"

    from img2vql.pipeline import analyze_image_to_vql
    from img2vql.pipeline.config import PipelineConfig

    cfg = PipelineConfig.from_env(locale="pl", grid=8, adopt_method="grid")
    payload = analyze_image_to_vql(img, out_program=out, config=cfg, run_llm=False)

    assert payload.get("ok") is True
    assert out.is_file()
    levels = payload.get("levels", {})
    assert "L0" in levels and levels["L0"].get("ok") is True
    assert "L1" in levels and levels["L1"].get("ok") is True
    assert "L3" in levels and levels["L3"].get("ok") is True
    assert levels.get("L5", {}).get("skipped") is True


def test_vql_to_image_roundtrip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VQL_LLM_ENABLED", "0")
    pytest.importorskip("cairosvg")

    img = _solid(tmp_path / "blocks.png", (200, 50, 50), size=(120, 80))
    out_prog = tmp_path / "prog.vql.json"
    out_png = tmp_path / "render.png"

    from img2vql.pipeline import image_to_vql, vql_to_image

    forward = image_to_vql(img, out_program=out_prog, adopt_method="grid", run_llm=False, render_out=None)
    assert forward.get("ok") is True

    render_path = vql_to_image(out_prog, out_png)
    assert Path(render_path).is_file()
    assert Path(render_path).stat().st_size > 100


def test_normalize_openrouter_model_strips_prefix() -> None:
    from img2vql.pipeline.config import normalize_openrouter_model, resolve_vql_llm_model

    assert normalize_openrouter_model("openrouter/google/gemini-2.0-flash-001") == "google/gemini-2.0-flash-001"
    assert normalize_openrouter_model("google/gemini-2.5-flash-preview") == "google/gemini-2.5-flash-preview"


def test_resolve_vql_llm_model_ignores_coder_llm_model(monkeypatch: pytest.MonkeyPatch) -> None:
    from img2vql.pipeline.config import DEFAULT_VQL_VISION_MODEL, resolve_vql_llm_model

    monkeypatch.delenv("VQL_LLM_MODEL", raising=False)
    monkeypatch.setenv("LLM_MODEL", "openrouter/qwen/qwen3-coder-next")
    assert resolve_vql_llm_model() == DEFAULT_VQL_VISION_MODEL
    from img2vql.pipeline.llm_vql import build_llm_extraction_prompt

    l1 = {
        "text": "UI with red button",
        "metadata": {"scene_class": "dense_ui_or_code"},
        "features": {"colors": {"dominant": ["#FF0000"]}},
        "llm_hint": {"send_to_llm": True},
        "width": 800,
        "height": 600,
    }
    prompt = build_llm_extraction_prompt(
        fast_context={
            "img2nl_text": l1["text"],
            "scene_class": "dense_ui_or_code",
            "llm_hint": l1["llm_hint"],
        },
        partial_program={"scene": {"width": 800, "height": 600, "layers": []}, "metadata": {}},
        scene_width=800,
        scene_height=600,
        locale="pl",
    )
    assert "img2nl" in prompt or "FAST PRE-ANALYSIS" in prompt
    assert "VQLProgram" in prompt or "VQL" in prompt
    assert "800" in prompt
