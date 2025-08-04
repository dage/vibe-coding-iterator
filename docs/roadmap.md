# Roadmap

**Current**: Open source models only via DeepInfra
- Developing setup process including model selection

**Research findings**:
- Anthropic/Gemini text models: Available on DeepInfra, not HuggingFace registered (breaks capability querying)
- Anthropic/Gemini vision: Requires direct API + separate API keys (architectural changes needed)

**Future phases**:
- Phase 2: Add Gemini and Anthropic for code generation. Small effort as can use same code for generating text and reuse DeepInfra API key, but needs hard-coding in the model discovery scripts since capabilities cannot be queried at HuggingFace.
- Phase 3: Add support for using vision capabilities of Anthropic and Gemini models. Will require using both the Gemini and Anthopic API and require the developers to set up separate API keys directly at those providers.