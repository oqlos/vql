"""Parse and build vql:// URIs."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import parse_qs, urlencode, urlparse

VQL_SCHEME = "vql"


@dataclass
class VqlUri:
    scheme: str
    selector: str
    file: str = ""

    @property
    def target(self) -> str:
        return f"{self.scheme}://{self.selector}"


def is_vql_uri(uri: str) -> bool:
    return urlparse(uri).scheme.lower() == VQL_SCHEME


def _with_file(selector: str, *, file: str, extra: dict[str, str | int] | None = None) -> str:
    params: dict[str, str] = {"file": file}
    if extra:
        params.update({k: str(v) for k, v in extra.items() if v != ""})
    return f"vql://{selector}?{urlencode(params)}"


def uri_for_program(file: str = "app.vql.json") -> str:
    return _with_file("program", file=file)


def uri_for_scene(file: str = "app.vql.json") -> str:
    return _with_file("scene", file=file)


def uri_for_objects(file: str = "app.vql.json") -> str:
    return _with_file("objects", file=file)


def uri_for_object(obj_id: str, *, file: str = "app.vql.json") -> str:
    return _with_file(f"object/{obj_id}", file=file)


def uri_for_window_analyze(
    *,
    file: str = "app.vql.json",
    monitor: int = 1,
    grid: int = 12,
    image: str = "",
) -> str:
    extra: dict[str, str | int] = {"monitor": monitor, "grid": grid}
    if image:
        extra["image"] = image
    return _with_file("window/analyze", file=file, extra=extra)


def uri_for_window_summary(file: str = "app.vql.json") -> str:
    return _with_file("window/summary", file=file)


def uri_for_window_imgl(
    *,
    file: str = "layout.vql.json",
    image: str = "",
    lang: str = "eng+pol",
    with_grid: bool = False,
    grid: int = 12,
    action: str = "analyze",
) -> str:
    extra: dict[str, str | int] = {"action": action, "lang": lang, "grid": grid}
    if image:
        extra["image"] = image
    if with_grid:
        extra["with_grid"] = "1"
    return _with_file("window/imgl", file=file, extra=extra)


def uri_for_imgl_list(
    *,
    file: str = "layout.vql.json",
    image: str = "",
    lang: str = "eng",
) -> str:
    return uri_for_window_imgl(file=file, image=image, lang=lang, action="list")


def uri_for_imgl_click(
    *,
    file: str = "layout.vql.json",
    image: str = "",
    text: str = "",
    label: str = "",
    element_id: str = "",
    window: str = "",
    lang: str = "eng",
) -> str:
    extra: dict[str, str | int] = {"action": "click", "lang": lang}
    if image:
        extra["image"] = image
    if text:
        extra["text"] = text
    if label:
        extra["label"] = label
    if element_id:
        extra["element_id"] = element_id
    if window:
        extra["window"] = window
    return _with_file("window/imgl", file=file, extra=extra)


def uri_for_imgl_type(
    *,
    file: str = "layout.vql.json",
    image: str = "",
    value: str = "",
    label: str = "",
    text: str = "",
    element_id: str = "",
    window: str = "",
    lang: str = "eng",
) -> str:
    extra: dict[str, str | int] = {"action": "type", "lang": lang, "value": value}
    if image:
        extra["image"] = image
    if label:
        extra["label"] = label
    if text:
        extra["text"] = text
    if element_id:
        extra["element_id"] = element_id
    if window:
        extra["window"] = window
    return _with_file("window/imgl", file=file, extra=extra)


def uri_for_window_diagnose(
    *,
    file: str = "app.vql.json",
    image: str = "",
    locale: str = "pl",  # European ISO 639-1
) -> str:
    extra: dict[str, str | int] = {"locale": locale}
    if image:
        extra["image"] = image
    return _with_file("window/diagnose", file=file, extra=extra)


def uri_for_window_compare(
    *,
    file: str = "app.vql.json",
    image: str = "",
) -> str:
    extra: dict[str, str | int] = {}
    if image:
        extra["image"] = image
    return _with_file("window/compare", file=file, extra=extra or None)


def uri_for_window_refresh(
    *,
    file: str = "app.vql.json",
    image: str = "",
    locale: str = "pl",
) -> str:
    extra: dict[str, str | int] = {"locale": locale}
    if image:
        extra["image"] = image
    return _with_file("window/refresh", file=file, extra=extra)


def parse_vql_uri(uri: str, *, default_file: str = "") -> VqlUri:
    parsed = urlparse(uri)
    if parsed.scheme != VQL_SCHEME:
        raise ValueError(f"expected vql:// URI, got: {uri}")
    selector = (parsed.netloc + parsed.path).strip("/") or "program"
    qs = parse_qs(parsed.query)
    file_param = (qs.get("file") or [""])[0] or default_file
    return VqlUri(scheme=VQL_SCHEME, selector=selector, file=file_param)
