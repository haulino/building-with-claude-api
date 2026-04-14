# Building with the Claude API

Personal implementation of exercises and projects from Anthropic's [Building with the Claude API](https://anthropic.skilljar.com/claude-with-the-anthropic-api) course.

## Course Overview

A comprehensive course covering the full spectrum of working with Anthropic models using the Claude API. Topics include:

- API setup and authentication
- Single and multi-turn conversational systems
- Prompt evaluation with automated grading
- Retrieval-augmented generation (RAG) systems
- Tool integration and custom extensions
- AI agents with parallelization and routing patterns
- Multimodal content (images and documents)
- Model Context Protocol (MCP) server development
- Computer Use automation

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Add `ANTHROPIC_API_KEY` to `.env`.

## Linting
```bash
make fmt
make lint
```

## Git Hooks

Commit hooks live in `.githooks/` and are activated via `core.hookspath`:

```bash
git config core.hookspath .githooks
```

| Hook | Enforces |
|------|----------|
| `commit-msg` | Conventional Commits format on every commit message |
| `pre-commit` | Linting (`make lint`) before each commit |

New clones must run the config command above to activate the hooks — they are not enabled automatically.

## Project Structure

```
building-with-claude-api/
├── accessing-claude-with-the-api/    # API fundamentals
├── conversations/                    # Multi-turn conversation systems
├── prompt-evaluation/                # Automated grading workflows
├── rag/                              # Retrieval-augmented generation
├── tools/                            # Tool integration exercises
├── agents/                           # Agentic patterns
├── multimodal/                       # Images and documents
├── mcp/                              # MCP server development
└── computer-use/                     # Computer Use automation
```

## Key Concepts

### Five-Step Request Flow
1. Client request to your server
2. Server request to Anthropic API (SDK + API key + model + messages + max_tokens)
3. Model processing (tokenization → embedding → contextualization → generation)
4. Response to your server (message + usage + stop_reason)
5. Response to client

## Releases

Releases are automated with [release-please](https://github.com/googleapis/release-please). Commit messages must follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[(<scope>)][!]: <description>

Examples:
  feat: add streaming support
  fix(auth): handle token expiry
  feat!: redesign API  ← triggers a major version bump
```

Merging a PR to `main` updates the release PR. Merging the release PR publishes the CHANGELOG, bumps the version in `pyproject.toml`, and creates a GitHub Release.

## License
MIT
