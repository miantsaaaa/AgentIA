import difflib
import hashlib
import os
import threading
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workspace import WorkspaceChange

_file_locks: dict[str, threading.Lock] = {}
_file_locks_mutex = threading.Lock()


def _get_file_lock(path: str) -> threading.Lock:
    with _file_locks_mutex:
        if path not in _file_locks:
            _file_locks[path] = threading.Lock()
        return _file_locks[path]


class HashMismatchError(ValueError):
    """Levée quand le hash du fichier sur disque ne correspond plus à expected_hash."""


# The workspace root: NEVER computed from CWD. Always use __file__ or env var.
def _workspace_root() -> Path:
    env = os.getenv("AGENTIA_WORKSPACE_ROOT")
    if env:
        return Path(env).resolve()
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Impossible de localiser la racine du workspace (pyproject.toml introuvable)")


def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def propose_change(
    session: Session,
    relative_path: str,
    proposed_content: str,
    requester: str,
) -> WorkspaceChange:
    abs_path = _workspace_root() / relative_path
    current_content = abs_path.read_text(encoding="utf-8") if abs_path.exists() else ""
    expected_hash = _sha256(current_content)
    diff_lines = list(
        difflib.unified_diff(
            current_content.splitlines(keepends=True),
            proposed_content.splitlines(keepends=True),
            fromfile=f"a/{relative_path}",
            tofile=f"b/{relative_path}",
        )
    )
    unified_diff = "".join(diff_lines)
    change = WorkspaceChange(
        relative_path=relative_path,
        expected_hash=expected_hash,
        proposed_content=proposed_content,
        unified_diff=unified_diff,
        status="PENDING",
        requester=requester,
    )
    session.add(change)
    session.commit()
    session.refresh(change)
    return change


def approve_change(
    session: Session,
    change_id: str,
    decision_note: str | None = None,
) -> WorkspaceChange:
    change = session.get(WorkspaceChange, change_id)
    if change is None:
        raise KeyError(f"Proposition introuvable : {change_id}")
    if change.status != "PENDING":
        raise ValueError(f"Statut invalide pour approbation : {change.status}")
    change.status = "APPROVED"
    change.approved_at = datetime.now(UTC)
    change.decision_note = decision_note
    session.commit()
    session.refresh(change)
    return change


def reject_change(
    session: Session,
    change_id: str,
    decision_note: str | None = None,
) -> WorkspaceChange:
    change = session.get(WorkspaceChange, change_id)
    if change is None:
        raise KeyError(f"Proposition introuvable : {change_id}")
    if change.status != "PENDING":
        raise ValueError(f"Statut invalide pour rejet : {change.status}")
    change.status = "REJECTED"
    change.decision_note = decision_note
    session.commit()
    session.refresh(change)
    return change


def apply_change(session: Session, change_id: str) -> WorkspaceChange:
    change = session.get(WorkspaceChange, change_id)
    if change is None:
        raise KeyError(f"Proposition introuvable : {change_id}")
    if change.status != "APPROVED":
        raise ValueError(f"Statut invalide pour application : {change.status}")
    abs_path = _workspace_root() / change.relative_path
    with _get_file_lock(str(abs_path)):
        current_content = abs_path.read_text(encoding="utf-8") if abs_path.exists() else ""
        current_hash = _sha256(current_content)
        if current_hash != change.expected_hash:
            raise HashMismatchError("Le fichier a été modifié depuis la proposition ; re-proposer")
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        abs_path.write_text(change.proposed_content, encoding="utf-8")
    change.applied_hash = _sha256(change.proposed_content)
    change.status = "APPLIED"
    session.commit()
    session.refresh(change)
    return change


def list_changes(session: Session, status: str | None = None) -> list[WorkspaceChange]:
    stmt = select(WorkspaceChange)
    if status is not None:
        stmt = stmt.where(WorkspaceChange.status == status)
    return list(session.scalars(stmt).all())
