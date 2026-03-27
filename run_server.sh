#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

export PYTHONPATH="$ROOT_DIR/server:$ROOT_DIR/shared${PYTHONPATH:+:$PYTHONPATH}"

SKETCHY_SERVER_HOST="${SKETCHY_SERVER_HOST:-0.0.0.0}"
SKETCHY_SERVER_PORT="${SKETCHY_SERVER_PORT:-8000}"

if command -v python3 >/dev/null 2>&1; then
  python3 -m uvicorn sketchy_server.app.main:app --host "$SKETCHY_SERVER_HOST" --port "$SKETCHY_SERVER_PORT"
else
  python -m uvicorn sketchy_server.app.main:app --host "$SKETCHY_SERVER_HOST" --port "$SKETCHY_SERVER_PORT"
fi
