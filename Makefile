fmt:
	source .venv/bin/activate && ruff format .

lint:
	source .venv/bin/activate && ruff check .
