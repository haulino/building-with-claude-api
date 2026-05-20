# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Setup
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# Lint and format
make lint        # ruff check .
make fmt         # ruff format .

# Tests
pytest tests/                        # all tests
pytest tests/test_api_request.py     # single file
pytest tests/test_api_request.py::test_api_request_returns_text  # single test

# Git hooks (required after clone)
git config core.hookspath .githooks
```

## Architecture

Each top-level directory is a course module from Anthropic's "Building with the Claude API" Skilljar course. Modules contain standalone Python scripts (not packages) that demonstrate specific API patterns.

Tests live in `tests/` and import source modules via `sys.path` manipulation in `conftest.py` — there's no installed package. When adding tests for a new module directory, add its path to `conftest.py`.

All scripts use `python-dotenv` to load `ANTHROPIC_API_KEY` from `.env`.

## Conventions

- **Pre-commit:** Hook runs `ruff check` then `ruff format` automatically — long lines get fixed on commit.
- **Commits:** Conventional Commits format enforced by `.githooks/commit-msg` and CI. Types: feat, fix, chore, docs, test, refactor, style, perf, ci, build, revert.
- **Linting:** Ruff with E/F/W rules, 88-char line length. Run `make lint` and `make fmt` before every commit (the pre-commit hook enforces this).
- **Releases:** Automated via release-please. Version tracked in `pyproject.toml`.
- **Model:** Scripts use `claude-sonnet-4-0` as the default model.

## Testing Patterns

- Mock `client.messages.stream()` with a MagicMock that has `__enter__`/`__exit__` and `text_stream = iter([...])`.
- Keep imports under 88 chars — use multi-line style when importing 3+ names from a module.
