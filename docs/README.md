# Dokumentacja VQL

Indeks dokumentacji monorepo [vql](../README.md).

## Spis treści

### Start
| Dokument | Opis |
|----------|------|
| [getting-started.md](getting-started.md) | Instalacja, szybki start, dev stack |
| [packages.md](packages.md) | Wszystkie pakiety — kiedy którego użyć |
| [architecture.md](architecture.md) | Warstwy IR, DSL, adaptery |

### Screenshot → VQL
| Dokument | Opis |
|----------|------|
| [photo-roundtrip.md](photo-roundtrip.md) | **Fotografia ↔ VQL** — opis i odtworzenie, jakość, biblioteki |
| [vdisplay-imgl-automation.md](vdisplay-imgl-automation.md) | **vdisplay → imgl → VQL → LLM** (zalecane) |
| [desktop-capture.md](desktop-capture.md) | GNOME/Wayland, blank PNG, dwie ścieżki capture |
| [window-pipeline.md](window-pipeline.md) | Capture → analyze → detect → diagnose → SVG |
| [window-uri.md](window-uri.md) | `vql://window/*` URI + CLI `uri2vql` |

### API dla agentów
| Dokument | Opis |
|----------|------|
| [rest-window-api.md](rest-window-api.md) | REST `POST /v1/window/*` (port 8216) |
| [img2svg-uri.md](img2svg-uri.md) | `img2svg://` URI + `dsl2img2svg` |

### MCP tools (mcp2vql)
| Tool | Opis |
|------|------|
| `vql_detect_ui` | Detekcja okien, przycisków (img2vql) |
| `vql_compare_window` | Fingerprint vs program |
| `vql_refresh_window_metadata` | Odśwież metadata bez rebuild grid |
| `vql_diagnose_window` | Diagnose LLM routing (+ opcjonalny save) |
| `vql_query` | Dowolne `vql://` URI |

## Pakiety (README)

| Pakiet | README |
|--------|--------|
| Warstwa sterowania | [packages/README.md](../packages/README.md) |
| img2vql | [packages/img2vql/README.md](../packages/img2vql/README.md) |
| img2svg | [packages/img2svg/README.md](../packages/img2svg/README.md) |
| uri2img2svg | [packages/uri2img2svg/README.md](../packages/uri2img2svg/README.md) |
| dsl2img2svg | [packages/dsl2img2svg/README.md](../packages/dsl2img2svg/README.md) |

## Przykłady

Szczegóły: [examples/README.md](../examples/README.md)

| Skrypt | Cel |
|--------|-----|
| [live-capture-test.sh](../examples/live-capture-test.sh) | Capture + analyze + nlp2uri |
| [full-pipeline.sh](../examples/full-pipeline.sh) | Pełny pipeline: capture → detect → svg → diagnose |
| [img2nl-vql-flow.sh](../examples/img2nl-vql-flow.sh) | Fingerprint, refresh, compare; opcjonalnie imgl |
| [photo-roundtrip-test.py](../examples/photo-roundtrip-test.py) | Test fotografia ↔ VQL (próbki A/B/C, MSE, JSON) |
| [generate-demo-screen.py](../examples/generate-demo-screen.py) | Syntetyczny UI PNG (headless) |
| [scope-window.py](../examples/scope-window.py) | Przycięcie do okna fokusu (imgl) |

## Zewnętrzne zależności

| Projekt | Rola |
|---------|------|
| [wronai/vdisplay](https://github.com/wronai/vdisplay) | Zrzut z wirtualnego display (mirror, bez portalu) |
| [semcod/imgl](https://github.com/semcod/imgl) | OCR, semantyczny layout, `capture`, `interact --llm` |
| [wronai/img2nl](https://github.com/wronai/img2nl) | Heurystyki, i18n, offline translate, OCR trigger |

## Interfejsy — mapa

| Warstwa | Window / screenshot | SVG / wektoryzacja |
|---------|---------------------|-------------------|
| CLI | `uri2vql`, `img2vql` | `img2svg`, `uri2img2svg`, `dsl2img2svg` |
| URI | `vql://window/*` | `img2svg://vectorize\|svg\|vql` |
| REST | `POST /v1/window/*` | — (planowane) |
| MCP | `vql_detect_ui`, `vql_diagnose_window`, … | — |

## Status

- [TODO.md](../TODO.md)
- [CHANGELOG.md](../CHANGELOG.md)
