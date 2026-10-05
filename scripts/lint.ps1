$ErrorActionPreference = "Stop"
& .\.venv\Scripts\python.exe -m ruff check backend scripts
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& .\.venv\Scripts\python.exe scripts/check_repo_organization.py