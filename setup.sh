#!/bin/bash
# setup.sh - Setup script for vibe-coding-iterator

set -e

# Get script directory for reliable path handling
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source the deepctl setup functions
source "$SCRIPT_DIR/tools/deepctl-setup.sh"

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

echo "Using conda environment name: $sanitized_name"
echo

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
conda activate "$sanitized_name"
echo "✓ Conda environment '$sanitized_name' is now active"

# Check deepctl availability
echo
echo "=== DeepInfra Setup ==="
if check_deepctl; then
    echo
    echo "✓ deepctl is already installed and available"
else
    echo
    echo "deepctl is required for this project to interact with DeepInfra models."
    read -p "Would you like to install deepctl automatically? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if install_deepctl; then
            echo "✓ deepctl setup completed successfully"
        else
            echo "✗ Failed to install deepctl"
            echo "Please install manually: curl https://deepinfra.com/get.sh | sh"
            echo "Or visit: https://github.com/deepinfra/deepctl"
            exit 1
        fi
    else
        echo "Setup cannot continue without deepctl."
        echo "To install manually: curl https://deepinfra.com/get.sh | sh"
        echo "Then run ./setup.sh again"
        exit 1
    fi
fi

echo
echo "=== Model Configuration ==="
echo "You can now configure your preferred models for vision and code generation."
read -p "Would you like to configure models now? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running model selection tool..."
    python3 src/check_deps.py  # Ensure dependencies are available
    ./tools/select-models.sh
    echo "✓ Model configuration completed"
else
    echo "You can configure models later by running: ./tools/select-models.sh"
fi

echo
echo "=== Setup Complete ==="
echo "✓ Conda environment '$sanitized_name' is active"
echo "✓ Python dependencies are installed"
echo "✓ deepctl is ready to use"
echo "✓ Model configuration system is available"
echo
echo "Next steps:"
echo "- Set up DeepInfra API key"
echo "- Run initial tests"
echo
echo "To activate this environment in future sessions:"
echo "  conda activate $sanitized_name"