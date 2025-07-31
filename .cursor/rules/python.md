---
type: Auto Attached
globs: ["src/*.py", "evals/*.py", "tools/*.py"]
description: Python development patterns and coding standards
---

# Python Development Rules

## Code Patterns
- Use src/deepinfra_client.py for all API calls
- Load VIBES_ environment variables at startup
- Handle API failures gracefully with fallbacks

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