"""Protobuf body field mappers for DslEnvelope."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from dsl2vql.v1 import command_pb2

BODY_MAP: dict[str, str] = {
    "QUERY": "query",
    "VALIDATE": "validate",
    "RESOLVE": "resolve",
    "PATCH": "patch",
    "GENERATE": "generate",
    "RENDER": "render",
    "COMPILE": "compile",
    "EXPORT": "export",
}

EncodeBody = Callable[[Any, dict[str, Any]], None]
DecodeBody = Callable[[Any, dict[str, Any]], None]


def encode_query(msg: Any, cmd: dict[str, Any]) -> None:
    msg.target = str(cmd.get("target", ""))
    msg.file = str(cmd.get("file", ""))
    msg.format = str(cmd.get("format", "json"))


def encode_validate(msg: Any, cmd: dict[str, Any]) -> None:
    msg.path = str(cmd.get("path", ""))


def encode_resolve(msg: Any, cmd: dict[str, Any]) -> None:
    msg.text = str(cmd.get("text", ""))
    msg.file = str(cmd.get("file", ""))


def encode_patch(msg: Any, cmd: dict[str, Any]) -> None:
    msg.target = str(cmd.get("target", ""))
    msg.with_path = str(cmd.get("with_path", ""))
    msg.file = str(cmd.get("file", ""))


def encode_generate(msg: Any, cmd: dict[str, Any]) -> None:
    msg.text = str(cmd.get("text", ""))
    msg.out = str(cmd.get("out", ""))


def encode_render(msg: Any, cmd: dict[str, Any]) -> None:
    msg.path = str(cmd.get("path", ""))
    msg.out = str(cmd.get("out", ""))
    msg.format = str(cmd.get("format", "svg"))


def encode_compile(msg: Any, cmd: dict[str, Any]) -> None:
    msg.text = str(cmd.get("text", ""))
    msg.width = float(cmd.get("width") or 1024)
    msg.height = float(cmd.get("height") or 768)


def encode_export(msg: Any, cmd: dict[str, Any]) -> None:
    msg.path = str(cmd.get("path", ""))
    msg.out = str(cmd.get("out", ""))
    msg.format = str(cmd.get("format", "svg"))


def decode_query(msg: Any, cmd: dict[str, Any]) -> None:
    if msg.target:
        cmd["target"] = msg.target
    if msg.file:
        cmd["file"] = msg.file
    if msg.format:
        cmd["format"] = msg.format


def decode_validate(msg: Any, cmd: dict[str, Any]) -> None:
    if msg.path:
        cmd["path"] = msg.path


def decode_resolve(msg: Any, cmd: dict[str, Any]) -> None:
    if msg.text:
        cmd["text"] = msg.text
    if msg.file:
        cmd["file"] = msg.file


def decode_patch(msg: Any, cmd: dict[str, Any]) -> None:
    if msg.target:
        cmd["target"] = msg.target
    if msg.with_path:
        cmd["with_path"] = msg.with_path
    if msg.file:
        cmd["file"] = msg.file


def decode_generate(msg: Any, cmd: dict[str, Any]) -> None:
    if msg.text:
        cmd["text"] = msg.text
    if msg.out:
        cmd["out"] = msg.out


def decode_render(msg: Any, cmd: dict[str, Any]) -> None:
    if msg.path:
        cmd["path"] = msg.path
    if msg.out:
        cmd["out"] = msg.out
    if msg.format:
        cmd["format"] = msg.format


def decode_compile(msg: Any, cmd: dict[str, Any]) -> None:
    if msg.text:
        cmd["text"] = msg.text
    if msg.width:
        cmd["width"] = msg.width
    if msg.height:
        cmd["height"] = msg.height


def decode_export(msg: Any, cmd: dict[str, Any]) -> None:
    if msg.path:
        cmd["path"] = msg.path
    if msg.out:
        cmd["out"] = msg.out
    if msg.format:
        cmd["format"] = msg.format


ENCODE_BODY: dict[str, EncodeBody] = {
    "QUERY": encode_query,
    "VALIDATE": encode_validate,
    "RESOLVE": encode_resolve,
    "PATCH": encode_patch,
    "GENERATE": encode_generate,
    "RENDER": encode_render,
    "COMPILE": encode_compile,
    "EXPORT": encode_export,
}

DECODE_BODY: dict[str, DecodeBody] = {
    "QUERY": decode_query,
    "VALIDATE": decode_validate,
    "RESOLVE": decode_resolve,
    "PATCH": decode_patch,
    "GENERATE": decode_generate,
    "RENDER": decode_render,
    "COMPILE": decode_compile,
    "EXPORT": decode_export,
}


def set_envelope_body(envelope: command_pb2.DslEnvelope, cmd: dict[str, Any]) -> None:
    verb = str(cmd.get("verb", "")).upper()
    field = BODY_MAP.get(verb)
    encoder = ENCODE_BODY.get(verb)
    if not field or encoder is None:
        return
    encoder(getattr(envelope, field), cmd)


def envelope_to_dict(envelope: command_pb2.DslEnvelope) -> dict[str, Any]:
    verb = envelope.verb.upper()
    cmd: dict[str, Any] = {"verb": verb}
    field = BODY_MAP.get(verb)
    decoder = DECODE_BODY.get(verb)
    if not field or decoder is None or envelope.WhichOneof("body") != field:
        return cmd
    decoder(getattr(envelope, field), cmd)
    return cmd
