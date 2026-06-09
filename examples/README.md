# Przykłady VQL

Skrypty demonstracyjne w katalogu `examples/`. Uruchamiaj z katalogu głównego repo:

```bash
cd ~/github/oqlos/vql
bash install-dev.sh
```

## Skrypty bash

| Skrypt | Wymaga | Opis |
|--------|--------|------|
| [live-capture-test.sh](live-capture-test.sh) | Pillow, uri2vql | Capture Wayland (`--interactive`) → analyze → summary |
| [img2nl-vql-flow.sh](img2nl-vql-flow.sh) | img2nl, img2vql | Fingerprint, refresh, compare, diagnose --save; opcjonalnie imgl |
| [full-pipeline.sh](full-pipeline.sh) | pełny stack | Capture → analyze → detect → svg → diagnose (jeden przebieg) |

### Zmienne środowiskowe

| Zmienna | Domyślnie | Znaczenie |
|---------|-----------|-----------|
| `VQL_TEST_IMAGE` | — | Gotowy PNG zamiast live capture |
| `VQL_TEST_PROGRAM` | `/tmp/vql-live.vql.json` | Ścieżka programu VQL |
| `VQL_TEST_GRID` | `24` | Rozmiar siatki (analyze + svg w `full-pipeline.sh`) |
| `IMG2NL_ROOT` | `../../wronai/img2nl` | Ścieżka do img2nl (install-dev.sh) |
| `IMGL_ROOT` | `~/github/semcod/imgl` | Ścieżka do imgl (opcjonalnie) |
| `IMGL_AUTO_CAPTURE` | `1` | imgl capture zamiast synthetic PNG |
| `IMGL_WINDOW_SCOPE` | `auto` | Przycięcie do okna fokusu (`scope-window.py`) |

### Szybkie uruchomienie

```bash
# Wayland — wymaga --interactive lub uprawnień Screen Recording
bash examples/live-capture-test.sh

# Z gotowym PNG (po capture-screen --interactive)
VQL_TEST_IMAGE=/tmp/screen.png bash examples/live-capture-test.sh

# Pełny pipeline (capture + UI detect + SVG + diagnose)
bash examples/full-pipeline.sh

# img2nl metadata flow (synthetic PNG gdy brak obrazu)
bash examples/img2nl-vql-flow.sh

# Z własnym zrzutem
bash examples/img2nl-vql-flow.sh /tmp/screen.png /tmp/moj-ekran.vql.json
```

## Skrypty Python

| Skrypt | Opis |
|--------|------|
| [generate-demo-screen.py](generate-demo-screen.py) | Syntetyczny UI PNG (headless, bez capture) |
| [scope-window.py](scope-window.py) | Przycięcie screenshotu do okna z największą liczbą elementów UI (imgl) |

```bash
python examples/generate-demo-screen.py -o /tmp/demo-ui.png
python examples/scope-window.py /tmp/screen.png -o /tmp/screen.scoped.png --json
```

## Powiązana dokumentacja

- [docs/desktop-capture.md](../docs/desktop-capture.md) — czarny PNG na Wayland
- [docs/window-pipeline.md](../docs/window-pipeline.md) — pełny przepływ
- [docs/window-uri.md](../docs/window-uri.md) — URI i CLI
- [docs/img2svg-uri.md](../docs/img2svg-uri.md) — wektoryzacja
- [docs/rest-window-api.md](../docs/rest-window-api.md) — REST dla agentów
