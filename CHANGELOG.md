# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
- README — Desktop adopt + img2nl section, links to `docs/`
- `packages/README.md` — img2vql, img2svg, extended mermaid diagram
- `install-dev.sh` — installs img2svg; img2vql when img2nl present
- `Makefile` — PACKAGES includes img2svg

### Docs
- `docs/` — pełny indeks (9 plików), MCP tools, interfejsy
- `examples/README.md` — indeks skryptów + zmienne env
- `examples/full-pipeline.sh` — end-to-end demo
- `TODO.md` — mapa interfejsów + następne kroki
- Package READMEs: img2vql, img2svg, uri2img2svg, dsl2img2svg

## [0.1.3] - 2026-06-09

### Docs
- Update CHANGELOG.md
- Update README.md
- Update TODO.md
- Update docs/README.md
- Update docs/architecture.md
- Update docs/desktop-capture.md
- Update docs/getting-started.md
- Update docs/img2svg-uri.md
- Update docs/packages.md
- Update docs/rest-window-api.md
- ... and 10 more files

### Test
- Update tests/test_adopt_window_capture.py
- Update tests/test_screenshot_merge.py

### Other
- Update Makefile
- Update app.vql.events.pb
- Update app.vql.json
- Update examples/full-pipeline.sh
- Update examples/generate-demo-screen.py
- Update examples/img2nl-vql-flow.sh
- Update examples/live-capture-test.sh
- Update examples/scope-window.py
- Update install-dev.sh
- Update layout.vql.imgl.json
- ... and 74 more files

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
