#!/bin/bash
# setup.sh - Setup script for vibe-coding-iterator

set -e

# Get script directory for reliable path handling
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source the deepctl setup functions
source "$SCRIPT_DIR/tools/deepctl-setup.sh"

echo "=== Vibe Coding Iterator Setup ==="
echo

# Check deepctl availability
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
    ./tools/select_models.sh
    echo "✓ Model configuration completed"
else
    echo "You can configure models later by running: ./tools/select_models.sh"
fi

echo
echo "=== Setup Complete ==="
echo "✓ deepctl is ready to use"
echo "✓ Model configuration system is available"
echo
echo "Next steps will include:"
echo "- Creating conda environment"
echo "- Setting up DeepInfra API key"  
echo "- Installing Python dependencies"
echo "- Running initial tests"