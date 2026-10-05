import subprocess
import sys


def run(label: str, command: list[str]) -> None:
    print(f"== {label} ==", flush=True)
    subprocess.run(command, check=True)


try:
    run("Tests backend", [sys.executable, "-m", "pytest"])
    run("Lint backend", [sys.executable, "-m", "ruff", "check", "backend"])
    run("Hygiène fichiers indexés", [sys.executable, "scripts/check_staged_files.py"])
except subprocess.CalledProcessError as error:
    raise SystemExit(error.returncode) from error

print(
    "Porte locale provisoire : tests, lint et hygiène terminés. La release reste bloquée "
    "tant que le frontend et les autres contrôles ne sont pas implémentés."
)
raise SystemExit(1)