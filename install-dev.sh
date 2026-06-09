#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

pip install -e ".[desktop,png]"
pip install -e packages/uri2vql
pip install -e packages/nlp2vql
IMG2NL_ROOT="${IMG2NL_ROOT:-$ROOT/../../wronai/img2nl}"
IMGL_ROOT="${IMGL_ROOT:-$ROOT/../../semcod/imgl}"
if [ -f "$IMG2NL_ROOT/pyproject.toml" ]; then
  pip install -e "$IMG2NL_ROOT[analyze,similarity]"
  pip install -e packages/img2vql
  pip install -e packages/uri2vql
  pip install -e "packages/img2svg[vectorize]"
  pip install -e packages/uri2img2svg
  pip install -e packages/dsl2img2svg
else
  pip install -e "packages/img2svg[vectorize]"
  pip install -e packages/uri2img2svg
  pip install -e packages/dsl2img2svg
  echo "skip img2nl/img2vql (set IMG2NL_ROOT or clone wronai/img2nl)"
fi
if [ -f "$IMGL_ROOT/pyproject.toml" ]; then
  pip install -e "$IMGL_ROOT[vdisplay]"
  pip install pytesseract
  pip install -e "packages/uri2vql[imgl]"
else
  echo "skip imgl (set IMGL_ROOT or clone semcod/imgl for adopt-imgl demo)"
fi
pip install -e packages/dsl2vql  # after uri2vql + nlp2vql (lazy imports)
pip install -e packages/cli2vql
pip install -e packages/rest2vql
pip install -e "packages/mcp2vql" 2>/dev/null || echo "skip mcp2vql (mcp optional)"
pip install -e ".[dev,png]" jsonschema protobuf fastapi uvicorn httpx

echo "vql dev stack installed"
