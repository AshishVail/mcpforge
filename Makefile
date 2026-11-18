.PHONY: install test lint typecheck format check

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

lint:
	python -m ruff check .

typecheck:
	python -m mypy src

format:
	python -m ruff format .

check: lint typecheck test
