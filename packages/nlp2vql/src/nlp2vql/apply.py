"""NL → DSL → dispatch for VQL control."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nlp2vql.to_dsl import nl_to_dsl_line


@dataclass
class ApplyResult:
    ok: bool
    prompt: str
    dsl: str = ""
    action: str = ""
    output: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "prompt": self.prompt,
            "dsl": self.dsl,
            "action": self.action,
            "output": self.output,
            "data": self.data,
            "error": self.error,
        }


def apply_nl(prompt: str, *, file: str | None = None, execute: bool = True) -> ApplyResult:
    dsl = nl_to_dsl_line(prompt, file=file)
    if not execute:
        return ApplyResult(ok=True, prompt=prompt, dsl=dsl, output=dsl)
    from dsl2vql import dispatch

    result = dispatch(dsl, default_file=file)
    return ApplyResult(
        ok=result.ok,
        prompt=prompt,
        dsl=dsl,
        action=result.action,
        output=result.output,
        data=result.data,
        error=result.error,
    )
