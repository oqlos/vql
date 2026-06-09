# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.10] - 2026-06-09

### Fixed
- Fix unused-imports issues (ticket-8e666f5d)
- Fix ai-boilerplate issues (ticket-e0e0ab6d)
- Fix unused-imports issues (ticket-057cf9dc)
- Fix ai-boilerplate issues (ticket-a6d9ecee)
- Fix string-concat issues (ticket-3e3bfd3b)
- Fix unused-imports issues (ticket-19c95c44)
- Fix unused-imports issues (ticket-efcbfb1e)
- Fix unused-imports issues (ticket-daf72a7d)
- Fix unused-imports issues (ticket-6da2a8ff)
- Fix ai-boilerplate issues (ticket-3990d59d)
- Fix unused-imports issues (ticket-bc82e83e)
- Fix string-concat issues (ticket-abf26244)
- Fix unused-imports issues (ticket-c0d7a135)
- Fix string-concat issues (ticket-ff5032fd)
- Fix unused-imports issues (ticket-576bab90)
- Fix unused-imports issues (ticket-decf1bdf)
- Fix magic-numbers issues (ticket-af63ef32)
- Fix string-concat issues (ticket-6b15430f)
- Fix unused-imports issues (ticket-8a867444)
- Fix unused-imports issues (ticket-96185ba6)
- Fix magic-numbers issues (ticket-0f7890e8)
- Fix unused-imports issues (ticket-bf838267)
- Fix unused-imports issues (ticket-d3cdea36)
- Fix magic-numbers issues (ticket-f4a4b7eb)
- Fix unused-imports issues (ticket-8a571a4a)
- Fix magic-numbers issues (ticket-43fe4d81)
- Fix unused-imports issues (ticket-eee4c1b8)
- Fix ai-boilerplate issues (ticket-7d1ffd9b)
- Fix unused-imports issues (ticket-d63d2189)
- Fix string-concat issues (ticket-c3de3b8f)
- Fix unused-imports issues (ticket-f1f5c59f)
- Fix magic-numbers issues (ticket-48bfab49)
- Fix unused-imports issues (ticket-8a25b787)
- Fix magic-numbers issues (ticket-d2c1408e)
- Fix string-concat issues (ticket-c1c2051c)
- Fix unused-imports issues (ticket-e87661a6)
- Fix magic-numbers issues (ticket-26e77a10)
- Fix unused-imports issues (ticket-1fd2d0c8)
- Fix magic-numbers issues (ticket-5c52a68e)
- Fix ai-boilerplate issues (ticket-81f97908)
- Fix unused-imports issues (ticket-eb25a27a)
- Fix magic-numbers issues (ticket-83cc4d96)
- Fix unused-imports issues (ticket-4129ca21)
- Fix unused-imports issues (ticket-a873a55c)
- Fix string-concat issues (ticket-6297287f)
- Fix unused-imports issues (ticket-de4c3522)
- Fix magic-numbers issues (ticket-17e6563c)
- Fix string-concat issues (ticket-28425684)
- Fix unused-imports issues (ticket-427bd01d)
- Fix magic-numbers issues (ticket-faea61b1)
- Fix string-concat issues (ticket-45bc2485)
- Fix unused-imports issues (ticket-21e70bbe)
- Fix magic-numbers issues (ticket-a19a8d81)
- Fix unused-imports issues (ticket-d13efe8b)
- Fix ai-boilerplate issues (ticket-c09ede63)
- Fix unused-imports issues (ticket-c44d7d5e)
- Fix unused-imports issues (ticket-3a99c323)
- Fix ai-boilerplate issues (ticket-3bb4df62)
- Fix unused-imports issues (ticket-4d166942)
- Fix unused-imports issues (ticket-e57a5c56)
- Fix ai-boilerplate issues (ticket-436cd286)
- Fix unused-imports issues (ticket-dc4069d3)
- Fix magic-numbers issues (ticket-d75fa5c9)
- Fix ai-boilerplate issues (ticket-a5ef0b2d)
- Fix unused-imports issues (ticket-8d4aa7f8)
- Fix magic-numbers issues (ticket-d4f17b07)
- Fix unused-imports issues (ticket-e3990176)
- Fix magic-numbers issues (ticket-38166679)
- Fix unused-imports issues (ticket-806125af)
- Fix ai-boilerplate issues (ticket-f6b9f81a)
- Fix string-concat issues (ticket-cd9d2ee1)
- Fix unused-imports issues (ticket-0b9a1932)
- Fix unused-imports issues (ticket-eb9ebfae)
- Fix unused-imports issues (ticket-ae4fef90)
- Fix magic-numbers issues (ticket-47bc9ec0)
- Fix ai-boilerplate issues (ticket-32e8ee8a)
- Fix unused-imports issues (ticket-b9f60342)
- Fix magic-numbers issues (ticket-eae11564)
- Fix unused-imports issues (ticket-d05b0eac)
- Fix magic-numbers issues (ticket-4bd3e952)
- Fix string-concat issues (ticket-08384f5b)
- Fix unused-imports issues (ticket-c5168216)
- Fix unused-imports issues (ticket-f83889cc)
- Fix unused-imports issues (ticket-768744b5)
- Fix string-concat issues (ticket-bfb11370)
- Fix unused-imports issues (ticket-85b9f059)
- Fix magic-numbers issues (ticket-133bcadd)
- Fix unused-imports issues (ticket-302606cf)
- Fix string-concat issues (ticket-45576b5a)
- Fix unused-imports issues (ticket-dc3a69a1)
- Fix magic-numbers issues (ticket-aa4961c7)
- Fix unused-imports issues (ticket-fbfe0729)
- Fix magic-numbers issues (ticket-54003a1a)
- Fix ai-boilerplate issues (ticket-2851b104)
- Fix unused-imports issues (ticket-2884aeb6)
- Fix unused-imports issues (ticket-6a5bf3de)
- Fix magic-numbers issues (ticket-18d718a2)
- Fix unused-imports issues (ticket-7efa2b0b)
- Fix magic-numbers issues (ticket-aa07c23c)
- Fix llm-generated-code issues (ticket-3b8e7d2c)

## [Unreleased]

### Added
- **img2svg[vtracer]** — `trace_vtracer`, CLI `--method vtracer` (kolorowe ścieżki SVG)
- **PathGenerator** — render `shape_type=path` z atrybutu `d` (vtracer/OpenCV roundtrip)
- **tests/test_photo_roundtrip.py** — NL roundtrip, img2svg background, vtracer, render PNG
- **make test-roundtrip** — pytest + `examples/photo-roundtrip-test.py`

### Changed
- **img2svg** — `trace_to_vql_program` ustawia `scene.background` z dominującego regionu
- **SVGRenderer** — tło z `program.scene.background` (nie hardcoded white)
- **parse_svg_path** — `center=False` zachowuje współrzędne SVG (bez skali ×100)
- **install-dev.sh** — `img2svg[vectorize]` (opencv + vtracer)

### Docs
- **photo-roundtrip.md** — pełna dokumentacja: klasy A/B/C, wyniki MSE, macierz, biblioteki, CI
- **photo-roundtrip-sample.vql.json** — przykładowy fragment VQLProgram
- **examples/README.md** — sekcja photo roundtrip + `make test-roundtrip`
- **examples/photo-roundtrip-test.py** — próbki product/natural/metadata_only
- **vdisplay-imgl-automation.md** — vdisplay → imgl → VQL → LLM (zalecana ścieżka capture)
- README, window-pipeline, desktop-capture, getting-started — dwie ścieżki capture (imgl vs uri2vql)

### Planned
- REST `POST /v1/img2svg/*` — mirror uri2img2svg
- OCR label → `ui_elements.metadata.label` (z auto-OCR / imgl)
- CI: `img2nl-vql-flow.sh` w pipeline (synthetic PNG, bez imgl)

## [0.1.4] - 2026-06-09

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update docs/README.md
- Update docs/desktop-capture.md
- Update docs/getting-started.md
- Update docs/packages.md
- Update docs/photo-roundtrip-sample.vql.json
- ... and 7 more files

### Test
- Update testql-scenarios/generated-cli-tests.testql.toon.yaml
- Update testql-scenarios/generated-from-pytests.testql.toon.yaml
- Update tests/test_photo_roundtrip.py
- Update tests/test_vql.py

### Other
- Update Makefile
- Update app.doql.less
- Update app.vql.events.pb
- Update examples/photo-roundtrip-test.py
- Update install-dev.sh
- Update packages/img2svg/pyproject.toml
- Update packages/img2svg/src/img2svg/__init__.py
- Update packages/img2svg/src/img2svg/cli.py
- Update packages/img2svg/src/img2svg/svg_emit.py
- Update packages/img2svg/src/img2svg/to_vql.py
- ... and 21 more files

## [0.1.3] - 2026-06-09

### Added
- **SUMD.md** — auto-opis projektu (metadata, DOQL, testql, call graph, 151 mod)
- **testql-scenarios/** — kontrakty CLI (`generated-cli-tests`) i integracji pytest (`generated-from-pytests`)
- **app.doql.less** — deklaracja DOQL (workflows: install, dev, build, test, lint, fmt)
- **goal.yaml** — semver, conventional commits, keep-a-changelog
- **uri2img2svg v0.1** — `img2svg://vectorize|svg|vql` URI + CLI ([docs/img2svg-uri.md](docs/img2svg-uri.md))
- **dsl2img2svg v0.1** — `VECTORIZE`, `TO_VQL`, `QUERY img2svg://` DSL verbs
- **img2vql** — auto-OCR fallback (rapidocr → imgl) when `text_likelihood` but no OCR text; extra `[ocr]`
- **mcp2vql** — `vql_diagnose_window` tool (diagnose + optional save)
- **rest2vql** — `POST /v1/window/{detect,compare,refresh,diagnose,analyze,adopt,summary}` ([docs/rest-window-api.md](docs/rest-window-api.md))
- **mcp2vql** — MCP tools: `vql_detect_ui`, `vql_compare_window`, `vql_refresh_window_metadata`
- **uri2vql** — `capture-and-analyze` CLI (interactive capture + analyze + optional diagnose --save)
- **vql.adopt.window** — `merge_regions=True` in `screenshot_to_program` (fewer redundant grid cells)
- **img2vql** — `scene.relations` with `contains` (window > panel > button nesting)
- **uri2vql** — `vql://window/summary?live=1` refreshes metadata before summary
- **img2vql v0.2** — UI detection: windows, panels, titlebar, toolbar, buttons with pixel bboxes
- **img2vql** — `detect`, `adopt`, `describe_ui_layout`, layer `ui_elements` in VQL
- **img2svg v0.1** — raster → SVG / VQL (`regions` color merge, `contours` via OpenCV)
- **uri2vql** — CLI: `detect-window`, `adopt-ui`, `adopt-imgl`; URI: `window/detect`, `window/adopt`, `window/imgl`
- **uri2vql** — `analyze-window --interactive` for GNOME/Wayland portal capture
- **vql.adopt.window** — blank PNG rejection in `analyze_screenshot`
- **docs/** — getting-started, desktop-capture, window-pipeline, window-uri, packages, architecture
- **examples/** — `live-capture-test.sh` (interactive capture), `img2nl-vql-flow.sh` (fingerprint flow)
- **img2vql** — fingerprint compare, metadata refresh, diagnose `--save`
- **uri2vql** — `compare-window`, `refresh-window`; URI `window/compare`, `window/refresh`

### Changed
- Version bump **0.1.2 → 0.1.3** (`VERSION`, `pyproject.toml`)
- `requires-python` **>=3.10** (było dokumentowane jako 3.9+)
- README — sekcja Development (Makefile, project.sh), link SUMD, metryki projektu
- `packages/README.md` — img2vql, img2svg, extended mermaid diagram
- `install-dev.sh` — installs img2svg; img2vql when img2nl present
- `Makefile` — PACKAGES includes img2svg, uri2img2svg, dsl2img2svg

### Docs
- `docs/` — pełny indeks (9 plików), MCP tools, interfejsy
- `examples/README.md` — indeks skryptów + zmienne env
- `examples/full-pipeline.sh` — end-to-end demo
- `TODO.md` — mapa interfejsów + następne kroki (zsynchronizowane z SUMD)
- Package READMEs: img2vql, img2svg, uri2img2svg, dsl2img2svg

## [0.1.2] - 2026-06-08

### Docs
- Update README.md

### Other
- Update app.vql.events.pb

## [0.1.1] - 2026-06-08

### Docs
- Update README.md
- Update packages/CONTROL_LAYER_PROMPT.template.md
- Update packages/README.md

### Test
- Update tests/test_vql.py

### Other
- Update .gitignore
- Update Makefile
- Update VERSION
- Update app.vql.events.pb
- Update install-dev.sh
- Update packages/cli2vql/pyproject.toml
- Update packages/cli2vql/src/cli2vql/__init__.py
- Update packages/cli2vql/src/cli2vql/cli.py
- Update packages/dsl2vql/proto/dsl2vql/v1/command.proto
- Update packages/dsl2vql/proto/dsl2vql/v1/result.proto
- ... and 46 more files

## [0.0.1] - 2026-06-08

### Other
- Update .idea/.gitignore
- Update .idea/inspectionProfiles/Project_Default.xml
- Update .idea/inspectionProfiles/profiles_settings.xml
- Update .idea/modules.xml
- Update .idea/vcs.xml
- Update .idea/vql.iml
