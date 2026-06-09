"""Image heuristics for capture validation."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from vql.adopt.capture_types import require_pillow


def image_is_blank(path: Path, *, dark_threshold: int = 8) -> bool:
    """True when capture looks empty (all black / single dark color)."""
    require_pillow()
    from PIL import Image

    im = Image.open(path).convert("RGB")
    if im.size[0] < 2 or im.size[1] < 2:
        return True
    small = im.resize((32, 32))
    pixels = list(small.get_flattened_data())
    if not pixels:
        return True
    unique = set(pixels)
    if len(unique) == 1 and max(unique.pop()) < dark_threshold:
        return True
    if all(max(px) < dark_threshold for px in pixels):
        return True
    return False


def image_stats(path: str | Path, *, dark_threshold: int = 8) -> dict[str, Any]:
    """Return quick heuristics for a PNG/JPEG (blank detection, brightness, size)."""
    require_pillow()
    from PIL import Image

    p = Path(path).expanduser()
    if not p.is_file():
        return {"ok": False, "path": str(p), "error": "file not found"}

    im = Image.open(p).convert("RGB")
    w, h = im.size
    small = im.resize((32, 32))
    pixels = list(small.get_flattened_data())
    unique = len(set(pixels))
    brightness = [int(0.299 * r + 0.587 * g + 0.114 * b) for r, g, b in pixels]
    b_min, b_max = min(brightness), max(brightness)
    b_avg = sum(brightness) // len(brightness)
    top = Counter(pixels).most_common(3)
    is_blank = image_is_blank(p, dark_threshold=dark_threshold)
    return {
        "ok": True,
        "path": str(p),
        "width": w,
        "height": h,
        "bytes": p.stat().st_size,
        "unique_colors_sampled": unique,
        "brightness_min": b_min,
        "brightness_max": b_max,
        "brightness_avg": b_avg,
        "top_colors": [f"#{r:02X}{g:02X}{b:02X}" for (r, g, b), _ in top],
        "is_blank": is_blank,
    }
