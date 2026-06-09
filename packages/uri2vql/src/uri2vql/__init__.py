"""vql:// URI query and patch."""

from uri2vql.compile import compile_vql_uri
from uri2vql.nlp2uri import ResolvedVqlUri, best_uri, nlp2uri, resolve_prompt_to_vql_uri
from uri2vql.patch import patch_uri
from uri2vql.query import query_uri
from uri2vql.run import run_uri
from uri2vql.uri import (
    VQL_SCHEME,
    is_vql_uri,
    uri_for_objects,
    uri_for_program,
    uri_for_scene,
    uri_for_window_analyze,
    uri_for_window_compare,
    uri_for_window_imgl,
    uri_for_window_refresh,
    uri_for_window_summary,
)
from uri2vql.window import analyze_window_uri, compare_window_image, query_window, refresh_window_metadata

__all__ = [
    "VQL_SCHEME",
    "ResolvedVqlUri",
    "analyze_window_uri",
    "best_uri",
    "compare_window_image",
    "compile_vql_uri",
    "is_vql_uri",
    "nlp2uri",
    "patch_uri",
    "query_uri",
    "query_window",
    "refresh_window_metadata",
    "resolve_prompt_to_vql_uri",
    "run_uri",
    "uri_for_objects",
    "uri_for_program",
    "uri_for_scene",
    "uri_for_window_analyze",
    "uri_for_window_compare",
    "uri_for_window_imgl",
    "uri_for_window_refresh",
    "uri_for_window_summary",
]
