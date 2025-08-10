#!/bin/bash
# start.sh

set -euo pipefail

# Resolve project root (directory of this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ensure storage exists for static serving
mkdir -p "$SCRIPT_DIR/storage"

# Activate conda env and run the dev server
if command -v conda >/dev/null 2>&1; then
  eval "$(conda shell.bash hook)"
  conda activate ai-env 2>/dev/null || {
    echo "Conda env 'ai-env' not found. Run ./setup.sh first." >&2
    exit 1
  }
  python -m src.tools.dev_server
else
  echo "conda is not installed or not in PATH. Please install Miniconda/Anaconda and run ./setup.sh" >&2
  exit 1
fi


