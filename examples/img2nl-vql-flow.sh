#!/usr/bin/env bash
# End-to-end img2nl → VQL window pipeline demo.
# Auto-generates a synthetic UI PNG when the image path is missing (headless-friendly).
# Optional imgl step: OCR layout + annotated preview PNG.
# Docs: examples/README.md, docs/window-pipeline.md, docs/window-uri.md
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMG="${1:-/tmp/vql-img2nl-demo.png}"
PROG="${2:-/tmp/vql-img2nl-demo.vql.json}"
IMGL_ROOT="${IMGL_ROOT:-$HOME/github/semcod/imgl}"
ANNOTATED="${IMG%.png}.numbered.png"
IMGL_LAYOUT="${PROG%.vql.json}.imgl.vql.json"
IMGL_RAN=0
SOURCE_IMG=""

cd "$ROOT"

# Prefer active venv (e.g. koru/.venv) over repo-local vql/.venv
resolve_venv_bin() {
  local name="$1"
  local candidate
  if [[ -n "${VIRTUAL_ENV:-}" ]]; then
    for candidate in "${VIRTUAL_ENV}/bin/${name}" "${VIRTUAL_ENV}/bin/${name}3"; do
      if [[ -x "$candidate" ]]; then
        echo "$candidate"
        return 0
      fi
    done
  fi
  if [[ -x "${ROOT}/.venv/bin/${name}" ]]; then
    echo "${ROOT}/.venv/bin/${name}"
    return 0
  fi
  if command -v "$name" >/dev/null 2>&1; then
    command -v "$name"
    return 0
  fi
  return 1
}

if [[ -z "${PYTHON:-}" ]]; then
  if resolved="$(resolve_venv_bin python)"; then
    PYTHON="$resolved"
  else
    PYTHON="$(command -v python3)"
  fi
fi

URI2VQL_BIN="${URI2VQL:-}"
if [[ -z "$URI2VQL_BIN" ]]; then
  URI2VQL_BIN="$(resolve_venv_bin uri2vql || true)"
fi

IMGL_BIN="${IMGL:-}"
if [[ -z "$IMGL_BIN" ]]; then
  IMGL_BIN="$(resolve_venv_bin imgl || true)"
fi

export PYTHONPATH="src:packages/uri2vql/src:packages/img2vql/src${PYTHONPATH:+:$PYTHONPATH}"

run_uri2vql() {
  if [[ -n "$URI2VQL_BIN" ]]; then
    "$URI2VQL_BIN" "$@"
  elif "$PYTHON" -c "import uri2vql.cli" 2>/dev/null; then
    "$PYTHON" -m uri2vql.cli "$@"
  else
    echo "uri2vql not found. Install the dev stack first:"
    echo "  cd $ROOT && bash install-dev.sh"
    exit 1
  fi
}

run_imgl() {
  if [[ -n "$IMGL_BIN" ]]; then
    "$IMGL_BIN" "$@"
  else
    "$PYTHON" -m imgl.cli "$@"
  fi
}

ensure_demo_image() {
  if [[ -f "$IMG" ]]; then
    echo "Using existing image: $IMG"
    return 0
  fi

  if [[ "${IMGL_AUTO_CAPTURE:-1}" != "0" ]] && "$PYTHON" -c "import imgl" 2>/dev/null; then
    echo "== 0. capture screen (imgl → vdisplay mirror, no portal)"
    if run_imgl capture -o "$IMG" 2>/dev/null && [[ -f "$IMG" ]]; then
      echo "Wrote $IMG"
      return 0
    fi
    echo "    capture failed — falling back to synthetic demo" >&2
  fi

  echo "== 0. generate demo screen (synthetic UI, no screenshot needed)"
  "$PYTHON" "$ROOT/examples/generate-demo-screen.py" -o "$IMG"
  echo "Wrote $IMG"
}

maybe_scope_window() {
  if [[ "${IMGL_WINDOW_SCOPE:-auto}" == "0" ]]; then
    return 0
  fi
  if ! "$PYTHON" -c "import imgl" 2>/dev/null; then
    return 0
  fi

  local scope_args=()
  if [[ "${IMGL_WINDOW_SCOPE:-auto}" =~ ^[0-9]+$ ]]; then
    scope_args+=(--window "${IMGL_WINDOW_SCOPE}")
  fi
  if [[ -n "${IMGL_WINDOW_ID:-}" ]]; then
    scope_args+=(--window-id "$IMGL_WINDOW_ID")
  fi

  local scoped="${IMG%.png}.scoped.png"
  echo "== 0a. window scope (focus region with most UI elements)"
  SOURCE_IMG="$IMG"
  local scope_out
  if scope_out="$("$PYTHON" "$ROOT/examples/scope-window.py" "$IMG" -o "$scoped" "${scope_args[@]}" 2>/dev/null)"; then
    if [[ -f "$scope_out" && "$scope_out" != "$IMG" ]]; then
      IMG="$scope_out"
      echo "Scoped image: $IMG"
    else
      echo "Using full screenshot (scope skipped)"
    fi
  else
    echo "Window scope skipped"
  fi
}

run_imgl_enrichment() {
  if [[ -d "$IMGL_ROOT" ]]; then
    export PYTHONPATH="$IMGL_ROOT${PYTHONPATH:+:$PYTHONPATH}"
  fi
  if ! "$PYTHON" -c "import imgl" 2>/dev/null; then
    echo "== 0b. skip imgl (not in active Python: $PYTHON)"
    echo "    install: pip install -e $IMGL_ROOT"
    return 0
  fi
  if ! "$PYTHON" -c "import pytesseract" 2>/dev/null; then
    echo "== 0b. imgl OCR requires pytesseract (missing in: $PYTHON)" >&2
    echo "    pip install pytesseract" >&2
    echo "    # or: cd $ROOT && bash install-dev.sh" >&2
    exit 1
  fi

  IMGL_RAN=1
  echo "== 0b. imgl — OCR layout + annotated preview"
  run_uri2vql adopt-imgl --image "$IMG" --out "$IMGL_LAYOUT" --lang eng+pol | jq '{ok, element_count, roles, detect_source}'

  run_imgl annotate "$IMG" --output "$ANNOTATED" --lang eng+pol >/dev/null
  echo "Annotated preview: $ANNOTATED"
  echo "imgl layout program: $IMGL_LAYOUT"

  run_imgl analyze "$IMG" --lang eng+pol 2>/dev/null | jq '{
    window_count: (.windows | length),
    windows: [.windows[]? | {title, elements: [.elements[]? | {type, text}]}]
  }' || true
}

ensure_demo_image
maybe_scope_window
run_imgl_enrichment

echo "Environment: python=$PYTHON${VIRTUAL_ENV:+ venv=$VIRTUAL_ENV}"
echo

echo "== 1. analyze-window (full adopt)"
run_uri2vql analyze-window --image "$IMG" --out "$PROG" --grid 12 | jq '{
  ok,
  object_count: .data.object_count,
  fingerprint: .data.fingerprint.phash,
  scene_class: .data.scene_class
}'

if ! "$PYTHON" -c "import imagehash" 2>/dev/null; then
  echo "hint: fingerprint/compare need imagehash — rerun: bash install-dev.sh" >&2
fi

echo "== 2. analyze-window again (should skip grid if unchanged)"
run_uri2vql analyze-window --image "$IMG" --out "$PROG" --grid 12 | jq '{
  ok,
  skipped_adopt: .data.skipped_adopt,
  recommendation: .data.recommendation
}'

echo "== 3. refresh metadata"
run_uri2vql refresh-window --vql-program "$PROG" --image "$IMG" | jq '{ok, scene_class, special_hits}'

echo "== 4. compare fingerprint"
run_uri2vql compare-window --vql-program "$PROG" --image "$IMG" | jq '{ok, match, phash_distance, error}' || true

echo "== 5. diagnose + save"
run_uri2vql diagnose-window --image "$IMG" --vql-program "$PROG" --save | jq '{ok, recommendation, saved_to_program}'

echo "== 6. summary"
run_uri2vql query "vql://window/summary?file=$PROG" | jq '{object_count, scene_class, diagnose_recommendation, special_hits}'

echo
echo "Demo artifacts:"
echo "  source PNG:     ${SOURCE_IMG:-$IMG}"
if [[ -n "${SOURCE_IMG:-}" && "$SOURCE_IMG" != "$IMG" ]]; then
  echo "  scoped PNG:     $IMG"
fi
echo "  VQL program:    $PROG"
if [[ "${IMGL_RAN:-0}" == 1 && -f "$ANNOTATED" ]]; then
  echo "  imgl annotated: $ANNOTATED"
fi
if [[ "${IMGL_RAN:-0}" == 1 && -f "$IMGL_LAYOUT" ]]; then
  echo "  imgl layout:    $IMGL_LAYOUT"
fi
