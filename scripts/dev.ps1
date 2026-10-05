$ErrorActionPreference = "Stop"
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload