---
type: Always
description: Core project rules for Vibe Coding Iterator development
---

# Vibe Coding Iterator - Core Development Rules

## Agent Interaction
- Always provide independent analysis and constructive critique, avoiding flattery and uncritical agreement.
- Provide minimal, specific solutions that address only the exact request rather than adding comprehensive boilerplate or "standard" patterns that aren't actually needed in the project.
- Make incremental changes that improve the codebase step-by-step. Before adding any new abstraction, mechanism, or complexity, ensure the current implementation works and ask yourself: "Is this change absolutely necessary to fulfill the user's request?" If not, stop.

## Session Start
- Read README.md in each new chat session.

## Knowledge Updates
- Use internet search for up-to-date information on all technologies and libraries before coding.

## Git
- NEVER use destructive git commands, including but not limited to `commit`, `push`, `reset`, `rebase`, `merge`, or `checkout` with file changes. All commits and history-altering operations must be handled by the user.
- You are encouraged to use read-only git commands freely to understand the repository, such as `log`, `status`, `diff`, `show`, and `blame`. You may also stage files using `git add`.
- After completing a task that results in file changes, proactively suggest a commit message that follows the project's conventions.
- Before formatting a commit message, inspect the last 10 commits (`git log -10`) to ensure the style (e.g. use of scope, tense, body formatting) is consistent with the project's history.
- Always write commit headers as feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert: imperative summary per Conventional Commits 1.0.0; keep header ≤50 chars, body optional, add ! + BREAKING CHANGE: footer for API breaks, one logical change per commit.

## Files and Dependencies
- Never delete files outside project directory
- May delete files within project except .env
- Ask permission before installing 3rd party software (pip packages are auto-approved)

## Code Standards
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
1.  Generate/modify code via DeepInfra models
2.  Render and screenshot with Playwright
3.  Analyze with vision models
4.  Process feedback to instructions
5.  Apply via Aider non-interactively
6.  Continue or await intervention

## State Continuity
- Always pull from git after a human has done manual intervention to get the most up-to-date version of the project files.
