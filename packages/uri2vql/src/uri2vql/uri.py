"""Parse vql:// URIs."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse


@dataclass
class VqlUri:
    scheme: str
    selector: str
    file: str = ""

    @property
    def target(self) -> str:
        return f"{self.scheme}://{self.selector}"


def parse_vql_uri(uri: str, *, default_file: str = "") -> VqlUri:
    parsed = urlparse(uri)
    if parsed.scheme != "vql":
        raise ValueError(f"expected vql:// URI, got: {uri}")
    selector = (parsed.netloc + parsed.path).strip("/") or "program"
    qs = parse_qs(parsed.query)
    file_param = (qs.get("file") or [""])[0] or default_file
    return VqlUri(scheme="vql", selector=selector, file=file_param)
