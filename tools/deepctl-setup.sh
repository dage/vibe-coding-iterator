#!/bin/bash
# tools/deepctl-setup.sh - deepctl installation and version checking utilities

# Check if deepctl is available and show version information
check_deepctl() {
    echo "Checking deepctl availability..."
    
    # Get latest version from GitHub
    echo "Latest version on GitHub:"
    if command -v curl >/dev/null 2>&1; then
        latest_version=$(curl -s https://api.github.com/repos/deepinfra/deepctl/releases/latest | grep '"tag_name"' | cut -d'"' -f4 2>/dev/null)
        if [ -n "$latest_version" ]; then
            echo "  $latest_version"
        else
            echo "  Unable to fetch latest version"
        fi
    else
        echo "  curl not available, cannot fetch latest version"
    fi
    
    # Check local installation
    echo "Local installation:"
    if command -v deepctl >/dev/null 2>&1; then
        local_version=$(deepctl version info 2>/dev/null | head -n1)
        if [ -n "$local_version" ]; then
            echo "  $local_version"
            return 0
        else
            echo "  deepctl found but version unknown"
            return 0
        fi
    else
        echo "  Not installed"
        return 1
    fi
}

# Install deepctl
install_deepctl() {
    echo "Installing deepctl..."
    
    # Check if already installed
    if command -v deepctl >/dev/null 2>&1; then
        echo "✓ deepctl is already installed"
        deepctl version info 2>/dev/null | head -n1
        return 0
    fi
    
    # Check OS (designed for macOS but don't block other Unix-like systems)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Detected macOS - proceeding with installation"
    else
        echo "Warning: Installation tested on macOS, proceeding anyway..."
    fi
    
    # Download and install the macOS binary directly
    LATEST_VERSION=$(curl -s https://api.github.com/repos/deepinfra/deepctl/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
    DOWNLOAD_URL="https://github.com/deepinfra/deepctl/releases/download/${LATEST_VERSION}/deepctl-macos"
    
    if curl -fsSL -o /tmp/deepctl "$DOWNLOAD_URL" && chmod +x /tmp/deepctl && sudo mv /tmp/deepctl /usr/local/bin/deepctl; then
        echo "✓ deepctl installation completed"
        
        # Verify installation
        if command -v deepctl >/dev/null 2>&1; then
            echo "✓ Installation verified:"
            deepctl version info 2>/dev/null | head -n1 || echo "  deepctl available (version check failed)"
            return 0
        else
            echo "✗ Installation completed but deepctl not found in PATH"
            echo "You may need to restart your terminal or manually add deepctl to PATH"
            return 1
        fi
    else
        echo "✗ Failed to install deepctl"
        return 1
    fi
}

# Uninstall deepctl
uninstall_deepctl() {
    echo "Uninstalling deepctl..."
    
    if command -v deepctl >/dev/null 2>&1; then
        if sudo rm -f /usr/local/bin/deepctl; then
            echo "✓ deepctl uninstalled successfully"
            return 0
        else
            echo "✗ Failed to uninstall deepctl"
            return 1
        fi
    else
        echo "deepctl is not installed"
        return 0
    fi
}

# Allow script to be called directly or sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-}" in
        "check")
            check_deepctl
            ;;
        "install")
            install_deepctl
            ;;
        "uninstall")
            uninstall_deepctl
            ;;
        *)
            echo "Usage: $0 {check|install|uninstall}"
            echo "  check     - Check deepctl installation and versions"
            echo "  install   - Install deepctl"
            echo "  uninstall - Uninstall deepctl"
            exit 1
            ;;
    esac
fi