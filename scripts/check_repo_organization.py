import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = (
    "backend/app/api",
    "backend/app/core",
    "backend/app/models",
    "backend/app/models_provider",
    "backend/app/permissions",
    "backend/app/schemas",
    "backend/app/services",
    "backend/app/tools",
    "backend/tests",
    "data/seed",
    "docs",
    "migrations/versions",
    "scripts",
)


def unindexed_documents(root: Path) -> list[str]:
    docs = root / "docs"
    index_path = docs / "00_INDEX.md"
    if not index_path.is_file():
        return ["docs/00_INDEX.md absent"]
    index_text = index_path.read_text(encoding="utf-8")
    indexed = set(re.findall(r"\|\s*(\d{2}_[A-Z0-9_]+)\s*\|", index_text))
    return [
        f"Document non référencé dans 00_INDEX.md : {path.name}"
        for path in sorted(docs.glob("[0-9][0-9]_*.md"))
        if path.stem != "00_INDEX" and path.stem not in indexed
    ]


def find_problems(root: Path = ROOT) -> list[str]:
    problems = [
        f"Répertoire attendu absent : {path}"
        for path in REQUIRED_PATHS
        if not (root / path).is_dir()
    ]
    problems.extend(unindexed_documents(root))
    for required_file in ("AGENTS.md", "README.md", "docs/42_AGENT_WORKFLOW.md"):
        if not (root / required_file).is_file():
            problems.append(f"Fichier de gouvernance absent : {required_file}")
    return problems


def main() -> int:
    problems = find_problems()
    if problems:
        print("Organisation du dépôt : échec")
        print("\n".join(f"- {problem}" for problem in problems))
        return 1
    print("Organisation du dépôt : OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())