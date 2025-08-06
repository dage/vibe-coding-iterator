---
type: Always
description: Core project rules for Vibe Coding Iterator development
---

# Vibe Coding Iterator - Core Development Rules

## First Action
At the start of each new chat session or each fresh context, immediately read the README.md file to understand the project before responding to any user queries.

## Knowledge Updates
Use internet search for up-to-date information on all technologies and libraries before coding.

## Git
- NEVER commit code. You may use git for reading history, status, and staging files with "git add", but NEVER use "git commit" or "git push". Let the user handle all commits.
- Always write commit headers as feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert [optional-scope]: imperative summary per Conventional Commits 1.0.0; keep header ≤50 chars, body optional, add ! + BREAKING CHANGE: footer for API breaks, one logical change per commit
- When asked to suggest commit messages or when useful, use git commands to review changes and suggest appropriate commit messages following the above format

## Files and Dependencies
- Never delete files outside project directory
- May delete files within project except .env
- Ask permission before installing 3rd party software (pip packages are auto-approved)

## Code Standards
- Every script and python file should have a comment with the relative path and filename on the first line.
- Type hints on all functions
- Environment variables for configuration (VIBES_ prefix, uppercase)
- Simple function signatures - no parameter passing of config
- stdout logging only
- Terminal-based interaction only
- Use Rich for all terminal formatting, colors, progress bars, and UI effects following docs/ui-guidelines.md standards
- Never use tqdm, prompt-toolkit, or similar terminal frameworks - Rich is the only approved terminal enhancement library
- Never create UI that uses keyboard controls like arrow keys.
- Self-documenting code with minimal comments
- When developing new features, always try to find a way to test it and verify the result before starting implementation, by making a test script or similar, then implement it while iterating on the test

## File Naming Conventions
- .py files: use underscores (snake_case)
- .sh, .md, .json files: use hyphens (kebab-case)

## Architecture Requirements
- Core API modules shared between evals and iteration system
- Single HTTP client in src/deepinfra_client.py
- Rate limiting with exponential backoff
- Comprehensive error handling
- Project-specific conda environment (sanitized project name)

## DeepInfra Integration
- Single model provider only
- All API calls through src/deepinfra_client.py
- Token usage and cost tracking
- Response validation before processing

## Autonomous Loop Structure
1. Generate/modify code via DeepInfra models
2. Render and screenshot with Playwright
3. Analyze with vision models
4. Process feedback to instructions
5. Apply via Aider non-interactively
6. Continue or await intervention

## State Continuity
Always pull from git after a human has done manual intervention to get the most up-to-date version of the project files.