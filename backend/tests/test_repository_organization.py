from pathlib import Path

from scripts.check_repo_organization import (
    find_problems,
    invalid_implementation_statuses,
    unindexed_documents,
)

ROOT = Path(__file__).resolve().parents[2]


def test_repository_has_an_indexed_and_documented_structure() -> None:
    assert find_problems(ROOT) == []


def test_numbered_document_must_be_added_to_the_index(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "00_INDEX.md").write_text("# Index\n", encoding="utf-8")
    (docs / "43_NEW_RULES.md").write_text("# Règles\n", encoding="utf-8")
    assert unindexed_documents(tmp_path) == [
        "Document non référencé dans 00_INDEX.md : 43_NEW_RULES.md"
    ]


def test_implementation_ledger_rejects_undefined_status(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "43_IMPLEMENTATION_STATUS.md").write_text(
        "| Composant | Statut | Preuve | Suite |\n"
        "|---|---|---|---|\n"
        "| UI | EN COURS | - | - |\n",
        encoding="utf-8",
    )
    assert "Statut invalide" in invalid_implementation_statuses(tmp_path)[0]