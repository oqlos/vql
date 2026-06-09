# Desktop capture (GNOME / Wayland)

## Problem: czarny PNG

Na **GNOME + Wayland** bez uprawnienia *Nagrywanie ekranu* wiele backendów zapisuje **czarny obraz** o dużym rozmiarze wirtualnego pulpitu (np. 8416×4800, `#000000`):

| Backend | Typowy wynik bez uprawnień |
|---------|---------------------------|
| `gnome-screenshot -f` | czarny PNG, pełny virtual desktop |
| `mss`, `grim`, `gnome-shell` | to samo |
| `capture-screen` (bez `--interactive`) | odrzucony jako blank |

## Rozwiązanie

### 1. Interaktywny portal (najpewniejsze)

```bash
uri2vql capture-screen --interactive --out /tmp/screen.png
```

Pokazuje dialog xdg-desktop-portal — po zgodzie dostajesz prawdziwy zrzut (np. 2700×4800, ~300+ kolorów).

### 2. Uprawnienia systemowe

**Ustawienia → Prywatność → Nagrywanie ekranu** → włącz dla Terminala / Cursor.

Wtedy `gnome-screenshot -f` i `capture-screen` bez `--interactive` mogą działać.

### 3. Ręczny zrzut

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
