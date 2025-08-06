---
type: Auto Attached
globs: ["src/*.py", "evals/*.py", "tools/*.py"]
description: Python development patterns and coding standards
---

# Python Development Rules

## Code Patterns
- Strive for self contained python modules that have no or minim side effects.
- Any side effects should be documented in the file header comments
- All model queries (vision and code generation) handled by src/model_client.py
- src/model_client.py loads model config from config folder on initialization
- Load VIBES_ environment variables at startup
- Handle API failures gracefully with fallbacks
- Run dependency checks at script startup: `from check_deps import ensure_dependencies; ensure_dependencies()`
- Use underscores (snake_case) for .py filenames

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