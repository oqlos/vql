# VQL - Visual Query Language

## before
```bash
uri2vql pipeline-analyze --image /tmp/screen.png --out app.vql.json --llm
```
![1.png](docs/1.png)

## after
```bash
uri2vql vql-to-image --program app.vql.json --out app.render.png
```
![2.png](docs/2.png)

VQL objects
[app.vql.json](docs/app.vql.json)
```bash
{
  "version": "1.0",
  "render_target": "svg",
  "scene": {
    "width": 2560.0,
    "height": 1600.0,
    "background": "#FFFFFF",
    "url": "file:///tmp/screen.png",
    "app": "desktop",
    "layers": [
      {
        "id": "screen_regions",
        "objects": [
          {
            "id": "region_000",
            "primitives": [
              {
                "shape_type": "rectangle",
                "params": {
                  "width": 213.0,
                  "height": 133.0
                }
              }
            ],
            "style": {
              "color": "#2F342E",
              "fill": true,
              "stroke_width": 0.0,
```


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.5-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$7.78-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-3.6h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $7.7792 (6 commits)
- 👤 **Human dev:** ~$359 (3.6h @ $100/h, 30min dedup)

Generated on 2026-06-09 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

**VQL (Visual Query Language)** — język wektorowego opisu fotografii, rysunków i zrzutów ekranu.

Samodzielna paczka Python z IR (`VQLProgram`), kompilatorem NL→VQL, walidacją i rendererami SVG/PNG. Sterowana przez DSL i bus CQRS/ES w paczkach `*2vql`.

**Ekosystem:** SUMD (opis) → DOQL (deklaracja) → Makefile/taskfile (automation) → testql (weryfikacja)

**Dokumentacja:** [docs/README.md](docs/README.md) · **Przykłady:** [examples/README.md](examples/README.md) · **SUMD:** [SUMD.md](SUMD.md)

## Instalacja

```bash
pip install vql              # core
pip install vql[png]         # eksport PNG (cairosvg)
pip install vql[desktop]     # zrzut ekranu (pillow, mss)
bash install-dev.sh          # pełny stack dev
```

## Szybki start — rysowanie

```python
from vql import nl_to_program, render_to_svg

program = nl_to_program("narysuj czerwone koło", width=400, height=400)
svg = render_to_svg(program)
```

```bash
dsl2vql -c 'COMPILE "narysuj niebieski kwadrat"'
rest2vql serve --port 8216
```

## Szybki start — zrzut ekranu → VQL

```bash
# Automatyzacja LLM: vdisplay → imgl (bez dialogu GNOME, gdy mirror działa)
imgl capture -o /tmp/screen.png --verify --analyze --lang eng+pol

# Alternatywa: portal GNOME (docs/desktop-capture.md)
uri2vql capture-screen --interactive --out /tmp/screen.png

# All-in-one
uri2vql capture-and-analyze --out app.vql.json --diagnose

# Lub krok po kroku
uri2vql analyze-window --image /tmp/screen.png --out app.vql.json --grid 12
uri2vql adopt-ui --image /tmp/screen.png --out ui.vql.json --locale pl
uri2img2svg query "img2svg://svg?path=/tmp/screen.png&out=/tmp/screen.svg"

uri2vql query "vql://window/summary?file=app.vql.json&live=1&image=/tmp/screen.png"
```

Pełny skrypt: `bash examples/full-pipeline.sh`

## Fotografia ↔ VQL (roundtrip)

Opis z obrazu i odtworzenie z metadanych — zależnie od typu obrazu:

```bash
# Test roundtrip (próbki + raport fidelity)
python examples/photo-roundtrip-test.py
make test-roundtrip

# Opis mozaiką kolorów
img2svg vql photo.png --out photo.vql.json --grid 20

# Wektoryzacja kolorowa (lepsza dla płaskich kształtów)
pip install 'img2svg[vtracer]'
img2svg vql photo.png --out photo.vql.json --method vtracer

# Odtworzenie
python -c "
from vql import VQLProgram, render_to_png
import json
p = VQLProgram.from_dict(json.load(open('photo.vql.json')))
render_to_png(p, 'reconstructed.png')
"
```

Macierz jakości i biblioteki: [docs/photo-roundtrip.md](docs/photo-roundtrip.md)

## Interfejsy

| Warstwa | Window / screenshot | SVG |
|---------|---------------------|-----|
| CLI | `uri2vql`, `img2vql` | `img2svg`, `uri2img2svg`, `dsl2img2svg` |
| URI | `vql://window/*` | `img2svg://vectorize\|svg\|vql` |
| REST | `POST /v1/window/*` :8216 | planowane |
| MCP | `vql_detect_ui`, `vql_diagnose_window`, … | — |

REST: [docs/rest-window-api.md](docs/rest-window-api.md) · URI: [docs/window-uri.md](docs/window-uri.md) · SVG: [docs/img2svg-uri.md](docs/img2svg-uri.md)

## Desktop adopt + img2nl

| Etap | Narzędzie | Co robi |
|------|-----------|---------|
| Capture | `imgl capture` (vdisplay) / `uri2vql capture-screen` | PNG + provenance / portal |
| Grid adopt | `analyze-window` | scalone regiony + fingerprint |
| UI detect | `img2vql` / `adopt-ui` | okna, przyciski, bbox, relations |
| Wektoryzacja | `img2svg` / `uri2img2svg` | PNG → SVG / VQL |
| Diagnose | `diagnose-window` | routing LLM + auto-OCR |
| Compare | `compare-window` | phash — zmiana ekranu? |
| OCR semantyczny | `adopt-imgl` / imgl | tekst + role + interakcja |

Pipeline: [docs/window-pipeline.md](docs/window-pipeline.md) · LLM capture: [docs/vdisplay-imgl-automation.md](docs/vdisplay-imgl-automation.md) · Portal: [docs/desktop-capture.md](docs/desktop-capture.md)

## Przykłady

```bash
bash examples/live-capture-test.sh
bash examples/full-pipeline.sh
bash examples/img2nl-vql-flow.sh /tmp/screen.png
VQL_TEST_IMAGE=/tmp/screen.png bash examples/full-pipeline.sh
```

## Development

```bash
make install-dev    # pełny stack *2vql
make test           # pytest core + dsl2vql
make test-all       # wszystkie pakiety
make serve          # rest2vql :8216
make goal           # test + commit + publish (goal.yaml)
bash project.sh     # SUMD + DOQL + testql + analiza
```

Zmienne LLM: skopiuj `.env.example` → `.env` (`OPENROUTER_API_KEY`, `LLM_MODEL`).

## Struktura monorepo

```
src/vql/              — domena (schema, compiler, renderers, adopt/window)
packages/
  dsl2vql/ uri2vql/ nlp2vql/ cli2vql/ rest2vql/ mcp2vql/
  img2vql/            — detekcja UI + img2nl diagnose (v0.2)
  img2svg/            — obraz → SVG / VQL (v0.1)
  uri2img2svg/        — img2svg:// URI (v0.1)
  dsl2img2svg/        — VECTORIZE / TO_VQL DSL (v0.1)
docs/                 — dokumentacja
examples/             — skrypty demo (README w examples/)
testql-scenarios/     — kontrakty testql (CLI, pytest)
```

**Skala (SUMD):** 151 modułów · 278 funkcji · ~12.5k LOC · CC̄=4.2

Szczegóły: [packages/README.md](packages/README.md) · [docs/packages.md](docs/packages.md)

## Status

- [TODO.md](TODO.md) — checklist + analiza
- [CHANGELOG.md](CHANGELOG.md) — historia zmian
- [SUMD.md](SUMD.md) — auto-opis projektu (DOQL, testql, call graph)

## License

Licensed under Apache-2.0.
