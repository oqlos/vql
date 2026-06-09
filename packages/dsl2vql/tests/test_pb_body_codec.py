"""Regression: envelope protobuf roundtrip after body codec refactor."""

from __future__ import annotations

from dsl2vql.pb_body_codec import envelope_to_dict, set_envelope_body
from dsl2vql.v1 import command_pb2


def test_envelope_query_roundtrip() -> None:
    cmd = {"verb": "QUERY", "target": "vql://scene", "file": "app.vql.json", "format": "json"}
    envelope = command_pb2.DslEnvelope()
    envelope.verb = "QUERY"
    set_envelope_body(envelope, cmd)
    assert envelope_to_dict(envelope) == cmd


def test_envelope_compile_roundtrip() -> None:
    cmd = {"verb": "COMPILE", "text": "circle", "width": 640.0, "height": 480.0}
    envelope = command_pb2.DslEnvelope()
    envelope.verb = "COMPILE"
    set_envelope_body(envelope, cmd)
    assert envelope_to_dict(envelope) == cmd
