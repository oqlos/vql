"""Dict ↔ protobuf DslEnvelope / DslResult."""

from __future__ import annotations

import json
from typing import Any

from dsl2vql.grammar import parse_line, to_text
from dsl2vql.result import DslResult
from dsl2vql.v1 import command_pb2, result_pb2

_BODY_MAP = {
    "QUERY": "query",
    "VALIDATE": "validate",
    "RESOLVE": "resolve",
    "PATCH": "patch",
    "GENERATE": "generate",
    "RENDER": "render",
    "COMPILE": "compile",
    "EXPORT": "export",
}


def _set_body(envelope: command_pb2.DslEnvelope, cmd: dict[str, Any]) -> None:
    verb = str(cmd.get("verb", "")).upper()
    field = _BODY_MAP.get(verb)
    if not field:
        return
    msg = getattr(envelope, field)
    if verb == "QUERY":
        msg.target = str(cmd.get("target", ""))
        msg.file = str(cmd.get("file", ""))
        msg.format = str(cmd.get("format", "json"))
    elif verb == "VALIDATE":
        msg.path = str(cmd.get("path", ""))
    elif verb == "RESOLVE":
        msg.text = str(cmd.get("text", ""))
        msg.file = str(cmd.get("file", ""))
    elif verb == "PATCH":
        msg.target = str(cmd.get("target", ""))
        msg.with_path = str(cmd.get("with_path", ""))
        msg.file = str(cmd.get("file", ""))
    elif verb == "GENERATE":
        msg.text = str(cmd.get("text", ""))
        msg.out = str(cmd.get("out", ""))
    elif verb == "RENDER":
        msg.path = str(cmd.get("path", ""))
        msg.out = str(cmd.get("out", ""))
        msg.format = str(cmd.get("format", "svg"))
    elif verb == "COMPILE":
        msg.text = str(cmd.get("text", ""))
        msg.width = float(cmd.get("width") or 1024)
        msg.height = float(cmd.get("height") or 768)
    elif verb == "EXPORT":
        msg.path = str(cmd.get("path", ""))
        msg.out = str(cmd.get("out", ""))
        msg.format = str(cmd.get("format", "svg"))


def envelope_to_dict(envelope: command_pb2.DslEnvelope) -> dict[str, Any]:
    verb = envelope.verb.upper()
    cmd: dict[str, Any] = {"verb": verb}
    field = _BODY_MAP.get(verb)
    if not field or envelope.WhichOneof("body") != field:
        return cmd
    msg = getattr(envelope, field)
    if verb == "QUERY":
        if msg.target:
            cmd["target"] = msg.target
        if msg.file:
            cmd["file"] = msg.file
        if msg.format:
            cmd["format"] = msg.format
    elif verb == "VALIDATE" and msg.path:
        cmd["path"] = msg.path
    elif verb == "RESOLVE":
        if msg.text:
            cmd["text"] = msg.text
        if msg.file:
            cmd["file"] = msg.file
    elif verb == "PATCH":
        if msg.target:
            cmd["target"] = msg.target
        if msg.with_path:
            cmd["with_path"] = msg.with_path
        if msg.file:
            cmd["file"] = msg.file
    elif verb == "GENERATE":
        if msg.text:
            cmd["text"] = msg.text
        if msg.out:
            cmd["out"] = msg.out
    elif verb == "RENDER":
        if msg.path:
            cmd["path"] = msg.path
        if msg.out:
            cmd["out"] = msg.out
        if msg.format:
            cmd["format"] = msg.format
    elif verb == "COMPILE":
        if msg.text:
            cmd["text"] = msg.text
        if msg.width:
            cmd["width"] = msg.width
        if msg.height:
            cmd["height"] = msg.height
    elif verb == "EXPORT":
        if msg.path:
            cmd["path"] = msg.path
        if msg.out:
            cmd["out"] = msg.out
        if msg.format:
            cmd["format"] = msg.format
    return cmd


def encode_protobuf(cmd: dict[str, Any], *, default_file: str = "", correlation_id: str = "") -> bytes:
    envelope = command_pb2.DslEnvelope()
    envelope.verb = str(cmd.get("verb", "")).upper()
    _set_body(envelope, cmd)
    envelope.default_file = default_file
    envelope.correlation_id = correlation_id
    return envelope.SerializeToString()


def decode_protobuf(data: bytes) -> dict[str, Any]:
    envelope = command_pb2.DslEnvelope()
    envelope.ParseFromString(data)
    return envelope_to_dict(envelope)


def encode_text_to_protobuf(line: str, *, default_file: str = "", correlation_id: str = "") -> bytes:
    cmd = parse_line(line)
    if cmd is None:
        raise ValueError("empty command")
    return encode_protobuf(cmd, default_file=default_file, correlation_id=correlation_id)


def decode_protobuf_to_text(data: bytes) -> str:
    return to_text(decode_protobuf(data))


def result_to_pb(result: DslResult) -> result_pb2.DslResult:
    pb = result_pb2.DslResult()
    pb.ok = result.ok
    pb.verb = (result.action or "").upper()
    pb.output = result.output
    pb.data_json = json.dumps(result.data, ensure_ascii=False).encode("utf-8")
    pb.error = result.error or ""
    pb.event_id = result.event_id or ""
    pb.command = result.command
    pb.action = result.action
    return pb


def encode_result_protobuf(result: DslResult) -> bytes:
    return result_to_pb(result).SerializeToString()
