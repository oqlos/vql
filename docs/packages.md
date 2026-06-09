# Pakiety — przegląd i linki

## Core

| Pakiet | Instalacja | Dokumentacja |
|--------|------------|--------------|
| **vql** | `pip install vql` | [README](../README.md) |
| **dsl2vql** | `pip install -e packages/dsl2vql` | [packages/README.md](../packages/README.md) |

## Adaptery `*2vql`

| Pakiet | Port | Rola | Docs |
|--------|------|------|------|
| **uri2vql** | — | `vql://` URI, `window/*`, capture | [window-uri.md](window-uri.md) |
| **nlp2vql** | — | NL → DSL | [packages/README.md](../packages/README.md) |
| **cli2vql** | — | Shell REPL | — |
| **rest2vql** | 8216 | REST FastAPI + `/v1/window/*` | [rest-window-api.md](rest-window-api.md) |
| **mcp2vql** | — | MCP stdio (window tools) | [docs/README.md](README.md#mcp-tools-mcp2vql) |

## Obraz → VQL / SVG

| Pakiet | Wersja | README |
|--------|--------|--------|
| **img2vql** | 0.2.0 | [packages/img2vql/README.md](../packages/img2vql/README.md) |
| **img2svg** | 0.1.0 | [packages/img2svg/README.md](../packages/img2svg/README.md) |
| **uri2img2svg** | 0.1.0 | [packages/uri2img2svg/README.md](../packages/uri2img2svg/README.md) |
| **dsl2img2svg** | 0.1.0 | [packages/dsl2img2svg/README.md](../packages/dsl2img2svg/README.md) |

### Kiedy którego użyć

| Potrzeba | Pakiet | Komenda / URI |
|----------|--------|---------------|
| Zrzut ekranu (LLM / vdisplay) | imgl + vdisplay | `imgl capture -o screen.png` |
| Zrzut ekranu (portal) | uri2vql | `capture-screen --interactive` |
| Siatka kolorów + fingerprint | uri2vql | `analyze-window` |
| Okna, przyciski, bbox | img2vql | `detect` / `adopt-ui` |
| Relacje contains | img2vql | `adopt` → `scene.relations` |
| Plik SVG z PNG | img2svg / uri2img2svg | `img2svg svg` / `img2svg://svg?...` |
| VQL wektorów | img2svg / uri2img2svg | `img2svg vql` / `img2svg://vql?...` |
| DSL wektoryzacja | dsl2img2svg | `VECTORIZE PATH ... OUT ...` |
| Czy wysłać do LLM? | img2vql + img2nl | `diagnose-window` |
| Auto-OCR tekstu UI | img2vql[ocr] | w refresh/diagnose metadata |
| OCR + klikalne elementy | imgl | `adopt-imgl` / `vql://window/imgl` |
| NL → klik na pulpicie | imgl | `interact --llm --execute` |
| Czy ekran się zmienił? | img2vql | `compare-window` |
| REST dla agentów | rest2vql | `POST /v1/window/detect` |
| MCP dla agentów | mcp2vql | `vql_detect_ui`, `vql_diagnose_window` |

## Zależności zewnętrzne

```bash
export IMG2NL_ROOT=~/github/wronai/img2nl
pip install -e "$IMG2NL_ROOT[analyze,translate,ocr]"

pip install -e ~/github/semcod/imgl[vdisplay]   # capture + OCR + LLM
pip install -e ~/github/wronai/vdisplay[pillow] # sam vdisplay (imgl instaluje też)
```

## Extras pip

```bash
pip install vql[desktop]              # pillow, mss
pip install vql[png]                  # cairosvg
pip install img2svg[opencv]           # kontury
pip install img2vql[ocr]              # rapidocr auto-OCR
pip install img2nl[translate]         # offline argostranslate
pip install rest2vql[window]          # window REST endpoints
pip install mcp2vql[window]           # window MCP tools
```

## Dev

```bash
bash install-dev.sh
make test-all
```

## Przykłady

[examples/README.md](../examples/README.md)
