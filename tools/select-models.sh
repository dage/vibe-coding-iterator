#!/usr/bin/env bash
# tools/select-models.sh

set -euo pipefail

# Get script directory for reliable path handling
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

CFG="$PROJECT_ROOT/config/models.json"
INSPECT_PY="$PROJECT_ROOT/src/model_inspector.py"
TMP="/tmp/available_models.json"

timestamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }

# Parse command line arguments
LIMIT=""
YES_MODE=false
MODEL_DETAILS=""
VISION_MODELS=""
CODE_MODELS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --limit)
            LIMIT="$2"
            shift 2
            ;;
        --yes)
            YES_MODE=true
            shift
            ;;
        --model-details)
            MODEL_DETAILS="$2"
            shift 2
            ;;
        --vision-models)
            VISION_MODELS="$2"
            shift 2
            ;;
        --code-models)
            CODE_MODELS="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --limit N           Limit number of models to process"
            echo "  --yes               Automatically answer 'yes' to all prompts"
            echo "  --model-details N   Show detailed info for model index N"
            echo "  --vision-models N   Comma-separated list of vision model indices"
            echo "  --code-models N     Comma-separated list of code model indices"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# 2-1  show current config (if present)
if [[ -f $CFG ]]; then
  echo "Current models.json  (created: $(jq -r .created "$CFG"))"
  jq . "$CFG" | sed 's/^/   /'
else
  echo "No models.json detected."
fi
echo

# Handle model details query if specified
if [[ -n "$MODEL_DETAILS" ]]; then
    echo "Getting detailed information for model #$MODEL_DETAILS..."
    python3 "$INSPECT_PY" --output "$TMP" --query "?$MODEL_DETAILS"
    exit 0
fi

# Check if we should proceed with model selection
if [[ "$YES_MODE" == true ]]; then
    echo "Auto-mode: proceeding with model selection"
else
    read -rp "Re-select models? (y/N) " yn
    [[ "${yn}" =~ ^[Yy]$ ]] || exit 0
fi
echo

# 2-2  build fresh catalogue (writes JSON & prints markdown table w/ timestamp)
INSPECT_ARGS="--output $TMP --format markdown-table --workers 10"
if [[ -n "$LIMIT" ]]; then
    INSPECT_ARGS="$INSPECT_ARGS --limit $LIMIT"
fi

if ! python3 "$INSPECT_PY" $INSPECT_ARGS; then
    echo "✗ Failed to build model catalogue"
    echo "Please check your DeepInfra setup and network connection"
    exit 1
fi

if [[ ! -f "$TMP" ]] || [[ ! -s "$TMP" ]]; then
    echo "✗ No model data was generated"
    exit 1
fi
echo

# Function to get detailed model info
get_model_details() {
    local index=$1
    echo >&2
    # Get model name from the JSON data
    local model_name=$(jq -r ".[$((index-1))].id" "$TMP" 2>/dev/null || echo "unknown")
    echo "Getting detailed information for model #$index: $model_name..." >&2
    python3 "$INSPECT_PY" --output "$TMP" --query "?$index" >&2
    echo >&2
}

# Get vision models
if [[ -n "$VISION_MODELS" ]]; then
    echo "Auto-mode: Using vision models: $VISION_MODELS"
    vis="$VISION_MODELS"
elif [[ "$VISION_MODELS" == "" ]]; then
    echo "Auto-mode: Using empty vision models list"
    vis=""
else
    echo "Interactive model selection:"
    echo "- Enter model indices (comma-separated) for each category"
    echo "- Use '?<index>' to get detailed information about a specific model"
    echo "- Example: '?5' to see details for model #5"
    echo

    echo "Enter indices for **VISION** models: "
    while true; do
        read -rp "> " vis_input
        
        # Check if user wants detailed info
        if [[ "$vis_input" =~ ^\?[0-9]+$ ]]; then
            index=${vis_input#?}
            get_model_details "$index"
            continue
        fi
        
        # Validate input format for model selection
        if [[ -n "$vis_input" ]] && [[ ! "$vis_input" =~ ^[0-9,[:space:]]*$ ]]; then
            echo "✗ Invalid input format. Use comma-separated numbers (e.g., 1,2,3) or '?<number>' for details" >&2
            continue
        fi
        
        vis="$vis_input"
        break
    done
fi

# Get code models
if [[ -n "$CODE_MODELS" ]]; then
    echo "Auto-mode: Using code models: $CODE_MODELS"
    cod="$CODE_MODELS"
elif [[ "$CODE_MODELS" == "" ]]; then
    echo "Auto-mode: Using empty code models list"
    cod=""
else
    echo "Enter indices for **CODE**   models: "
    while true; do
        read -rp "> " cod_input
        
        # Check if user wants detailed info
        if [[ "$cod_input" =~ ^\?[0-9]+$ ]]; then
            index=${cod_input#?}
            get_model_details "$index"
            continue
        fi
        
        # Validate input format for model selection
        if [[ -n "$cod_input" ]] && [[ ! "$cod_input" =~ ^[0-9,[:space:]]*$ ]]; then
            echo "✗ Invalid input format. Use comma-separated numbers (e.g., 1,2,3) or '?<number>' for details" >&2
            continue
        fi
        
        cod="$cod_input"
        break
    done
fi

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