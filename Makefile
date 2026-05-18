# check for lint errors (style, unused imports, etc.)
lint:
	source .venv/bin/activate && ruff check .

# format code
fmt:
	source .venv/bin/activate && ruff format .