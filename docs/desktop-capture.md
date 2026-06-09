# Desktop capture (GNOME / Wayland)

VQL oferuje **dwie ścieżki** zrzutu ekranu:

| Ścieżka | Komenda | Kiedy użyć |
|---------|---------|------------|
| **vdisplay + imgl** (zalecane dla LLM) | `imgl capture -o screen.png` | Automatyzacja, headless, provenance DISPLAY |
| **uri2vql** (portal) | `uri2vql capture-screen --interactive` | Szybki test bez imgl, dialog GNOME OK |

Pełny przepływ vdisplay → imgl → VQL → LLM: [vdisplay-imgl-automation.md](vdisplay-imgl-automation.md).

## Problem: czarny PNG

Na **GNOME + Wayland** bez uprawnienia *Nagrywanie ekranu* wiele backendów zapisuje **czarny obraz** o dużym rozmiarze wirtualnego pulpitu (np. 8416×4800, `#000000`):

| Backend | Typowy wynik bez uprawnień |
|---------|---------------------------|
| `gnome-screenshot -f` | czarny PNG, pełny virtual desktop |
| `mss`, `grim`, `gnome-shell` | to samo |
| `capture-screen` (bez `--interactive`) | odrzucony jako blank |

## Rozwiązanie

### 1. imgl + vdisplay mirror (zalecane dla automatyzacji LLM)

```bash
imgl capture -o /tmp/screen.png --verify
imgl diagnose /tmp/screen.png   # worth_analyzing: true
```

vdisplay próbuje mirror bez dialogu GNOME. Na Wayland, gdy mirror zawiedzie, imgl automatycznie przechodzi na portal (region picker). Zapisuje `screen.capture.json` z `display` / `monitor` — potrzebne przy `imgl interact --execute`.

Wymaga: `pip install -e "$IMGL_ROOT[vdisplay]"` (patrz `install-dev.sh`).

### 2. Interaktywny portal uri2vql (bez imgl)

```bash
uri2vql capture-screen --interactive --out /tmp/screen.png
```

Pokazuje dialog xdg-desktop-portal — po zgodzie dostajesz prawdziwy zrzut (np. 2700×4800, ~300+ kolorów).

### 3. Uprawnienia systemowe

**Ustawienia → Prywatność → Nagrywanie ekranu** → włącz dla Terminala / Cursor.

Wtedy `gnome-screenshot -f` i `capture-screen` bez `--interactive` mogą działać.

### 4. Ręczny zrzut

PrtScn → `~/Pictures/Screenshots/*.png`, potem:

```bash
uri2vql analyze-window --image ~/Pictures/Screenshots/....png --out app.vql.json
```

## Diagnostyka

```bash
uri2vql capture-screen --diagnose --interactive
```

Zwraca `attempts[]` per backend: `ok`, `blank`, `stats` (brightness, top_colors).

## Detekcja blank w pipeline

`analyze_screenshot()` i `live-capture-test.sh` odrzucają czarne PNG:

```json
{
  "ok": false,
  "error": "screenshot is blank (all black) — GNOME blocked capture without permission",
  "recommendation": "skip_llm_blank_capture"
}
```

## analyze-window z live capture

```bash
uri2vql analyze-window --interactive --out app.vql.json --grid 12
```

Flaga `--interactive` przekazywana do `capture_screen()` gdy nie podano `--image`.

## Test end-to-end

```bash
bash examples/live-capture-test.sh
# lub z gotowym PNG:
VQL_TEST_IMAGE=/tmp/screen.png bash examples/live-capture-test.sh
```

## Przykłady

```bash
bash examples/live-capture-test.sh
VQL_TEST_IMAGE=/tmp/screen.png bash examples/full-pipeline.sh
uri2vql capture-and-analyze --out app.vql.json --diagnose
```

→ [examples/README.md](../examples/README.md) · [window-pipeline.md](window-pipeline.md)
