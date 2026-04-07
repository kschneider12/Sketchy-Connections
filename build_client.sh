#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

ICON_ARGS=()
if [[ $# -ge 1 && -n "${1:-}" ]]; then
  ICON_ARGS=(--icon "$1")
fi

PY_CMD=""
if command -v python3 >/dev/null 2>&1; then
  PY_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PY_CMD="python"
fi

if command -v pyinstaller >/dev/null 2>&1; then
  PYI_CMD=(pyinstaller)
elif [[ -n "$PY_CMD" ]] && "$PY_CMD" -c "import PyInstaller" >/dev/null 2>&1; then
  PYI_CMD=("$PY_CMD" -m PyInstaller)
else
  echo "PyInstaller is required." >&2
  echo "Install with: python -m pip install pyinstaller" >&2
  exit 1
fi

"${PYI_CMD[@]}" \
  --noconfirm \
  --clean \
  --windowed \
  --name SketchyConnections \
  --paths client \
  --paths shared \
  --add-data "client/assets:assets" \
  "${ICON_ARGS[@]}" \
  client/sketchy_client/main.py

echo "Build complete: dist/SketchyConnections"
