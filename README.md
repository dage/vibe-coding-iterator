# Vibe Coding Iterator

AI-driven development system for graphical web applications using autonomous vision-guided iteration loops and open source models.

## Project Description

Vibe Coding Iterator extends traditional vibe coding by introducing autonomous vision-guided iteration after an initial single-shot implementation. The system targets graphical intensive web applications including special effects and games.

Key differentiators:

1. **Vision-guided iteration**: Vision models evaluate visual output and guide autonomous improvements, removing humans from the feedback loop. Focus on single image analysis with animation analysis as ongoing experimental feature.
2. **Open source model focus**: Leverages cost-effective open source models instead of expensive proprietary frontier models.
3. **Unified model provider**: Single API provider (DeepInfra) and required API key enables assumptions about specific models availability and provides opportunities to use AI models as replacements for traditional software logic throughout the system. It also simplifies the whole process by sharing an API credits pool across the project and getting invoices from a single provider.
4. **Future Proof**: This system is meant to take over where the code generation models stop after single-shotting, to get that extra performance beyond what the model can do on itself, so as the models keep improving, this system is meant to raise the ceiling in terms what can be achieved by vibe coding.

The system can run autonomously for extended periods while allowing developer interruption for guidance changes, manual coding takeover, context management or switching models.

**See [docs/roadmap.md](docs/roadmap.md) for current limitations and future development phases.**

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
│       ├── project.mdc
│       ├── python.mdc
│       └── shell.mdc
├── .env                     # Environment variables (created by future setup steps)
├── .gitignore
├── README.md
├── setup.sh                 # Main setup script
├── requirements.txt
├── tools/                   # Utility scripts for manual tasks
│   ├── deepctl-setup.sh     # deepctl installation and version checking utilities (Mac only)
│   └── select-models.sh     # Model selection and configuration tool
├── docs/                    # Project documentation
│   ├── roadmap.md           # Development roadmap and limitations
│   └── ui-guidelines.md     # Terminal UI standards for Rich library usage
├── src/                     # All main Python source cod modules for
├── evals/                   # Model evaluation and testing scripts
└── <project-name>/          # Sanitized user given project name
```

## Tech Stack

- DeepInfra API – Unified model provider
- Vision models – Autonomous visual evaluation and guidance
- Open-source LLMs – Code generation
- Playwright – Browser automation and screenshots
- Aider – Autonomous iteration with custom Playwright integration
- Conda – Project-specific isolated environments
- Cursor IDE – Project development (.cursor/rules)
- deepctl – Command line tool for DeepInfra (Mac only, will be automatically installed during setup if not present and user gives permission)
- Rich – Terminal formatting and UI capabilities (colors, progress bars, tables, etc.) with standardized styling per docs/ui-guidelines.md

## Setup

```bash
git clone https://github.com/dage/vibe-coding-iterator.git
cd vibe-coding-iterator
./setup.sh
```

The setup script handles environment setup including project name input, conda environment creation, dependency installation, API key configuration, and optional model configuration. It performs integration tests to verify everything works before you start vibe coding.


## Architecture

**Autonomous Development Loop:**
1. Generate/modify code using open source models via DeepInfra
2. Generate HTML page and use Playwright to capture screenshot
3. Vision model evaluation and guidance generation based on screenshot
4. Iterate based on vision feedback using Aider in non-interactive mode
5. Continue autonomously or await developer intervention

**Core Components:**
- **Shared API layer**: Core modules used by both evaluation scripts and iteration system
- **Evaluation system**: Standalone scripts for testing model performance across different tasks
- **Iteration controller**: Autonomous loop management

## Evals and Testing

The evaluation system enables developers to compare different DeepInfra models for both code generation and vision analysis across various tasks. This facilitates rapid selection of optimal models for specific use cases.

The system leverages DeepInfra models for both qualitative feedback and quantitative evaluations.

## Development Workflow

The system operates autonomously through vision-guided iterations. Developers can interrupt at any time for:
- Manual control takeover using Aider in interactive mode or switching to Cursor/other IDE for manual coding and git commits
- Direction changes through updated instructions before restarting the autonomous iteration loop
- Model selection adjustments and configuration changes

The system can resume autonomous iteration after manual interventions and git commits, maintaining workflow continuity.

## Tools

The `tools/` directory contains utility scripts for manual tasks:

- **`deepctl-setup.sh`**: Install and configure deepctl CLI tool for DeepInfra (Mac only)
- **`select-models.sh`**: Interactive model selection tool for configuring vision and code generation models. Consolidates DeepInfra information and HuggingFace model cards.

## Configuration

### Model Configuration

Model configuration is stored in `config/models.json` with model IDs and token costs. The setup script will prompt for model selection, or run manually:

```bash
./tools/select-models.sh
```

### Environment Variables

Key environment variables (among others in the configuration):
- `VIBES_API_KEY` - DeepInfra API key
- `VIBES_VISION_MODEL` - Default vision model identifier
- `VIBES_CODE_MODEL` - Default code generation model identifier
- `VIBES_MAX_ITERATIONS` - Maximum autonomous iterations

## Disclaimer

This project is not affiliated with DeepInfra. DeepInfra was chosen partly because the developer had some unused API credits there and partly because it had some interesting open models made available. It might be replaced by OpenRouter in the near future.