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
│   └── rules/
│       ├── project.md              # Core engineering rules for agents/humans
│       ├── python.md               # Auto-attached rules for .py files
│       └── shell.md                # Auto-attached rules for .sh files
├── .env                            # Project config (created by setup.sh)
├── .gitignore                      # Ignores storage/ runtime artifacts
├── README.md                       # Project overview and how-to
├── requirements.txt                # Python dependencies
├── setup.sh                        # One-time env setup (creates conda env, installs deps)
├── start.sh                        # Start API+engine server (uses VIBES_APP_NAME env)
├── docs/
│   ├── ui-guidelines.md            # Terminal UI standards (Rich)
│   └── contracts/
│       ├── api.md                  # Generated API overview (from Pydantic)
│       ├── commands.schema.json    # Generated JSON Schema for commands
│       └── events.schema.json      # Generated JSON Schema for events
├── integration-tests/
│   └── test_openrouter_integration.py  # Optional OR integration checks (manual)
├── src/
│   ├── or_client.py                # OpenRouter client + Conversation helper
│   ├── adapters/
│   │   ├── http/
│   │   │   └── api.py              # FastAPI app (SSE /api/events, control, prompt, static, UI)
│   │   └── playwright/
│   │       └── browser.py          # HTML→PNG capture via Playwright (Chromium)
│   ├── contracts/
│   │   ├── commands.py             # Command models (ControlCommand, PromptCommand)
│   │   ├── events.py               # Event models (discriminated by t)
│   │   └── generate_schemas.py     # Writes docs/contracts/*.json and api.md
│   ├── engine/
│   │   ├── bus.py                  # Async pub/sub bus for events
│   │   ├── handlers.py             # Agent exchange stub + deterministic workspace patch
│   │   └── run_loop.py             # Iteration loop emitting prompt/response/screenshot events
│   ├── storage/
│   │   ├── events_log.py           # JSONL append helper for per-run events
│   │   ├── file_tree.py            # Shallow tree listing helper
│   │   └── paths.py                # Run IDs and storage paths (runs, workspace, screenshots)
│   └── tools/
│       ├── dev_server.py           # Runs API and engine concurrently
│       └── smoke.py                # One-shot smoke: SSE + screenshot existence
└── web/
    └── index.html                  # Minimal UI (screenshots, play/pause, exchange lanes)
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

## Run (dev server)

After setup, start the API + engine locally (serves the UI on http://localhost:8000/):

```bash
./start.sh
```

Notes:
- Uses the conda environment named by `VIBES_APP_NAME` from your `.env` (created by `setup.sh`).
- The UI is served at `/` (root). Static artifacts live under `/static/...`.
- SSE stream: `GET /api/events`. Control: `POST /api/control` with `{ "action": "pause" | "resume" }`.
- Prompt: `POST /api/prompt` with `{ "actor":"user", "route_to":"vision"|"code", "content":[...] }`.


## Developer helpers

### Dev shell helper

Source this to load `.env` and activate the project conda env in your current shell:

```bash
source tools/dev-env.sh
```

### Regenerate contracts

Regenerates JSON Schemas and the API doc from the Pydantic models after you change `src/contracts/*`.

```bash
python -m src.contracts.generate_schemas
```

### Quick harness (one-shot)

Starts the server briefly and runs a smoke test to confirm the UI is reachable, SSE emits, and a screenshot is created.

```bash
python -m src.tools.dev_server & SERVER=$!; sleep 3
python -m src.tools.smoke
RC=$?; kill $SERVER || true; exit $RC
```

### Optional controls check

Quick manual poke that toggling Play/Pause returns `{ok:true}` and emits control events on the SSE stream.

```bash
curl -sS -XPOST http://localhost:8000/api/control \
  -H 'Content-Type: application/json' -d '{"action":"resume"}'
curl -sS -XPOST http://localhost:8000/api/control \
  -H 'Content-Type: application/json' -d '{"action":"pause"}'
```

### Notes

- The Vision lane is intentionally empty for this iteration. The loop emits `prompt.sent` with `actor:"user"` to `to:"code"`, and `response.received` with `actor:"code"`.
- Screenshots are of a minimal HTML page; thumbnails may look blank at small size. Click to open the full PNG.
- `start.sh` reads `.env` (`VIBES_APP_NAME`) to choose the conda env and frees port 8000 if a prior dev server is running.


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
- `VIBES_VISION_MODEL` - Vision model slug (e.g., meta-llama/llama-3.2-90b-vision-instruct)
- `VIBES_CODE_MODEL` - Code generation model slug (e.g., z-ai/glm-4.5-air, meta-llama/llama-3.1-8b-instruct)
- `VIBES_APP_NAME` - Sanitized project name for attribution headers in OpenRouter (required)

Optional environment variables:
- `OPENROUTER_BASE_URL` - API base URL (set by setup; default `https://openrouter.ai/api/v1`)

## Disclaimer

This project is not affiliated with OpenRouter. OpenRouter was chosen for its unified API access to multiple AI model providers and competitive pricing for open source models.