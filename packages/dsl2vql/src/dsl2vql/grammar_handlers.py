"""Per-verb DSL command builders."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from dsl2vql.grammar_tokens import pick_flag

VerbBuilder = Callable[[list[str], dict[str, Any]], None]


def build_query(rest: list[str], cmd: dict[str, Any]) -> None:
    cmd["target"] = rest[0] if rest else ""
    if f := pick_flag(rest, "FILE"):
        cmd["file"] = f
    if f := pick_flag(rest, "FORMAT"):
        cmd["format"] = f.lower()


def build_validate(rest: list[str], cmd: dict[str, Any]) -> None:
    cmd["path"] = rest[0] if rest else ""


def build_resolve(rest: list[str], cmd: dict[str, Any]) -> None:
    cmd["text"] = " ".join(rest).strip('"').strip("'")
    if f := pick_flag(rest, "FILE"):
        cmd["file"] = f


def build_patch(rest: list[str], cmd: dict[str, Any]) -> None:
    cmd["target"] = rest[0] if rest else ""
    if f := pick_flag(rest, "WITH"):
        cmd["with_path"] = f
    if f := pick_flag(rest, "FILE"):
        cmd["file"] = f


def build_generate(rest: list[str], cmd: dict[str, Any]) -> None:
    cmd["text"] = rest[0].strip('"').strip("'") if rest else ""
    if f := pick_flag(rest, "OUT"):
        cmd["out"] = f


def build_render(rest: list[str], cmd: dict[str, Any]) -> None:
    cmd["path"] = rest[0] if rest else ""
    if f := pick_flag(rest, "OUT"):
        cmd["out"] = f
    if f := pick_flag(rest, "FORMAT"):
        cmd["format"] = f.lower()


def build_compile(rest: list[str], cmd: dict[str, Any]) -> None:
    cmd["text"] = " ".join(rest).strip('"').strip("'")
    if f := pick_flag(rest, "WIDTH"):
        cmd["width"] = float(f)
    if f := pick_flag(rest, "HEIGHT"):
        cmd["height"] = float(f)


def build_export(rest: list[str], cmd: dict[str, Any]) -> None:
    cmd["path"] = rest[0] if rest else ""
    if f := pick_flag(rest, "OUT"):
        cmd["out"] = f
    if f := pick_flag(rest, "FORMAT"):
        cmd["format"] = f.lower()


VERB_BUILDERS: dict[str, VerbBuilder] = {
    "QUERY": build_query,
    "VALIDATE": build_validate,
    "RESOLVE": build_resolve,
    "PATCH": build_patch,
    "GENERATE": build_generate,
    "RENDER": build_render,
    "COMPILE": build_compile,
    "EXPORT": build_export,
}


def build_command(verb: str, rest: list[str]) -> dict[str, Any]:
    cmd: dict[str, Any] = {"verb": verb}
    builder = VERB_BUILDERS.get(verb)
    if builder is not None:
        builder(rest, cmd)
    else:
        cmd["args"] = rest
    return cmd
