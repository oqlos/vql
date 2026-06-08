#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

pip install -e .
pip install -e packages/uri2vql
pip install -e packages/nlp2vql
pip install -e packages/dsl2vql  # after uri2vql + nlp2vql (lazy imports)
pip install -e packages/cli2vql
pip install -e packages/rest2vql
pip install -e "packages/mcp2vql" 2>/dev/null || echo "skip mcp2vql (mcp optional)"
pip install -e ".[dev,png]" jsonschema protobuf fastapi uvicorn httpx

echo "vql dev stack installed"
