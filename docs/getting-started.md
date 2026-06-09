# Getting started

## Wymagania

- Python 3.10+ (3.12 w `.venv` dev)
- Linux desktop (opcjonalnie: capture Wayland/GNOME)

## Instalacja dev (zalecana)

```bash
git clone <repo>/vql
cd vql
bash install-dev.sh
```

`install-dev.sh` instaluje:

| Grupa | Pakiety |
|-------|---------|
| Core | `vql[desktop,png]` |
| Sterowanie | `uri2vql`, `nlp2vql`, `dsl2vql`, `cli2vql`, `rest2vql`, `mcp2vql` |
| Obraz | `img2svg`, `uri2img2svg`, `dsl2img2svg` |
| img2nl (gdy `IMG2NL_ROOT`) | `img2nl[analyze]`, `img2vql`, `uri2vql[diagnose]` |

Zmienna `IMG2NL_ROOT` (domyślnie `../../wronai/img2nl`):

```bash
export IMG2NL_ROOT=~/github/wronai/img2nl
bash install-dev.sh
```

### Opcjonalne extras

```bash
pip install -e "packages/img2svg[opencv]"     # kontury OpenCV
pip install -e "packages/img2vql[ocr]"        # rapidocr auto-OCR
pip install -e "$IMG2NL_ROOT[translate]"      # offline argostranslate
pip install -e "packages/rest2vql[window]"  # REST window endpoints
pip install -e ~/github/semcod/imgl           # OCR + semantic UI
```

## Szybki start — rysowanie NL → SVG

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
# 1. Capture (GNOME/Wayland — patrz desktop-capture.md)
uri2vql capture-screen --interactive --out /tmp/screen.png

# 2. Jednym poleceniem: capture + analyze + diagnose
uri2vql capture-and-analyze --out /tmp/app.vql.json --diagnose

# 3. Lub krok po kroku
uri2vql analyze-window --image /tmp/screen.png --out /tmp/app.vql.json --grid 12
uri2vql adopt-ui --image /tmp/screen.png --out /tmp/ui.vql.json --locale pl
uri2img2svg query "img2svg://svg?path=/tmp/screen.png&out=/tmp/screen.svg"

# 4. Podsumowanie
uri2vql query "vql://window/summary?file=/tmp/app.vql.json&live=1&image=/tmp/screen.png"
```

Pełny skrypt: `bash examples/full-pipeline.sh`

## Przykłady

```bash
bash examples/live-capture-test.sh
VQL_TEST_IMAGE=/tmp/screen.png bash examples/full-pipeline.sh
bash examples/img2nl-vql-flow.sh /tmp/screen.png
```

Indeks: [examples/README.md](../examples/README.md)

## Testy

```bash
make test          # core + dsl2vql
make test-all      # wszystkie packages/
pytest packages/img2vql/tests packages/img2svg/tests packages/uri2img2svg/tests -q
```

## Następne kroki

1. [desktop-capture.md](desktop-capture.md) — czarny PNG na Wayland
2. [window-pipeline.md](window-pipeline.md) — pełny przepływ
3. [window-uri.md](window-uri.md) — referencja URI
4. [rest-window-api.md](rest-window-api.md) — REST dla agentów
5. [img2svg-uri.md](img2svg-uri.md) — wektoryzacja URI/DSL
