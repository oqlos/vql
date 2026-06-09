#!/usr/bin/env bash
# Interactive live-capture test for GNOME/Wayland.
# Docs: docs/desktop-capture.md, docs/window-pipeline.md
# Run from vql repo root:
#   cd ~/github/oqlos/vql
#   bash install-dev.sh
#   bash examples/live-capture-test.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-${ROOT}/.venv/bin/python}"
URI2VQL="${URI2VQL:-${ROOT}/.venv/bin/uri2vql}"
NLP2URI="${NLP2URI:-${ROOT}/.venv/bin/nlp2uri}"

if ! "$PYTHON" -c "from PIL import Image" 2>/dev/null; then
  echo "Brak Pillow. Zainstaluj: pip install 'vql[desktop]' pillow mss"
  echo "  lub: bash install-dev.sh"
  exit 1
fi

IMG="${VQL_TEST_IMAGE:-/tmp/vql-live-screen.png}"
PROG="${VQL_TEST_PROGRAM:-/tmp/vql-live.vql.json}"
GRID="${VQL_TEST_GRID:-12}"

echo "=== 1. capture-screen (portal --interactive on Wayland) ==="
if [[ -n "${VQL_TEST_IMAGE:-}" && -s "$VQL_TEST_IMAGE" ]]; then
  IMG="$VQL_TEST_IMAGE"
  echo "using provided image: $IMG"
elif "$URI2VQL" capture-screen --out "$IMG" --interactive; then
  echo "capture-screen OK: $IMG"
else
  echo "capture-screen failed — diagnose:"
  "$URI2VQL" capture-screen --diagnose --interactive --out "$IMG" || true
  echo ""
  echo "GNOME/Wayland bez uprawnień daje czarny PNG (często 8416×7680, #000000)."
  echo "  uri2vql capture-screen --interactive --out $IMG"
  echo "  gnome-screenshot (bez -f — interaktywny) lub PrtScn → ~/Pictures/Screenshots/"
  echo "  VQL_TEST_IMAGE=/ścieżka/do/ok.png bash examples/live-capture-test.sh"
  exit 1
fi

echo ""
echo "=== 2. verify image not blank ==="
"$PYTHON" - <<PY
from pathlib import Path
from vql.adopt.window import image_stats
p = Path("$IMG")
stats = image_stats(p)
print("file:", p, "bytes:", stats.get("bytes"), "size:", stats.get("width"), "x", stats.get("height"))
print("brightness:", stats.get("brightness_min"), "-", stats.get("brightness_max"), "avg", stats.get("brightness_avg"))
print("top_colors:", stats.get("top_colors"))
assert stats.get("ok") and not stats.get("is_blank"), "image is blank — GNOME blocked capture (Screen Recording permission?)"
print("image OK (not blank)")
PY

echo ""
echo "=== 3. uri2vql analyze-window ==="
"$URI2VQL" analyze-window --image "$IMG" --out "$PROG" --grid "$GRID"

echo ""
echo "=== 4. summary ==="
"$PYTHON" - <<PY
from uri2vql import query_uri
r = query_uri("vql://window/summary?file=$PROG")
d = r.data or {}
print("object_count:", d.get("object_count"))
print("dominant_colors:", d.get("dominant_colors"))
scene = d.get("scene", {})
print("scene:", scene.get("width"), "x", scene.get("height"))
assert r.ok, r.error
PY

echo ""
echo "=== 5. detect-window (optional img2vql) ==="
if "$URI2VQL" detect-window --image "$IMG" --locale pl 2>/dev/null | jq '{element_count, by_role}' 2>/dev/null; then
  :
else
  echo "skip detect-window (img2vql not installed)"
fi

echo ""
echo "=== 6. nlp2uri execute (optional) ==="
if command -v "$NLP2URI" >/dev/null 2>&1; then
  "$NLP2URI" execute "opisz ekran vql" 2>&1 | tail -5
else
  echo "skip nlp2uri"
fi

echo ""
echo "Next: bash examples/full-pipeline.sh"
echo "Docs: docs/window-pipeline.md, examples/README.md"
echo "live-capture-test: OK"
