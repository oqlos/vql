"""Backward-compat shim — re-export dispatch from bus."""

from __future__ import annotations

from dsl2vql.bus import dispatch, execute_dsl, execute_dsl_line
from dsl2vql.result import DslResult

__all__ = ["DslResult", "dispatch", "execute_dsl", "execute_dsl_line"]
