# img2svg

Raster image → SVG / VQL vectorization for the VQL monorepo.

**Docs:** [../../docs/window-pipeline.md](../../docs/window-pipeline.md) · [../../docs/packages.md](../../docs/packages.md)

## Methods

| Method | Deps | Best for | Typical output |
|--------|------|----------|----------------|
| `regions` (default) | Pillow | UI screenshots, flat-color graphics | ~200–300 merged rects |
| `contours` | OpenCV | Edge outlines | ~30–50 paths |

For photo-realistic tracing use external tools (vtracer, potrace) — planned as low-priority TODO.

## Install

```bash
pip install -e packages/img2svg
pip install -e "packages/img2svg[opencv]"  # contour mode
```

## CLI

```bash
img2svg trace screenshot.png --grid 24
img2svg svg screenshot.png --out screen.svg
img2svg vql screenshot.png --out screen.vql.json
img2svg svg screenshot.png --method contours  # needs opencv
```

## Python

```python
from img2svg import image_to_svg, image_to_vql, trace_image_regions

image_to_svg("/tmp/screen.png", out_path="/tmp/screen.svg", grid=24)
image_to_vql("/tmp/screen.png", out_program="/tmp/screen.vql.json")
trace_image_regions("/tmp/screen.png", grid=24)
```

## Render VQL → SVG (existing)

Programs from `img2svg vql` or `analyze-window` can be rendered:

```bash
dsl2vql -c 'RENDER app.vql.json OUT preview.svg'
```

Or Python: `from vql import render_to_svg`

## Pipeline with img2vql

```bash
# semantic UI bboxes
uri2vql adopt-ui --image /tmp/screen.png --out ui.vql.json

# color vectorization
img2svg svg /tmp/screen.png --out screen.svg --grid 24
img2svg svg /tmp/screen.png --out contours.svg --method contours
```

## Related

- [img2vql](../img2vql/README.md) — UI element detection
- [docs/desktop-capture.md](../../docs/desktop-capture.md) — getting a valid PNG on Wayland
