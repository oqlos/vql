# Architektura

## Warstwy

```
┌──────────────────────────────────────────────────────────────┐
│  Adaptery wejścia                                            │
│  uri2vql  nlp2vql  cli2vql  mcp2vql  rest2vql               │
│  uri2img2svg  dsl2img2svg                                    │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│  dsl2vql — bus CQRS/ES, JSON Schema, protobuf                │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│  vql/ (core)                                                 │
│  schema · compiler · validation · renderers · adopt/window   │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│  Rozszerzenia obrazu                                         │
│  img2vql · img2svg · img2nl (zewn.) · imgl (zewn.)           │
└──────────────────────────────────────────────────────────────┘
```

## VQLProgram (IR)

Źródło prawdy: `src/vql/schema/program.py`

```
VQLProgram
├── scene
│   ├── width, height, layers[], relations[]
│   └── Layer → Object → Primitive (rectangle, path, …)
│       └── metadata: role, bbox, confidence, color, …
└── metadata
    ├── fingerprint, scene_class, special_hits
    ├── llm_hint, diagnose_recommendation
    └── image, analyzed_at, capture
```

## Warstwy screenshot (layers)

| Layer ID | Źródło |
|----------|--------|
| `screen_regions` | `vql.adopt.window` (merge_regions) |
| `ui_elements` | `img2vql adopt` |
| `traced_regions` | `img2svg to_vql` |
| imgl layers | `adopt-imgl` |

## Interfejsy

| Warstwa | Window | SVG |
|---------|--------|-----|
| CLI | uri2vql, img2vql | img2svg, uri2img2svg, dsl2img2svg |
| URI | `vql://window/*` | `img2svg://*` |
| REST | `/v1/window/*` | planowane `/v1/img2svg/*` |
| MCP | detect, compare, refresh, diagnose | — |

## Pakiety obrazu

| Pakiet | Kierunek | Output |
|--------|----------|--------|
| `vql.adopt.window` | PNG → merged grid | `screen_regions` |
| `img2vql` | PNG → UI + diagnose | `ui_elements`, metadata, relations |
| `img2svg` | PNG → vectors | `.svg`, `traced_regions` |
| `img2nl` | PNG → features | llm_hint, scene_class, OCR trigger |
| `imgl` | PNG → OCR UI | labeled elements, interact |

Szczegóły: [packages.md](packages.md) · Pipeline: [window-pipeline.md](window-pipeline.md)

## Event store

`dsl2vql` → `app.vql.events.pb` (GENERATE, PATCH, …). Fingerprint w EventStore — planowane.

## Diagram DSL (vql drawing)

[packages/README.md](../packages/README.md#przepływ)
