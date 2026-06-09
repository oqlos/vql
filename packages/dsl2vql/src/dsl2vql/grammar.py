"""Text DSL → dict for VQL control verbs."""

from __future__ import annotations

from typing import Any

from dsl2vql.grammar_handlers import build_command
from dsl2vql.grammar_tokens import split_command

from dsl2vql.grammar_tokens import pick_flag, split_command  # noqa: F401


def parse_line(line: str) -> dict[str, Any] | None:
    tokens = split_command(line)
    if not tokens:
        return None
    return build_command(tokens[0].upper(), tokens[1:])


def to_text(cmd: dict[str, Any]) -> str:
    verb = str(cmd.get("verb", "")).upper()
    parts = [verb]
    for key in ("target", "path", "text"):
        if val := cmd.get(key):
            parts.append(f'"{val}"' if " " in str(val) else str(val))
    for key, flag in (
        ("file", "FILE"),
        ("format", "FORMAT"),
        ("with_path", "WITH"),
        ("out", "OUT"),
        ("width", "WIDTH"),
        ("height", "HEIGHT"),
    ):
        if val := cmd.get(key):
            parts.extend([flag, str(val)])
    return " ".join(parts)
