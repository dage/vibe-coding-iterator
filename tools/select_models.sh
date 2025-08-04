#!/usr/bin/env bash
# tools/select_models.sh

set -euo pipefail

# Get script directory for reliable path handling
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

CFG="$PROJECT_ROOT/config/models.json"
INSPECT_PY="$PROJECT_ROOT/src/model_inspector.py"
TMP="/tmp/available_models.json"

timestamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }

# 2-1  show current config (if present)
if [[ -f $CFG ]]; then
  echo "Current models.json  (created: $(jq -r .created "$CFG"))"
  jq . "$CFG" | sed 's/^/   /'
else
  echo "No models.json detected."
fi
echo

read -rp "Re-select models? (y/N) " yn
[[ "${yn}" =~ ^[Yy]$ ]] || exit 0
echo

# 2-2  build fresh catalogue (writes JSON & prints markdown table w/ timestamp)
echo "Building model catalogue (this may take a moment)..."
python3 "$INSPECT_PY" --output "$TMP" --format markdown-table --limit 20
echo

# 2-3  gather user choices by index (comma-separated)
read -rp "Enter indices for **VISION** models: " vis
read -rp "Enter indices for **CODE**   models: " cod

# 2-4  rewrite config
new_created=$(timestamp)
jq --arg created "$new_created" \
   --arg vis "$vis" --arg cod "$cod" \
'def pick($set): 
  .[] | select((.index|tostring) as $i | $i | IN($set))
  | {id, token_cost};
{
  created: $created,
  vision:  [pick($vis)],
  code:    [pick($cod)]
}' "$TMP" > "$CFG"

echo "✓  Updated $CFG" 