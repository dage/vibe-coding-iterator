---
type: Auto Attached
globs: ["*.sh", "tools/*.sh"]
description: Shell script development patterns and standards
---

# Shell Script Development Rules

## Script Patterns
- Use conda activate for environment switching
- Provide clear progress feedback
- Handle essential error cases
- Use hyphens (kebab-case) for .sh filenames

## Setup Scripts
- Prompt for sanitized project name
- Create project-specific conda environment
- Configure VIBES_ environment variables
- Test complete pipeline functionality

## Utility Scripts
- Manual execution for common maintenance tasks
- Clear usage instructions and output