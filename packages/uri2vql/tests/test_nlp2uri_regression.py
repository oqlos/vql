"""Regression: NL resolve parity after intent registry refactor."""

from __future__ import annotations

from uri2vql.nlp2uri import resolve_prompt_to_vql_uri


def _snapshot(prompt: str, **kwargs) -> list[tuple[str, float, str]]:
    hits = resolve_prompt_to_vql_uri(prompt, **kwargs)
    return [(h.uri, h.confidence, h.match_reason) for h in hits]


def test_resolve_refresh_window() -> None:
    hits = _snapshot("odśwież metadata vql app.vql.json", file="app.vql.json", image="/tmp/s.png")
    assert any(r == "window:refresh" for _, _, r in hits)
    top = hits[0]
    assert top[2] == "window:refresh"
    assert top[1] == 0.93


def test_resolve_compare_and_unchanged() -> None:
    compare = _snapshot("porównaj fingerprint vql z capture", file="prog.vql.json", image="/tmp/x.png")
    assert any(r == "window:compare" for _, _, r in compare)
    unchanged = _snapshot("czy ekran jest ten sam vql", file="app.vql.json", image="/tmp/s.png")
    assert any(r == "window:compare" for _, c, r in unchanged if c == 0.88)


def test_resolve_diagnose_multi_hit() -> None:
    hits = _snapshot("diagnozuj capture czy wysłać do llm vql", file="a.vql.json")
    reasons = [r for _, _, r in hits]
    assert "window:diagnose" in reasons


def test_resolve_imgl_click_without_target() -> None:
    hits = _snapshot("click", file="app.vql.json")
    click = next(h for h in hits if h[2] == "imgl:click")
    assert click[1] == 0.7
