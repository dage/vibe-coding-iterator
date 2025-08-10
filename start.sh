#!/bin/bash
# start.sh

set -euo pipefail

# Resolve project root (directory of this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ensure storage exists for static serving
mkdir -p "$SCRIPT_DIR/storage"

# Free port 8000 if a previous dev server from this project is running
PIDS=$(lsof -nP -iTCP:8000 -sTCP:LISTEN -t 2>/dev/null || true)
if [ -n "$PIDS" ]; then
  for pid in $PIDS; do
    cmd=$(ps -o command= -p "$pid" 2>/dev/null || true)
    if echo "$cmd" | grep -E -q '(src\.tools\.dev_server|uvicorn)'; then
      echo "Killing previous dev server on :8000 (pid $pid)"
      kill -9 "$pid" 2>/dev/null || true
    else
      echo "Port 8000 is in use by another process: $cmd" >&2
      echo "Please stop it and re-run ./start.sh" >&2
      exit 1
    fi
  done
fi

# Load .env to get VIBES_APP_NAME (used as the conda env name)
if [ -f "$SCRIPT_DIR/.env" ]; then
  set -a
  . "$SCRIPT_DIR/.env"
  set +a
fi

if [ -z "${VIBES_APP_NAME:-}" ]; then
  echo "VIBES_APP_NAME not set. Run ./setup.sh first to generate .env." >&2
  exit 1
fi

ENV_NAME="$VIBES_APP_NAME"

# Activate conda env and run the dev server
if command -v conda >/dev/null 2>&1; then
  eval "$(conda shell.bash hook)"
  conda activate "$ENV_NAME" 2>/dev/null || {
    echo "Conda env '$ENV_NAME' not found. Run ./setup.sh first." >&2
    exit 1
  }
  python -m src.tools.dev_server
else
  echo "conda is not installed or not in PATH. Please install Miniconda/Anaconda and run ./setup.sh" >&2
  exit 1
fi


