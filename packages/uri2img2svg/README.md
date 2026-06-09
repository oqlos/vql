# uri2img2svg

`img2svg://` URI layer for raster → SVG / VQL vectorization.

**Docs:** [../../docs/packages.md](../../docs/packages.md) · [../img2svg/README.md](../img2svg/README.md)

## Install

```bash
pip install -e packages/img2svg
pip install -e packages/uri2img2svg
pip install -e "packages/img2svg[opencv]"  # optional contours
```

## URIs

| URI | Action |
|-----|--------|
| `img2svg://vectorize?path=screen.png&grid=24` | Trace regions (JSON) |
| `img2svg://svg?path=screen.png&out=screen.svg` | Write SVG file |
| `img2svg://vql?path=screen.png&file=screen.vql.json` | Write VQL program |
| `img2svg://svg?path=screen.png&method=contours` | OpenCV contours |

## CLI

```bash
uri2img2svg query "img2svg://vectorize?path=/tmp/screen.png&grid=24"
uri2img2svg query "img2svg://svg?path=/tmp/screen.png&out=/tmp/screen.svg"
uri2img2svg query "img2svg://vql?path=/tmp/screen.png&file=/tmp/screen.vql.json"
```

## Python

```python
from uri2img2svg import query_uri, uri_for_vectorize

uri = uri_for_vectorize("/tmp/screen.png", out="/tmp/screen.svg", grid=24)
result = query_uri("img2svg://svg?path=/tmp/screen.png&out=/tmp/screen.svg")
```
