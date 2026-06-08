"""Parity: ta sama linia DSL → ten sam wynik (offline verby)."""

from __future__ import annotations

from dsl2vql import dispatch


def test_parity_text_vs_dict() -> None:
    line = 'COMPILE "narysuj koło"'
    r1 = dispatch(line)
    r2 = dispatch({"verb": "COMPILE", "text": "narysuj koło"})
    assert r1.ok == r2.ok
    assert r1.action == r2.action


def test_validate_schema_registry() -> None:
    from dsl2vql.schema_registry import validate_schema_registry

    assert validate_schema_registry() == []


def test_encode_decode_roundtrip() -> None:
    from dsl2vql.codec import decode_protobuf, encode_protobuf, roundtrip_text

    line = 'GENERATE "narysuj koło" OUT app.vql.json'
    assert roundtrip_text(line) == line
    pb = encode_protobuf(line)
    assert decode_protobuf(pb) == line
