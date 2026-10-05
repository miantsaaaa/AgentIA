from datetime import UTC, datetime
from uuid import uuid4

from app.core.database import Base
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class WorkspaceChange(Base):
    __tablename__ = "workspace_changes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    relative_path: Mapped[str] = mapped_column(String(1000))
    expected_hash: Mapped[str] = mapped_column(String(64))
    proposed_content: Mapped[str] = mapped_column(Text)
    unified_diff: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), index=True, default="PENDING")
    requester: Mapped[str] = mapped_column(String(160))
    decision_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    applied_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "relative_path": self.relative_path,
            "expected_hash": self.expected_hash,
            "proposed_content": self.proposed_content,
            "unified_diff": self.unified_diff,
            "status": self.status,
            "requester": self.requester,
            "decision_note": self.decision_note,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "applied_hash": self.applied_hash,
            "created_at": self.created_at.isoformat(),
        }
