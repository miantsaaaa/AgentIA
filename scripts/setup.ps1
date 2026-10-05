$ErrorActionPreference = "Stop"
if (-not (Test-Path ".venv\Scripts\python.exe")) {
	python -m venv .venv
}
& .\.venv\Scripts\python.exe -m pip install -e ".[dev]"