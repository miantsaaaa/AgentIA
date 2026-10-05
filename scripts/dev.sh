#!/usr/bin/env sh
set -eu
python -m uvicorn app.main:app --app-dir backend --reload