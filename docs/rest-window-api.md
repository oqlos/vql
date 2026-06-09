# REST window API (rest2vql)

HTTP endpoints dla agentów i automatyzacji — mirror CLI `uri2vql window/*`.

**Port domyślny:** 8216 (`rest2vql serve`)

## Instalacja

```bash
pip install -e packages/rest2vql
pip install -e "packages/rest2vql[window]"   # uri2vql + img2vql
```

## Uruchomienie

```bash
rest2vql serve --port 8216
```

## Endpoints

Wszystkie `POST /v1/window/*` przyjmują JSON:

```json
{
  "image": "/tmp/screen.png",
  "file": "app.vql.json",
  "locale": "pl",
  "grid": 12,
  "translate_mode": "auto",
  "save": false,
  "with_grid": false,
  "live": false,
  "interactive": null
}
```

Pola opcjonalne — wymagane zależą od endpointu.

| Endpoint | Wymagane | Opis |
|----------|----------|------|
| `POST /v1/window/detect` | `image` | Detekcja UI (img2vql) |
| `POST /v1/window/compare` | `image`, `file` | Fingerprint vs program |
| `POST /v1/window/refresh` | `image`, `file` | Odśwież metadata img2nl |
| `POST /v1/window/diagnose` | `image` | Diagnose LLM routing (`save`, `translate_mode`) |
| `POST /v1/window/analyze` | `image` | Grid adopt → VQL JSON |
| `POST /v1/window/adopt` | `image` | UI elements → VQL JSON |
| `POST /v1/window/summary` | `file` | Podsumowanie programu (`live=1` odświeża metadata) |

## Przykłady

```bash
# detect
curl -s -X POST http://localhost:8216/v1/window/detect \
  -H 'Content-Type: application/json' \
  -d '{"image":"/tmp/screen.png","locale":"pl"}' | jq .

# compare fingerprint
curl -s -X POST http://localhost:8216/v1/window/compare \
  -H 'Content-Type: application/json' \
  -d '{"image":"/tmp/screen.png","file":"/tmp/app.vql.json"}' | jq .

# diagnose + save to program
curl -s -X POST http://localhost:8216/v1/window/diagnose \
  -H 'Content-Type: application/json' \
  -d '{"image":"/tmp/screen.png","file":"/tmp/app.vql.json","save":true,"locale":"pl"}' | jq .

# summary with live refresh
curl -s -X POST http://localhost:8216/v1/window/summary \
  -H 'Content-Type: application/json' \
  -d '{"file":"/tmp/app.vql.json","image":"/tmp/screen.png","live":true}' | jq .
```

## Kody odpowiedzi

| Kod | Znaczenie |
|-----|-----------|
| 200 | `ok: true` lub wynik biznesowy |
| 400 | `ok: false` (np. blank PNG, brak pliku) |
| 501 | brak zależności (`img2vql` nie zainstalowany) |

## Przykłady

REST odpowiada tym samym operacjom co CLI `uri2vql` — porównaj z:

```bash
bash examples/full-pipeline.sh
uri2vql detect-window --image /tmp/screen.png
```

→ [examples/README.md](../examples/README.md) · [window-uri.md](window-uri.md) · [window-pipeline.md](window-pipeline.md)
