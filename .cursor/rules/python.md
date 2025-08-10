---
type: Auto Attached
globs: ["**/*.py"]
description: Python development patterns and coding standards
---

# Python Development Rules

## Code Patterns
- First line: relative file path and filename comment
- Strive for self contained python modules that have no or minim side effects.
- Any side effects should be documented in the file header comments
- All model queries (vision and code generation) handled by OpenRouter HTTP client
- Model configuration loaded from environment variables (VIBES_VISION_MODEL, VIBES_CODE_MODEL)
- Load VIBES_ environment variables at startup
- Handle API failures gracefully with fallbacks
- Dependency checks are performed by `setup.sh`; do not import or check at runtime
- Use underscores (snake_case) for .py filenames

## Defensive Coding
- Validate inputs and required env vars early; after validation, assume invariants hold throughout the script to keep code simple and avoid repeated checks.

## Evaluation Scripts
- Standalone execution with clear pass/fail indicators
- Individual or suite execution via evals/run_all.py
- Terminal-based progress reporting

## Model Integration
- Vision: Screenshot analysis, layout validation, bug detection
- Code generation: Context-aware improvements, bug fixes

## Aider Integration
- Non-interactive mode during autonomous loops
- Interactive mode for manual developer takeover