#!/bin/bash
# setup.sh

set -e

# Get script directory for reliable path handling
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"



echo "=== Vibe Coding Iterator Setup ==="
echo

# Function to sanitize project name for conda environment
sanitize_project_name() {
    local name="$1"
    # Convert to lowercase, replace spaces and special chars with hyphens, remove leading/trailing hyphens
    echo "$name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/^-\+//' | sed 's/-\+$//'
}

# Function to check if conda environment exists
conda_env_exists() {
    local env_name="$1"
    conda env list | grep -q "^$env_name "
}

# Function to check if conda environment has all required packages
check_env_packages() {
    local env_name="$1"
    local requirements_file="$2"
    
    # Activate environment temporarily to check packages
    eval "$(conda shell.bash hook)"
    conda activate "$env_name" 2>/dev/null || return 1
    
    # Read requirements and check each package
    while IFS= read -r line; do
        # Skip comments and empty lines
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// }" ]] && continue
        
        # Extract package name (before >=, ==, etc.)
        local package_name=$(echo "$line" | sed 's/[<>=!].*//' | tr -d ' ')
        
        if [[ -n "$package_name" ]]; then
            if ! python -c "import $package_name" 2>/dev/null; then
                conda deactivate 2>/dev/null || true
                return 1
            fi
        fi
    done < "$requirements_file"
    
    conda deactivate 2>/dev/null || true
    return 0
}

# Function to create and setup conda environment
setup_conda_env() {
    local env_name="$1"
    local requirements_file="$2"
    
    echo "Creating conda environment: $env_name"
    conda create -n "$env_name" python=3.11 -y
    
    echo "Installing Python packages..."
    eval "$(conda shell.bash hook)"
    conda activate "$env_name"
    pip install -r "$requirements_file"
    conda deactivate
    
    echo "✓ Conda environment setup completed"
}

# Get project name from user
echo "=== Project Configuration ==="
read -p "Enter your vibe project name: " project_name

if [[ -z "$project_name" ]]; then
    echo "✗ Project name cannot be empty"
    exit 1
fi

# Sanitize project name
sanitized_name=$(sanitize_project_name "$project_name")

if [[ "$sanitized_name" != "$project_name" ]]; then
    echo "Project name sanitized: '$project_name' → '$sanitized_name'"
fi



# Check if conda is available
if ! command -v conda >/dev/null 2>&1; then
    echo "✗ conda is not installed or not in PATH"
    echo "Please install Anaconda or Miniconda first:"
    echo "  https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Check if conda environment exists and has required packages
if conda_env_exists "$sanitized_name"; then
    echo "✓ Conda environment '$sanitized_name' already exists"
    
    if check_env_packages "$sanitized_name" "$SCRIPT_DIR/requirements.txt"; then
        echo "✓ Environment has all required packages"
        echo "✓ Conda environment is ready to use"
    else
        echo "⚠ Environment is missing some required packages"
        read -p "Recreate the environment? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Removing existing environment..."
            conda env remove -n "$sanitized_name" -y
            setup_conda_env "$sanitized_name" "$SCRIPT_DIR/requirements.txt"
        else
            echo "Please manually install missing packages or recreate the environment"
            exit 1
        fi
    fi
else
    echo "Creating new conda environment: $sanitized_name"
    setup_conda_env "$sanitized_name" "$SCRIPT_DIR/requirements.txt"
fi

# Activate the conda environment
echo
echo "=== Activating Conda Environment ==="
eval "$(conda shell.bash hook)"
if [[ -n "$CONDA_DEFAULT_ENV" && "$CONDA_DEFAULT_ENV" != "$sanitized_name" ]]; then
    conda deactivate || true
fi
conda activate "$sanitized_name"
echo "✓ Conda environment '$sanitized_name' is now active"

# Setup OpenRouter configuration
echo
echo "=== OpenRouter Configuration ==="
echo "This project uses OpenRouter API for AI model access."
echo

# Check if .env file exists and validate required variables
ENV_FILE="$SCRIPT_DIR/.env"
CONFIGURE_OPENROUTER=false

if [[ -f "$ENV_FILE" ]]; then
    echo "✓ Found existing .env file"

    # Ask whether to reuse or create new
    while true; do
        read -p "Reuse existing .env? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            REUSE_ENV=true
            break
        elif [[ $REPLY =~ ^[Nn]$ || -z "$REPLY" ]]; then
            REUSE_ENV=false
            break
        else
            echo "Please answer y or n."
        fi
    done

    if [[ "$REUSE_ENV" == true ]]; then
        # Check if all required environment variables are defined
        MISSING_VARS=()
        if ! grep -q "^VIBES_API_KEY=" "$ENV_FILE"; then
            MISSING_VARS+=("VIBES_API_KEY")
        fi
        if ! grep -q "^VIBES_VISION_MODEL=" "$ENV_FILE"; then
            MISSING_VARS+=("VIBES_VISION_MODEL")
        fi
        if ! grep -q "^VIBES_CODE_MODEL=" "$ENV_FILE"; then
            MISSING_VARS+=("VIBES_CODE_MODEL")
        fi

        if [[ ${#MISSING_VARS[@]} -eq 0 ]]; then
            echo "✓ All required environment variables are configured"
            echo "Current OpenRouter configuration:"
            echo "  API Key: $(grep "^VIBES_API_KEY=" "$ENV_FILE" | cut -d'=' -f2 | sed 's/.*/***/g')"
            echo "  Vision Model: $(grep "^VIBES_VISION_MODEL=" "$ENV_FILE" | cut -d'=' -f2)"
            echo "  Code Model: $(grep "^VIBES_CODE_MODEL=" "$ENV_FILE" | cut -d'=' -f2)"
            echo "Configuration looks complete."
            # Ensure VIBES_APP_NAME is present and up to date with sanitized project name
            if grep -q "^VIBES_APP_NAME=" "$ENV_FILE"; then
                tmpfile=$(mktemp)
                sed "s/^VIBES_APP_NAME=.*/VIBES_APP_NAME=$sanitized_name/" "$ENV_FILE" > "$tmpfile" && mv "$tmpfile" "$ENV_FILE"
            else
                echo "VIBES_APP_NAME=$sanitized_name" >> "$ENV_FILE"
            fi
        else
            echo "⚠ Missing required environment variables: ${MISSING_VARS[*]}"
            echo "The .env file needs to be recreated to include all required variables."
            read -p "Recreate .env file? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                CONFIGURE_OPENROUTER=true
            else
                echo "✗ Cannot continue without complete OpenRouter configuration"
                exit 1
            fi
        fi
    else
        echo "Will create a new .env"
        CONFIGURE_OPENROUTER=true
    fi
else
    echo "No .env found yet — let's configure OpenRouter now."
    CONFIGURE_OPENROUTER=true
fi

if [[ "$CONFIGURE_OPENROUTER" == true ]]; then
    # Suggested default models (open source, low cost, solid capabilities)
    DEFAULT_VISION_MODEL="meta-llama/llama-3.2-90b-vision-instruct"
    DEFAULT_CODE_MODEL="z-ai/glm-4.5-air"
    echo "Enter your OpenRouter API key:"
    echo "(Get one from: https://openrouter.ai/settings/keys)"
    echo "Note: input is hidden for security; type and press Enter."
    # Validate API key immediately; re-prompt until it passes
    BASE_URL_VALIDATE="https://openrouter.ai/api/v1"
    while true; do
        read -p "API Key: " -s api_key
        echo
        if [[ -z "$api_key" ]]; then
            echo "✗ API key cannot be empty"
            continue
        fi
        code=$(curl -sS -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $api_key" "$BASE_URL_VALIDATE/models")
        if [[ "$code" == "200" ]]; then
            echo "✓ API key accepted"
            break
        else
            echo "✗ API key was not accepted (HTTP $code). Please try again."
        fi
    done
    
    echo "Enter the OpenRouter model slug for vision tasks:"
    echo "(Default: $DEFAULT_VISION_MODEL)"
    read -p "Vision Model [$DEFAULT_VISION_MODEL]: " vision_model
    vision_model=${vision_model:-$DEFAULT_VISION_MODEL}
    
    echo "Enter the OpenRouter model slug for code generation:"
    echo "(Default: $DEFAULT_CODE_MODEL)"
    read -p "Code Model [$DEFAULT_CODE_MODEL]: " code_model
    code_model=${code_model:-$DEFAULT_CODE_MODEL}
    
    # Create or update .env file
    {
        echo "# Vibe Coding Iterator - OpenRouter Configuration"
        echo "# Generated on $(date)"
        echo ""
        echo "# OpenRouter base URL"
        echo "OPENROUTER_BASE_URL=https://openrouter.ai/api/v1"
        echo ""
        echo "# OpenRouter API key - get from https://openrouter.ai/settings/keys"
        echo "VIBES_API_KEY=$api_key"
        echo ""
        echo "# Vision model for screenshot analysis"
        echo "VIBES_VISION_MODEL=$vision_model"
        echo ""
        echo "# Code generation model"
        echo "VIBES_CODE_MODEL=$code_model"
        echo ""
        echo "# App name used for attribution headers (required)"
        echo "VIBES_APP_NAME=$sanitized_name"
    } > "$ENV_FILE"
    
    echo "✓ OpenRouter configuration saved to .env"
fi



echo
echo "=== Setup Complete ==="
echo "✓ Conda environment '$sanitized_name' is active"
echo "✓ Python dependencies are installed"
echo "✓ OpenRouter API configuration is ready"
echo
echo "Your environment variables:"
echo "- VIBES_API_KEY: Configured"
if [[ -f "$ENV_FILE" ]]; then
    echo "- VIBES_VISION_MODEL: $(grep "VIBES_VISION_MODEL=" "$ENV_FILE" | cut -d'=' -f2)"
    echo "- VIBES_CODE_MODEL: $(grep "VIBES_CODE_MODEL=" "$ENV_FILE" | cut -d'=' -f2)"
    echo "- VIBES_APP_NAME: $(grep "^VIBES_APP_NAME=" "$ENV_FILE" | cut -d'=' -f2)"
else
    echo "- VIBES_VISION_MODEL: (not configured)"
    echo "- VIBES_CODE_MODEL: (not configured)"
    echo "- VIBES_APP_NAME: $sanitized_name"
fi
echo
echo "=== Integration Test ==="
# Validate OpenRouter API access without consuming credits by listing models
OR_BASE_URL="${OPENROUTER_BASE_URL:-https://openrouter.ai/api/v1}"
OR_API_KEY="$(grep '^VIBES_API_KEY=' "$ENV_FILE" | cut -d'=' -f2)"

if curl -sSf -H "Authorization: Bearer $OR_API_KEY" "$OR_BASE_URL/models" >/dev/null; then
  echo "✓ OpenRouter API reachable and API key accepted"
else
  echo "✗ Integration test failed: models endpoint unreachable or API key rejected"
  echo "  - Verify internet connectivity"
  echo "  - Check VIBES_API_KEY in .env and optional OPENROUTER_BASE_URL"
  exit 1
fi

# Query API key details
KEY_URL="$OR_BASE_URL/key"
tmp_json=$(mktemp)
http_code=$(curl -sS -o "$tmp_json" -w "%{http_code}" -H "Authorization: Bearer $OR_API_KEY" "$KEY_URL")

if [[ "$http_code" == "200" ]]; then
  echo "✓ API key details (HTTP 200):"
  python - <<'PY'
import json, sys
path = sys.argv[1]
data = json.load(open(path))
info = data.get("data", {})
label = info.get("label")
limit = info.get("limit")
usage = info.get("usage")
remain = info.get("limit_remaining")
free = info.get("is_free_tier")
prov = info.get("is_provisioning_key")
print(f"  - label: {label}")
print(f"  - limit: {limit}")
print(f"  - usage: {usage}")
print(f"  - limit_remaining: {remain}")
print(f"  - is_free_tier: {free}")
print(f"  - is_provisioning_key: {prov}")
PY
  "$tmp_json"
else
  echo "✗ API key check failed (HTTP $http_code). Response body:" 
  cat "$tmp_json"
fi
rm -f "$tmp_json"