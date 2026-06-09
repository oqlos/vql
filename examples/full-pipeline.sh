#!/usr/bin/env bash
# Full screenshot pipeline: capture → analyze → detect → svg → diagnose.
# Docs: docs/window-pipeline.md, examples/README.md
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

URI2VQL="${URI2VQL:-${ROOT}/.venv/bin/uri2vql}"
IMG2SVG="${IMG2SVG:-${ROOT}/.venv/bin/img2svg}"
URI2IMG2SVG="${URI2IMG2SVG:-${ROOT}/.venv/bin/uri2img2svg}"

IMG="${VQL_TEST_IMAGE:-/tmp/vql-full-screen.png}"
PROG="${VQL_TEST_PROGRAM:-/tmp/vql-full.vql.json}"
UI_PROG="${VQL_TEST_UI_PROGRAM:-/tmp/vql-full-ui.vql.json}"
SVG_OUT="${VQL_TEST_SVG:-/tmp/vql-full-screen.svg}"
GRID="${VQL_TEST_GRID:-24}"
LOCALE="${VQL_TEST_LOCALE:-pl}"

echo "=== 1. capture (interactive portal) or use VQL_TEST_IMAGE ==="
if [[ -n "${VQL_TEST_IMAGE:-}" && -s "$VQL_TEST_IMAGE" ]]; then
  IMG="$VQL_TEST_IMAGE"
  echo "using: $IMG"
elif "$URI2VQL" capture-screen --interactive --out "$IMG"; then
  echo "captured: $IMG"
else
  echo "capture failed — use: VQL_TEST_IMAGE=/path/to/screen.png bash examples/full-pipeline.sh"
  exit 1
fi

echo ""
echo "=== 2. analyze-window (merged grid + fingerprint) ==="
"$URI2VQL" analyze-window --image "$IMG" --out "$PROG" --grid "$GRID" | jq '{
  ok, object_count: .data.object_count, scene_class: .data.scene_class,
  fingerprint: .data.fingerprint.phash, region_count: .data.image_stats
}'

echo ""
echo "=== 3. detect-window (UI bboxes) ==="
"$URI2VQL" detect-window --image "$IMG" --locale "$LOCALE" | jq '{
  ok, element_count, by_role, description: .description[:200]
}'

echo ""
echo "=== 4. adopt-ui → ui.vql.json ==="
"$URI2VQL" adopt-ui --image "$IMG" --out "$UI_PROG" --locale "$LOCALE" | jq '{
  ok, element_count, object_count, description: .description[:200]
}'

echo ""
echo "=== 5. img2svg + uri2img2svg ==="
if command -v "$IMG2SVG" >/dev/null 2>&1; then
  "$IMG2SVG" svg "$IMG" --out "$SVG_OUT" --grid "$GRID" | jq '{ok, output, region_count, svg_bytes}'
else
  echo "skip img2svg (not installed)"
fi
if command -v "$URI2IMG2SVG" >/dev/null 2>&1; then
  "$URI2IMG2SVG" query "img2svg://vectorize?path=$IMG&grid=$GRID" | jq '{ok, region_count: .data.region_count}'
fi

echo ""
echo "=== 6. diagnose + save ==="
"$URI2VQL" diagnose-window --image "$IMG" --vql-program "$PROG" --locale "$LOCALE" --save | jq '{
  ok, recommendation, special_hits: .special_hits, saved_to_program
}'

echo ""
echo "=== 7. summary (live refresh) ==="
"$URI2VQL" query "vql://window/summary?file=$PROG&live=1&image=$IMG" | jq '{
  object_count, scene_class, diagnose_recommendation, special_hits
}'

echo ""
echo "Artifacts:"
echo "  PNG:       $IMG"
echo "  VQL grid:  $PROG"
echo "  VQL UI:    $UI_PROG"
echo "  SVG:       $SVG_OUT"
echo ""
echo "full-pipeline: OK"
