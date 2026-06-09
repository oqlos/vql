# vql://window/* — referencja URI

Wszystkie URI obsługiwane przez `uri2vql query` i `query_window()`.

## analyze — siatka kolorów + metadata

```
vql://window/analyze?file=app.vql.json&image=/tmp/screen.png&grid=12&monitor=1&interactive=1
```

CLI: `uri2vql analyze-window --image ... --out app.vql.json --grid 12 --interactive`

## detect — detekcja UI (img2vql)

```
vql://window/detect?image=/tmp/screen.png&locale=pl
```

Zwraca: `elements[]` (role, bbox, location, confidence), `description` (NL).

CLI: `uri2vql detect-window --image ... --locale pl`

## adopt — UI → VQL program

```
vql://window/adopt?image=/tmp/screen.png&file=ui.vql.json&locale=pl&with_grid=1&grid=12
```

CLI: `uri2vql adopt-ui --image ... --out ui.vql.json`

## diagnose — img2nl routing LLM

```
vql://window/diagnose?image=/tmp/screen.png&file=app.vql.json&locale=pl&translate_mode=auto&save=1
```

CLI: `uri2vql diagnose-window --image ... --vql-program app.vql.json --save`

## compare — fingerprint

```
vql://window/compare?image=/tmp/screen.png&file=app.vql.json
```

CLI: `uri2vql compare-window --image ... --vql-program app.vql.json`

## refresh — odśwież metadata bez rebuild grid

```
vql://window/refresh?file=app.vql.json&image=/tmp/screen.png&locale=pl
```

CLI: `uri2vql refresh-window --vql-program app.vql.json --image ...`

## summary — podsumowanie programu

```
vql://window/summary?file=app.vql.json
vql://window/summary?file=app.vql.json&live=1&image=/tmp/screen.png
```

Zwraca: `object_count`, `dominant_colors`, `scene_class`, `fingerprint`, `diagnose_recommendation`, `special_hits`.

`live=1` — odświeża metadata img2nl przed odczytem (bez rebuild grid).

## imgl — OCR + interakcja (opcjonalnie)

```
vql://window/imgl?action=analyze&image=/tmp/screen.png&file=layout.vql.json&lang=eng+pol
vql://window/imgl?action=list&image=...&file=...
vql://window/imgl?action=click&target=button_3&file=...
```

CLI: `uri2vql adopt-imgl --image ... --out layout.vql.json`

## capture

**Zalecane (vdisplay + imgl):**

```bash
imgl capture -o /tmp/screen.png --verify --analyze
```

**uri2vql (portal, bez vdisplay):**

```bash
uri2vql capture-screen --interactive --out /tmp/screen.png
uri2vql capture-screen --diagnose
uri2vql capture-and-analyze --out app.vql.json --diagnose
```

`capture-and-analyze` — portal capture (domyślnie interactive) + analyze + opcjonalnie diagnose --save.

→ [vdisplay-imgl-automation.md](vdisplay-imgl-automation.md)

## NLP → URI (nlp2uri)

```bash
nlp2uri execute "opisz ekran vql"
nlp2uri execute "porównaj fingerprint vql"
nlp2uri execute "odśwież metadata okna"
```

## Metadata w app.vql.json

Po `analyze` / `adopt` / `diagnose --save`:

| Klucz | Opis |
|-------|------|
| `fingerprint` | phash, dhash — porównanie zmian ekranu |
| `scene_class` | np. `ui_blocks`, `dense_ui_or_code`, `unchanged_screen` |
| `special_hits` | `has_text`, `has_qr`, OCR preview |
| `llm_hint` | `send_to_llm`, confidence, reasons |
| `diagnose_recommendation` | ostatnia rekomendacja diagnose |
| `img2nl_text` | opis NL (locale) |

## Przykłady

```bash
bash examples/live-capture-test.sh
bash examples/full-pipeline.sh
bash examples/img2nl-vql-flow.sh /tmp/screen.png
```

→ [examples/README.md](../examples/README.md) · [window-pipeline.md](window-pipeline.md) · [rest-window-api.md](rest-window-api.md)
