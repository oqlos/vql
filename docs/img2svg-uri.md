# img2svg:// URI i DSL

Wektoryzacja obrazu przez URI i DSL (obok CLI `img2svg`).

## Pakiety

| Pakiet | Rola |
|--------|------|
| [img2svg](../packages/img2svg/README.md) | Core: trace, svg_emit, to_vql |
| [uri2img2svg](../packages/uri2img2svg/README.md) | `img2svg://` URI + CLI |
| [dsl2img2svg](../packages/dsl2img2svg/README.md) | `VECTORIZE`, `TO_VQL`, `QUERY` |

## Instalacja

```bash
pip install -e packages/img2svg
pip install -e packages/uri2img2svg
pip install -e packages/dsl2img2svg
pip install -e "packages/img2svg[opencv]"
```

## URI

```
img2svg://vectorize?path=/tmp/screen.png&grid=24
img2svg://svg?path=/tmp/screen.png&out=/tmp/screen.svg&grid=24
img2svg://vql?path=/tmp/screen.png&file=/tmp/screen.vql.json
img2svg://svg?path=/tmp/screen.png&method=contours&out=/tmp/c.svg
```

## CLI

```bash
uri2img2svg query "img2svg://vectorize?path=/tmp/screen.png&grid=24"
uri2img2svg query "img2svg://svg?path=/tmp/screen.png&out=/tmp/screen.svg"
```

## DSL

```bash
dsl2img2svg -c 'VECTORIZE PATH /tmp/screen.png OUT /tmp/screen.svg GRID 24'
dsl2img2svg -c 'TO_VQL PATH /tmp/screen.png OUT /tmp/screen.vql.json'
dsl2img2svg -c 'QUERY img2svg://vectorize?path=/tmp/screen.png'
```

## Pipeline z window/*

```bash
uri2vql capture-screen --interactive --out /tmp/screen.png
uri2vql adopt-ui --image /tmp/screen.png --out /tmp/ui.vql.json
uri2img2svg query "img2svg://svg?path=/tmp/screen.png&out=/tmp/screen.svg&grid=24"
```

## Przykłady

```bash
bash examples/full-pipeline.sh          # zawiera krok img2svg
VQL_TEST_IMAGE=/tmp/screen.png bash examples/full-pipeline.sh
```

→ [examples/README.md](../examples/README.md) · [window-pipeline.md](window-pipeline.md)
