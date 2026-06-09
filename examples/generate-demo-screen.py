#!/usr/bin/env python3
"""Generate a synthetic UI screenshot for headless img2nl / VQL demos."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def write_demo_screen(path: Path, *, width: int = 640, height: int = 420) -> Path:
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    image = Image.new("RGB", (width, height), color=(32, 32, 36))
    draw = ImageDraw.Draw(image)
    title_font = _load_font(16)
    body_font = _load_font(18)
    button_font = _load_font(17)

    # Desktop hint (orphan text for imgl)
    draw.text((12, 10), "Desktop", fill=(180, 180, 190), font=title_font)

    # Dialog window
    win = (80, 60, width - 80, height - 60)
    draw.rectangle(win, outline=(100, 100, 110), width=2, fill=(245, 245, 248))
    title_bar = (win[0], win[1], win[2], win[1] + 34)
    draw.rectangle(title_bar, fill=(70, 120, 200))
    draw.text((win[0] + 12, win[1] + 8), "Settings", fill=(255, 255, 255), font=title_font)

    label = "Username"
    label_x, label_y = win[0] + 24, win[1] + 72
    draw.text((label_x, label_y), label, fill=(30, 30, 35), font=body_font)

    input_box = (win[0] + 130, win[1] + 64, win[2] - 24, win[1] + 98)
    draw.rectangle(input_box, outline=(120, 120, 130), width=1, fill=(255, 255, 255))
    draw.text((input_box[0] + 10, input_box[1] + 8), "tom", fill=(20, 20, 25), font=body_font)

    button = (win[2] - 110, win[3] - 52, win[2] - 24, win[3] - 16)
    draw.rectangle(button, outline=(80, 80, 90), width=1, fill=(220, 225, 235))
    draw.text((button[0] + 18, button[1] + 8), "Save", fill=(0, 0, 0), font=button_font)

    image.save(path)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("/tmp/vql-img2nl-demo.png"),
        help="PNG output path",
    )
    args = parser.parse_args()
    out = write_demo_screen(args.output)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
