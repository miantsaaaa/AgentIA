import difflib
import hashlib
import os
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workspace import WorkspaceChange


# The workspace root: NEVER computed from CWD. Always use __file__ or env var.
def _workspace_root() -> Path:
    env = os.getenv("AGENTIA_WORKSPACE_ROOT")
    if env:
        return Path(env)
    # backend/app/services/workspace.py -> go up 4 levels to reach workspace root
    return Path(__file__).resolve().parents[4]


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
    current_content = abs_path.read_text(encoding="utf-8") if abs_path.exists() else ""
    current_hash = _sha256(current_content)
    if current_hash != change.expected_hash:
        raise ValueError("Le fichier a été modifié depuis la proposition ; re-proposer")
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
