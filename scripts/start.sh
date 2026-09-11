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

port_open() {
  (echo > "/dev/tcp/127.0.0.1/$1") >/dev/null 2>&1
}

find_free_backend_port() {
  local port
  for port in $(seq 8000 8099); do
    if ! port_open "$port"; then
      echo "$port"
      return 0
    fi
  done
  return 1
}

"$PYTHON_BIN" "$ROOT/scripts/preflight.py" --strict
"$PYTHON_BIN" "$ROOT/scripts/bootstrap.py"

VENV_PY="$ROOT/backend/.venv/bin/python"

if port_open 5173; then
  echo "Frontend port 5173 is already occupied. Stop that process before launching this build."
  exit 1
fi

BACKEND_PORT="$(find_free_backend_port)" || {
  echo "No free backend port found in range 8000-8099."
  exit 1
}

if [[ "$BACKEND_PORT" != "8000" ]]; then
  echo "Port 8000 is occupied; using backend port $BACKEND_PORT instead."
fi

(
  cd "$ROOT/backend"
  nohup "$VENV_PY" -m uvicorn app.main:app --host 127.0.0.1 --port "$BACKEND_PORT" --env-file "$ROOT/.env" > "$RUN_DIR/backend.log" 2>&1 &
  echo $! > "$RUN_DIR/backend.pid"
  echo "$BACKEND_PORT" > "$RUN_DIR/backend.port"
)

for _ in $(seq 1 60); do
  if curl -fsS "http://127.0.0.1:$BACKEND_PORT/health" >/dev/null 2>&1; then break; fi
  sleep 1
done
curl -fsS "http://127.0.0.1:$BACKEND_PORT/health" >/dev/null

API_BASE="http://127.0.0.1:$BACKEND_PORT"
MODEL_RUNTIME="$(curl -fsS "$API_BASE/api/v1/autofix/model-runtime" 2>/dev/null || true)"
if [[ "$MODEL_RUNTIME" == *'"mode":"LOCAL_OLLAMA"'* && "$MODEL_RUNTIME" == *'"ready":true'* ]]; then
  echo "AI runtime: LIVE LOCAL OLLAMA/QWEN"
elif [[ "$MODEL_RUNTIME" == *'"mode":"GEMINI_FREE"'* && "$MODEL_RUNTIME" == *'"ready":true'* ]]; then
  echo "AI runtime: LIVE GEMINI FREE-TIER"
else
  echo "AI runtime: DETERMINISTIC FALLBACK (run setup-local-ai.bat on Windows or start Ollama + pull qwen3:4b)"
fi

(
  cd "$ROOT/frontend"
  VITE_API_BASE_URL="$API_BASE" nohup npm run dev -- --host localhost --port 5173 --strictPort > "$RUN_DIR/frontend.log" 2>&1 &
  echo $! > "$RUN_DIR/frontend.pid"
  echo 5173 > "$RUN_DIR/frontend.port"
)

for _ in $(seq 1 60); do
  if port_open 5173; then break; fi
  sleep 1
done

if ! port_open 5173; then
  echo "Frontend did not become available. Check $RUN_DIR/frontend.log."
  exit 1
fi

cat <<EOF

READY
Dashboard:       http://localhost:5173
Real AutoFix:    http://localhost:5173/prototype
Judge Intake:    http://localhost:5173/intake
AI Reasoning:    http://localhost:5173/ai
Judge Mode:      http://localhost:5173/demo
API health:      $API_BASE/health
API docs:        $API_BASE/docs
Evidence Lab:    http://localhost:5173/evidence
Remediation:     http://localhost:5173/remediate
Evaluation Lab:  http://localhost:5173/evaluation
Readiness:       http://localhost:5173/readiness
Stop services:   ./scripts/stop.sh
EOF
