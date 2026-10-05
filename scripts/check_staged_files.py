import re
import subprocess
import sys

blocked_suffixes = {".db", ".sqlite", ".gguf", ".safetensors", ".pem", ".key"}
secret_patterns = [
    re.compile(rb"(?i)(api[_-]?key|access[_-]?token|client[_-]?secret)\s*[:=]\s*['\"]?[^\s'\"]{12,}"),
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
paths = subprocess.check_output(["git", "diff", "--cached", "--name-only", "-z"]).split(b"\0")
problems = []

for raw_path in filter(None, paths):
    path = raw_path.decode(errors="replace")
    suffix = "." + path.rsplit(".", 1)[-1].lower() if "." in path else ""
    if suffix in blocked_suffixes or path.lower().endswith(".env"):
        problems.append(f"Fichier interdit indexé : {path}")
        continue
    content = subprocess.run(
        ["git", "show", f":{path}"], capture_output=True, check=False
    ).stdout
    if len(content) > 50 * 1024 * 1024:
        problems.append(f"Fichier supérieur à 50 Mo : {path}")
    if any(pattern.search(content) for pattern in secret_patterns):
        problems.append(f"Motif de secret détecté : {path}")

if problems:
    print("\n".join(problems), file=sys.stderr)
    sys.exit(1)
print("Contrôle des fichiers indexés : OK")