#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$ROOT/.run"
mkdir -p "$RUN_DIR"

PYTHON_BIN="${PYTHON_BIN:-}"
if [[ -z "$PYTHON_BIN" ]]; then
  if command -v python3.11 >/dev/null 2>&1; then
    PYTHON_BIN="python3.11"
  elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  else
    echo "Python 3.11 is required."
    exit 1
  fi
fi

"$PYTHON_BIN" "$ROOT/scripts/preflight.py" --strict
"$PYTHON_BIN" "$ROOT/scripts/bootstrap.py"

VENV_PY="$ROOT/backend/.venv/bin/python"

if ! curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then
  (
    cd "$ROOT/backend"
    nohup "$VENV_PY" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --env-file "$ROOT/.env" > "$RUN_DIR/backend.log" 2>&1 &
    echo $! > "$RUN_DIR/backend.pid"
  )
fi

for _ in $(seq 1 60); do
  if curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then break; fi
  sleep 1
done
curl -fsS http://127.0.0.1:8000/health >/dev/null

if ! (echo > /dev/tcp/127.0.0.1/5173) >/dev/null 2>&1; then
  (
    cd "$ROOT/frontend"
    nohup npm run dev -- --host 127.0.0.1 > "$RUN_DIR/frontend.log" 2>&1 &
    echo $! > "$RUN_DIR/frontend.pid"
  )
fi

for _ in $(seq 1 60); do
  if (echo > /dev/tcp/127.0.0.1/5173) >/dev/null 2>&1; then break; fi
  sleep 1
done

cat <<'EOF'

READY
Dashboard:       http://127.0.0.1:5173
API health:      http://127.0.0.1:8000/health
API docs:        http://127.0.0.1:8000/docs
Evidence Lab:    http://127.0.0.1:5173/evidence
Remediation:     http://127.0.0.1:5173/remediate
Evaluation Lab:  http://127.0.0.1:5173/evaluation
Stop services:   ./scripts/stop.sh
EOF
