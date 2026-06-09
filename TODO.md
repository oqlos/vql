# vql — TODO

Ostatnia aktualizacja: 2026-06-08.

**Docs:** [docs/README.md](docs/README.md) · **Examples:** [examples/README.md](examples/README.md)

---

## Zrobione

### Window pipeline + img2nl
- [x] fingerprint, special_hits, scene_class, llm_hint w metadata
- [x] URI/CLI: compare, refresh, diagnose+save, summary?live=1
- [x] `capture-and-analyze` — portal capture + analyze + diagnose
- [x] Auto-OCR: rapidocr → imgl gdy text_likelihood ([img2vql/metadata.py](packages/img2vql/src/img2vql/metadata.py))
- [x] `img2vql[ocr]` extra

### img2vql v0.2
- [x] detect / adopt / describe_ui
- [x] `scene.relations` contains (window > panel > button)

### img2svg ekosystem
- [x] img2svg — regions, contours
- [x] uri2img2svg — `img2svg://vectorize|svg|vql`
- [x] dsl2img2svg — VECTORIZE, TO_VQL, QUERY

### REST + MCP
- [x] rest2vql `POST /v1/window/*` — [docs/rest-window-api.md](docs/rest-window-api.md)
- [x] mcp2vql: detect, compare, refresh, diagnose

### Grid adopt
- [x] merge_regions w screenshot_to_program
- [x] min_region_px filter

### Dokumentacja + examples
- [x] docs/ — pełny indeks (9 plików)
- [x] examples/README.md — indeks skryptów + zmienne env
- [x] examples/full-pipeline.sh — capture → detect → svg → diagnose
- [x] examples/live-capture-test.sh, img2nl-vql-flow.sh
- [x] examples/generate-demo-screen.py, scope-window.py
- [x] README, packages/README, CHANGELOG

---

## Do zrobienia

### Średni priorytet
- [ ] REST `POST /v1/img2svg/*` — mirror uri2img2svg
- [ ] OCR label → `ui_elements.metadata.label` (z auto-OCR / imgl)
- [ ] `rest2img2nl` / `mcp2img2nl` — adaptery w repo wronai/img2nl
- [ ] CI: `img2nl-vql-flow.sh` w pipeline (synthetic PNG, bez imgl)

### Niski priorytet
- [ ] EventStore fingerprint przy PATCH
- [ ] img2svg sidecar SVG z bbox ui_elements
- [ ] imgl + img2vql wspólna metadata schema
- [ ] img2nl YOLO detect extra
- [ ] vtracer/potrace backend
- [ ] relations: aligned_with, above

---

## Mapa interfejsów

| Warstwa | Window | SVG | Docs |
|---------|--------|-----|------|
| CLI | uri2vql, img2vql | img2svg, uri2img2svg, dsl2img2svg | [window-uri.md](docs/window-uri.md) |
| URI | `vql://window/*` | `img2svg://*` | [img2svg-uri.md](docs/img2svg-uri.md) |
| REST | `/v1/window/*` | — | [rest-window-api.md](docs/rest-window-api.md) |
| MCP | 4 window tools | — | [docs/README.md](docs/README.md) |
| Examples | full-pipeline, live-capture, img2nl-flow | w full-pipeline | [examples/README.md](examples/README.md) |

---

## Następny krok

1. REST `/v1/img2svg/svg` — HTTP wektoryzacja dla agentów
2. Propagacja OCR text do ui_elements po auto_ocr
3. CI job: `bash examples/img2nl-vql-flow.sh` (synthetic, bez imgl)
