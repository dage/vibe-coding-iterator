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

## Design Guidelines

This project prioritizes **simplicity and modularity** to maximize focus on AI model optimization and workflow experimentation rather than complex codebase maintenance:

- **No file logging**: Uses stdout only for all logging and output
- **Project isolation**: Each vibe project requires a fresh clone and setup - no cleanup functionality needed
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
├── .env                     # Environment variables (created by setup.sh)
├── .gitignore
├── README.md
├── setup.sh                 # Main setup script
├── requirements.txt
├── tools/                   # Utility scripts for manual tasks (e.g., listing DeepInfra models)
│   └── deepctl-setup.sh     # deepctl installation and version checking utilities (Mac only)
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

## Setup

```bash
git clone https://github.com/dage/vibe-coding-iterator.git
cd vibe-coding-iterator
./setup.sh
```

The setup script will:
1. Prompt for your vibe project name (which will be sanitized for directory and conda environment naming)
2. Create a project-specific conda environment with the sanitized name
3. Prompt user for DeepInfra API key
4. Create a default .env with API key and other configuration
5. Test DeepInfra model connectivity
7. Generate test files and execute a full iteration loop to ensure everything is working.


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

## Configuration

The setup script generates a `.env` file with `VIBES_` prefixed environment variables. Each time you start a vibe-coding session, that file is loaded. Edit `.env` to adjust default models, iteration limits, API keys, and other settings.

Key environment variables (among others in the configuration):
- `VIBES_API_KEY` - DeepInfra API key
- `VIBES_VISION_MODEL` - Default vision model identifier
- `VIBES_CODE_MODEL` - Default code generation model identifier
- `VIBES_MAX_ITERATIONS` - Maximum autonomous iterations

## Disclaimer

This project is not affiliated with DeepInfra. DeepInfra was chosen partly because the developer had some unused API credits there and partly because it quickly makes newly released open-source models available and offers a strong selection of models.