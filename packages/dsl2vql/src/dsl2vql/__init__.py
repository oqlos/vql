"""VQL control DSL — query, validate, render, generate and compile programs."""

from dsl2vql.bus import dispatch, execute_dsl, execute_dsl_line
from dsl2vql.engine import DslResult

__all__ = ["DslResult", "dispatch", "execute_dsl", "execute_dsl_line"]
