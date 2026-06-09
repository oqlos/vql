"""img2svg:// URI query layer."""

from uri2img2svg.query import QueryResult, query_uri
from uri2img2svg.uri import parse_img2svg_uri, uri_for_vectorize

__all__ = ["QueryResult", "query_uri", "parse_img2svg_uri", "uri_for_vectorize"]
