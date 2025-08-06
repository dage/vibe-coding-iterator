#!/usr/bin/env python3
# src/check_deps.py

"""
check_deps.py - Dependency checking for Vibe Coding Iterator

Checks for required dependencies and provides helpful error messages.
"""
import sys
from typing import Dict, List, Optional

def check_rich() -> bool:
    """Check if Rich library is available."""
    try:
        import rich
        return True
    except ImportError:
        return False

def check_deepctl() -> bool:
    """Check if deepctl is available."""
    try:
        import subprocess
        result = subprocess.run(["deepctl", "--version"], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False

def check_requests() -> bool:
    """Check if requests library is available."""
    try:
        import requests
        return True
    except ImportError:
        return False

def check_jq() -> bool:
    """Check if jq is available."""
    try:
        import subprocess
        result = subprocess.run(["jq", "--version"], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False

def check_dependencies() -> Dict[str, bool]:
    """Check all required dependencies."""
    return {
        "rich": check_rich(),
        "deepctl": check_deepctl(),
        "requests": check_requests(),
        "jq": check_jq()
    }

def print_missing_deps_error(missing_deps: List[str]) -> None:
    """Print error message for missing dependencies."""
    print("✗ Missing required dependencies:", file=sys.stderr)
    for dep in missing_deps:
        print(f"   - {dep}", file=sys.stderr)
    print("\nPlease run ./setup.sh to install missing dependencies.", file=sys.stderr)
    sys.exit(1)

def ensure_dependencies(required_deps: Optional[List[str]] = None) -> None:
    """
    Ensure required dependencies are available.
    
    Args:
        required_deps: List of dependency names to check. If None, checks all.
    """
    if required_deps is None:
        required_deps = ["rich", "deepctl", "requests", "jq"]
    
    deps_status = check_dependencies()
    missing_deps = [dep for dep in required_deps if not deps_status.get(dep, False)]
    
    if missing_deps:
        print_missing_deps_error(missing_deps)

if __name__ == "__main__":
    # When run directly, check all dependencies
    ensure_dependencies()
    print("✓ All dependencies are available") 