"""Parse and build img2svg:// URIs."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import parse_qs, urlencode, urlparse

IMG2SVG_SCHEME = "img2svg"


@dataclass
class Img2SvgUri:
    scheme: str
    selector: str
    path: str = ""
    out: str = ""
    grid: int = 24
    method: str = "regions"

    @property
    def target(self) -> str:
        return f"{self.scheme}://{self.selector}"


def is_img2svg_uri(uri: str) -> bool:
    return urlparse(uri).scheme.lower() == IMG2SVG_SCHEME


def uri_for_vectorize(
    path: str,
    *,
    out: str = "",
    grid: int = 24,
    method: str = "regions",
) -> str:
    params: dict[str, str] = {"path": path, "grid": str(grid), "method": method}
    if out:
        params["out"] = out
    return f"img2svg://vectorize?{urlencode(params)}"


def parse_img2svg_uri(uri: str) -> Img2SvgUri:
    parsed = urlparse(uri)
    if parsed.scheme != IMG2SVG_SCHEME:
        raise ValueError(f"expected img2svg:// URI, got: {uri}")
    selector = (parsed.netloc + parsed.path).strip("/") or "vectorize"
    qs = parse_qs(parsed.query)
    path = (qs.get("path") or [""])[0]
    out = (qs.get("out") or [""])[0] or (qs.get("file") or [""])[0]
    grid = int((qs.get("grid") or ["24"])[0])
    method = (qs.get("method") or ["regions"])[0]
    return Img2SvgUri(
        scheme=IMG2SVG_SCHEME,
        selector=selector,
        path=path,
        out=out,
        grid=grid,
        method=method,
    )
