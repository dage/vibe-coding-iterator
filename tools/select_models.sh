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
if ! python3 "$INSPECT_PY" --output "$TMP" --format markdown-table --workers 10; then
    echo "✗ Failed to build model catalogue"
    echo "Please check your DeepInfra setup and network connection"
    exit 1
fi

if [[ ! -f "$TMP" ]] || [[ ! -s "$TMP" ]]; then
    echo "✗ No model data was generated"
    exit 1
fi
echo

# 2-3  interactive model selection with detailed info option
echo "Interactive model selection:"
echo "- Enter model indices (comma-separated) for each category"
echo "- Use '?<index>' to get detailed information about a specific model"
echo "- Example: '?5' to see details for model #5"
echo

# Function to get detailed model info
get_model_details() {
    local index=$1
    echo
    echo "Getting detailed information for model #$index..."
    python3 "$INSPECT_PY" --output "$TMP" --query "?$index"
    echo
}

# Function to handle user input with detailed queries
handle_model_selection() {
    local category=$1
    local prompt=$2
    
    while true; do
        read -rp "$prompt" input
        
        # Check if user wants detailed info
        if [[ "$input" =~ ^\?[0-9]+$ ]]; then
            local index=${input#?}
            get_model_details "$index"
            continue
        fi
        
        # Validate input format for model selection
        if [[ -n "$input" ]] && [[ ! "$input" =~ ^[0-9,[:space:]]*$ ]]; then
            echo "✗ Invalid input format. Use comma-separated numbers (e.g., 1,2,3) or '?<number>' for details"
            continue
        fi
        
        echo "$input"
        break
    done
}

# Get vision models
vis=$(handle_model_selection "vision" "Enter indices for **VISION** models: ")

# Get code models  
cod=$(handle_model_selection "code" "Enter indices for **CODE**   models: ")

# 2-4  rewrite config
new_created=$(timestamp)

# Parse the comma-separated indices into arrays - handle empty inputs
if [[ -n "$vis" ]]; then
    vis_indices=$(echo "$vis" | jq -R 'split(",") | map(. | tonumber)')
else
    vis_indices="[]"
fi

if [[ -n "$cod" ]]; then
    cod_indices=$(echo "$cod" | jq -R 'split(",") | map(. | tonumber)')
else
    cod_indices="[]"
fi

# Generate the config using the parsed indices
if ! jq --argjson created "\"$new_created\"" \
       --argjson vis_indices "$vis_indices" \
       --argjson cod_indices "$cod_indices" \
'{
  created: $created,
  vision_models: [.[] | select(.index as $i | $vis_indices | index($i) != null) | {id, token_cost}],
  code_models: [.[] | select(.index as $i | $cod_indices | index($i) != null) | {id, token_cost}]
}' "$TMP" > "$CFG"; then
    echo "✗ Failed to generate configuration file"
    exit 1
fi

# Validate the generated config
if [[ ! -f "$CFG" ]] || ! jq empty "$CFG" 2>/dev/null; then
    echo "✗ Generated configuration file is invalid"
    exit 1
fi

echo "✓  Updated $CFG" 