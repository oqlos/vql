# dsl2img2svg

DSL verbs for raster → SVG / VQL via [uri2img2svg](../uri2img2svg/README.md).

## Verbs

| Verb | Example |
|------|---------|
| `VECTORIZE` | `VECTORIZE PATH screen.png OUT screen.svg GRID 24` |
| `TO_VQL` | `TO_VQL PATH screen.png OUT screen.vql.json` |
| `QUERY` | `QUERY img2svg://vectorize?path=screen.png&grid=24` |

## CLI

```bash
dsl2img2svg -c 'VECTORIZE PATH /tmp/screen.png OUT /tmp/screen.svg GRID 24'
dsl2img2svg -c 'TO_VQL PATH /tmp/screen.png OUT /tmp/screen.vql.json'
dsl2img2svg -c 'QUERY img2svg://svg?path=/tmp/screen.png&out=/tmp/screen.svg'
```
