# vql


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.3-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$0.75-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-2.0h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $0.7483 (3 commits)
- 👤 **Human dev:** ~$200 (2.0h @ $100/h, 30min dedup)

Generated on 2026-06-09 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

**VQL (Visual Query Language)** — język wektorowego opisu fotografii, rysunków i zrzutów ekranu.

Samodzielna paczka Python z IR (`VQLProgram`), kompilatorem NL→VQL, walidacją i rendererami SVG/PNG. Sterowana przez DSL i bus CQRS/ES w paczkach `*2vql`.

**Dokumentacja:** [docs/README.md](docs/README.md) · **Przykłady:** [examples/README.md](examples/README.md)

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
# GNOME/Wayland: --interactive (docs/desktop-capture.md)
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
| Capture | `uri2vql capture-screen` | PNG (portal / grim / mss) |
| Grid adopt | `analyze-window` | scalone regiony + fingerprint |
| UI detect | `img2vql` / `adopt-ui` | okna, przyciski, bbox, relations |
| Wektoryzacja | `img2svg` / `uri2img2svg` | PNG → SVG / VQL |
| Diagnose | `diagnose-window` | routing LLM + auto-OCR |
| Compare | `compare-window` | phash — zmiana ekranu? |
| OCR semantyczny | `adopt-imgl` / imgl | tekst + role + interakcja |

Pipeline: [docs/window-pipeline.md](docs/window-pipeline.md) · Capture: [docs/desktop-capture.md](docs/desktop-capture.md)

## Przykłady

```bash
bash examples/live-capture-test.sh
bash examples/full-pipeline.sh
bash examples/img2nl-vql-flow.sh /tmp/screen.png
VQL_TEST_IMAGE=/tmp/screen.png bash examples/full-pipeline.sh
```

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
```

Szczegóły: [packages/README.md](packages/README.md) · [docs/packages.md](docs/packages.md)

## Status

- [TODO.md](TODO.md) — checklist + analiza
- [CHANGELOG.md](CHANGELOG.md) — historia zmian

## License

Licensed under Apache-2.0.
