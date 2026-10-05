.PHONY: setup dev test seed lint release-check

setup:
	python -m pip install -e ".[dev]"

dev:
	python -m uvicorn app.main:app --app-dir backend --reload

test:
	python -m pytest

seed:
	python scripts/seed.py

lint:
	python -m ruff check backend

release-check:
	python scripts/release_check.py