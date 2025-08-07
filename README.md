# Vibe Coding Iterator

AI-driven development system for graphical web applications using autonomous vision-guided iteration loops and open source models.

## Project Description

Vibe Coding Iterator extends traditional vibe coding by introducing autonomous vision-guided iteration after an initial single-shot implementation. The system targets graphical intensive web applications including special effects and games.

Key differentiators:

1. **Vision-guided iteration**: Vision models evaluate visual output and guide autonomous improvements, removing humans from the feedback loop. Focus on single image analysis with animation analysis as ongoing experimental feature.
2. **Open source model focus**: Leverages cost-effective open source models instead of expensive proprietary frontier models.
3. **Unified model provider**: Single API provider (OpenRouter) and required API key enables assumptions about specific models availability and provides opportunities to use AI models as replacements for traditional software logic throughout the system. It also simplifies the whole process by sharing an API credits pool across the project and getting invoices from a single provider.
4. **Future Proof & AGI-ready**: This system is meant to take over where the code generation models stop after single-shotting, to get that extra performance beyond what the model can do on itself, so as the models keep improving towards AGI, this system is meant to raise the ceiling in terms what can be achieved by vibe coding.

The system can run autonomously for extended periods while allowing developer interruption for guidance changes, manual coding takeover, context management or switching models.



## Design Guidelines

This project prioritizes **simplicity and modularity** to maximize focus on AI model optimization and workflow experimentation rather than complex codebase maintenance:

- **Slack product requirements**: Omits code for cleanup, file logging, and similar production concerns
- **Terminal-only interface**: Simple text-based UI without keyboard navigation or mouse/pointer support
- **Simple function signatures**: Model identifiers and configuration stored as environment variables, not passed as function parameters
- **Environment variable prefixing**: All variables prefixed with `VIBES_` to avoid conflicts (e.g., `VIBES_API_KEY`)
- **Project-specific conda environments**: Each project gets its own conda environment matching the sanitized project name
- **Minimal dependencies**: Only essential packages, avoiding over-engineering
- **DRY principle**: Shared core modules between evaluation and iteration systems
- **Smooth developer experience**: Efficient workflows for switching between autonomous and manual development and allowing developer to use favorite IDE for manual takeover

## Directory Structure

```
vibe-coding-iterator/
├── .cursor/
│   └── rules/               # Cursor IDE development rules
│       ├── project.md
│       ├── python.md
│       └── shell.md
├── .env                     # Environment variables (created by setup script)
├── .gitignore
├── README.md
├── requirements.txt
├── setup.sh                 # Main setup script
├── docs/                    # Project documentation
│   └── ui-guidelines.md     # Terminal UI standards for Rich library usage
├── src/                     # All main Python source code modules
│   └── or_client.py         # OpenRouter client and Conversation helper
└── tools/                   # Utility scripts (currently empty)
```

## Tech Stack

- OpenRouter API – Unified model provider with access to multiple AI models
- Vision models – Autonomous visual evaluation and guidance
- Open-source LLMs – Code generation
- Playwright – Browser automation and screenshots
- Aider – Autonomous iteration with custom Playwright integration
- Conda – Project-specific isolated environments
- Cursor IDE – Project development (.cursor/rules)
- Rich – Terminal formatting and UI capabilities (colors, progress bars, tables, etc.) with standardized styling per docs/ui-guidelines.md

## Setup

```bash
git clone https://github.com/dage/vibe-coding-iterator.git
cd vibe-coding-iterator
./setup.sh
```

The setup script handles environment setup including project name input, conda environment creation, dependency installation, and OpenRouter API configuration and doing some simple integration tests to make sure everything is 100% ready and working for the vibe coding session.


## Architecture

**Autonomous Development Loop:**
1. Generate/modify code using AI models via OpenRouter
2. Generate HTML page and use Playwright to capture screenshot
3. Vision model evaluation and guidance generation based on screenshot
4. Iterate based on vision feedback using Aider in non-interactive mode
5. Continue autonomously or await developer intervention

**Core Components:**
- **Shared API layer**: Core modules used by both evaluation scripts and iteration system
- **Evaluation system**: Standalone scripts for testing model performance across different tasks
- **Iteration controller**: Autonomous loop management

## Evals and Testing

The evaluation system enables developers to test and validate AI model performance for both code generation and vision analysis across various tasks. This facilitates rapid validation of model effectiveness for specific use cases.

The system leverages OpenRouter models for both qualitative feedback and quantitative evaluations.

## Development Workflow

The system operates autonomously through vision-guided iterations. Developers can interrupt at any time for:
- Manual control takeover using Aider in interactive mode or switching to Cursor/other IDE for manual coding and git commits
- Direction changes through updated instructions before restarting the autonomous iteration loop
- Environment variable updates to change models or configuration

The system can resume autonomous iteration after manual interventions and git commits, maintaining workflow continuity.

## Tools

The `tools/` directory is available for utility scripts but is currently empty. Model configuration is handled through environment variables in the `.env` file.

## Configuration

### Model Configuration

Model configuration is stored in environment variables in the `.env` file. The setup script will prompt for OpenRouter API key and model slugs during initial setup. You can manually edit the `.env` file to change models:

### Environment Variables

Key environment variables (set in `.env` file):
- `VIBES_API_KEY` - OpenRouter API key (get from https://openrouter.ai/settings/keys)
- `VIBES_VISION_MODEL` - Vision model slug (e.g., anthropic/claude-3-haiku, openai/gpt-4o-mini)
- `VIBES_CODE_MODEL` - Code generation model slug (e.g., anthropic/claude-3-sonnet, meta-llama/llama-3.1-8b-instruct)
- `VIBES_APP_NAME` - Sanitized project name for attribution headers in OpenRouter (required)

Optional environment variables:
- `OPENROUTER_BASE_URL` - API base URL (set by setup; default `https://openrouter.ai/api/v1`)

## Disclaimer

This project is not affiliated with OpenRouter. OpenRouter was chosen for its unified API access to multiple AI model providers and competitive pricing for open source models.