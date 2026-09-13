#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PYTHON_BIN="${PYTHON_BIN:-}"
if [[ -z "$PYTHON_BIN" ]]; then
  if command -v python3.11 >/dev/null 2>&1; then PYTHON_BIN="python3.11"; else PYTHON_BIN="python3"; fi
fi

"$PYTHON_BIN" "$ROOT/scripts/preflight.py" --strict
"$PYTHON_BIN" "$ROOT/scripts/bootstrap.py"
"$ROOT/backend/.venv/bin/python" "$ROOT/scripts/acceptance.py"
