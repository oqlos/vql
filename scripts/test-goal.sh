#!/usr/bin/env bash
# Test entrypoint for goal -a — installs *2vql stack then runs pytest.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
make test
