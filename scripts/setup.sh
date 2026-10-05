#!/usr/bin/env sh
set -eu
if [ -x .venv/Scripts/python.exe ]; then
	PYTHON=.venv/Scripts/python.exe
elif [ -x .venv/bin/python ]; then
	PYTHON=.venv/bin/python
else
	if command -v python3 >/dev/null 2>&1; then
		python3 -m venv .venv
	else
		python -m venv .venv
	fi
	if [ -x .venv/Scripts/python.exe ]; then
		PYTHON=.venv/Scripts/python.exe
	else
		PYTHON=.venv/bin/python
	fi
fi
"$PYTHON" -m pip install -e ".[dev]"