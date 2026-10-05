.PHONY: setup dev test seed lint release-check

ifeq ($(OS),Windows_NT)
PS = powershell -NoProfile -ExecutionPolicy Bypass -File
PYTHON = .venv/Scripts/python.exe

setup:
	$(PS) scripts/setup.ps1

dev:
	$(PS) scripts/dev.ps1

test:
	$(PS) scripts/test.ps1

seed:
	$(PS) scripts/seed.ps1

lint:
	$(PS) scripts/lint.ps1

release-check:
	$(PS) scripts/release_check.ps1
else
PYTHON = .venv/bin/python

setup:
	sh scripts/setup.sh

dev:
	$(PYTHON) -m uvicorn app.main:app --app-dir backend --reload

test:
	$(PYTHON) -m pytest

seed:
	$(PYTHON) scripts/seed.py

lint:
	$(PYTHON) -m ruff check backend scripts
	$(PYTHON) scripts/check_repo_organization.py

release-check:
	$(PYTHON) scripts/release_check.py
endif