#!/usr/bin/env sh
set -eu
if [ -x .venv/Scripts/python.exe ]; then
    PYTHON=.venv/Scripts/python.exe
else
    PYTHON=.venv/bin/python
fi
"$PYTHON" scripts/release_check.py