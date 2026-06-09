"""Tests for nlp2uri window/img2nl URI hints."""

from __future__ import annotations

from uri2vql.nlp2uri import best_uri, resolve_prompt_to_vql_uri


def test_nlp_refresh_window() -> None:
    hit = best_uri("odśwież metadata vql app.vql.json", file="app.vql.json", image="/tmp/s.png")
    assert hit is not None
    assert "window/refresh" in hit.uri
    assert hit.match_reason == "window:refresh"


def test_nlp_compare_window() -> None:
    hit = best_uri("porównaj fingerprint vql z capture", file="prog.vql.json", image="/tmp/x.png")
    assert hit is not None
    assert "window/compare" in hit.uri


def test_nlp_diagnose_window() -> None:
    hits = resolve_prompt_to_vql_uri("diagnozuj capture czy wysłać do llm vql", file="a.vql.json")
    uris = [h.uri for h in hits]
    assert any("window/diagnose" in u for u in uris)


def test_nlp_unchanged_suggests_compare() -> None:
    hit = best_uri("czy ekran jest ten sam vql", file="app.vql.json", image="/tmp/s.png")
    assert hit is not None
    assert "window/compare" in hit.uri
