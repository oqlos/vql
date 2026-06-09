"""Regression: parse_line verb handlers after registry refactor."""

from __future__ import annotations

from dsl2vql.grammar import parse_line, to_text


def test_parse_query_with_flags() -> None:
    cmd = parse_line('QUERY vql://program FILE app.vql.json FORMAT json')
    assert cmd == {
        "verb": "QUERY",
        "target": "vql://program",
        "file": "app.vql.json",
        "format": "json",
    }


def test_parse_compile_dimensions() -> None:
    cmd = parse_line('COMPILE "narysuj koło" WIDTH 800 HEIGHT 600')
    assert cmd == {
        "verb": "COMPILE",
        "text": "narysuj koło WIDTH 800 HEIGHT 600",
        "width": 800.0,
        "height": 600.0,
    }


def test_parse_unknown_verb_passthrough() -> None:
    cmd = parse_line("CUSTOM arg1 arg2")
    assert cmd == {"verb": "CUSTOM", "args": ["arg1", "arg2"]}


def test_to_text_roundtrip() -> None:
    line = 'GENERATE "narysuj koło" OUT app.vql.json'
    assert to_text(parse_line(line) or {}) == line
