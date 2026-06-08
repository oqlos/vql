"""VQL renderers — unified ``render(program)`` backends."""

from vql.renderers.base import VQLRenderer, VQLRendererAdapter, render_program
from vql.renderers.svg import SVGVQLRenderer, render_to_png, render_to_svg

__all__ = [
    "VQLRenderer",
    "VQLRendererAdapter",
    "render_program",
    "SVGVQLRenderer",
    "render_to_svg",
    "render_to_png",
    "PlaywrightVQLRenderer",
]


def __getattr__(name: str):  # pragma: no cover - lazy import
    """Lazily expose the Playwright renderer (keeps import light)."""
    if name == "PlaywrightVQLRenderer":
        from vql.renderers.playwright import PlaywrightVQLRenderer

        return PlaywrightVQLRenderer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
