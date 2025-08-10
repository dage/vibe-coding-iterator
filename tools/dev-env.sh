#!/usr/bin/env bash
# tools/dev-env.sh
# Usage: source tools/dev-env.sh

set -euo pipefail

# Resolve project root (tools/..) robustly for bash and zsh
if [[ -n "${BASH_SOURCE:-}" ]]; then
  _src_path="${BASH_SOURCE[0]}"
elif [[ -n "${ZSH_VERSION:-}" ]]; then
  # zsh: ${(%):-%N} expands to the current script path when sourced
  _src_path="${(%):-%N}"
else
  # Fallback (may be the shell name if sourced in some shells)
  _src_path="$0"
fi
SCRIPT_DIR="$(cd "$(dirname "$_src_path")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load .env so VIBES_* are available in the shell
if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1090
  . "$ROOT_DIR/.env"
  set +a
else
  echo "✗ .env not found at $ROOT_DIR/.env. Run ./setup.sh first." >&2
  { return 1; } 2>/dev/null || exit 1
fi

if [[ -z "${VIBES_APP_NAME:-}" ]]; then
  echo "✗ VIBES_APP_NAME is not set in .env" >&2
  { return 1; } 2>/dev/null || exit 1
fi

# Activate conda environment named by VIBES_APP_NAME
if ! command -v conda >/dev/null 2>&1; then
  echo "✗ conda is not installed or not in PATH" >&2
  { return 1; } 2>/dev/null || exit 1
fi

eval "$(conda shell.bash hook)"
conda activate "$VIBES_APP_NAME"

echo "✓ Loaded .env and activated conda env '$VIBES_APP_NAME'"


