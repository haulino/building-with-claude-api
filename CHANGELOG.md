# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2026-04-11

### Added
- GitHub Actions CI workflow (`ci.yml`) combining lint and test jobs
- pytest test suite for API request module (`tests/test_api_request.py`)
- `conftest.py` with shared test configuration and fixtures
- Checkout step and job-scoped environment in CI workflow

### Changed
- Pinned all dependencies to exact versions (`anthropic==0.91.0`, `python-dotenv==1.2.2`, `ruff==0.15.9`, `pytest==9.0.3`)
- Refactored API request module into named functions with snake_case conventions
- Replaced standalone `lint.yml` with unified `ci.yml` workflow, segmented into distinct lint and test jobs

### Removed
- Standalone `.github/workflows/lint.yml` (consolidated into `ci.yml`)

## [0.4.0] - 2026-04-10

### Added
- Multi-turn conversation script (`accessing-claude-with-the-api/multi-turn-conversation.py`) with sequential answer printing
- `Makefile` with `fmt` and `lint` targets for local development
- Local lint target enabling `make lint` without CI

### Changed
- Updated README with multi-turn conversation usage and Makefile instructions

## [0.3.0] - 2026-04-09

### Added
- Basic API request script (`accessing-claude-with-the-api/api-request.py`)
- `requirements.txt` with `anthropic`, `python-dotenv`, and `ruff`
- Response processing and output formatting in API request

### Changed
- Updated README with setup instructions and project structure

## [0.2.0] - 2026-04-07

### Added
- GitHub Actions lint workflow (`.github/workflows/lint.yml`) running `ruff check` on pull requests and pushes to `main`
- `pyproject.toml` with ruff linting configuration
- `.worktrees/` entry to `.gitignore`

### Changed
- Removed branch filter restriction from `pull_request` trigger in lint workflow

## [0.1.0] - 2026-04-06

### Added
- `LICENSE` (MIT)
- `README.md` with course overview, setup instructions, and five-step request flow
- `accessing-claude-with-the-api/key-takeaways.md` documenting core API concepts

[Unreleased]: https://github.com/haulino/building-with-claude-api/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/haulino/building-with-claude-api/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/haulino/building-with-claude-api/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/haulino/building-with-claude-api/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/haulino/building-with-claude-api/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/haulino/building-with-claude-api/releases/tag/v0.1.0
