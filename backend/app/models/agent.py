from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    domain: Mapped[str] = mapped_column(String(120), index=True)
    tier: Mapped[int] = mapped_column(Integer, index=True)
    description: Mapped[str] = mapped_column(Text)
    level: Mapped[str] = mapped_column(String(2), default="N0", index=True)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT", index=True)
    version: Mapped[str] = mapped_column(String(30), default="0.1.0")
    skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    free_feasibility: Mapped[str] = mapped_column(String(20), default="MOYENNE")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "domain": self.domain,
            "tier": self.tier,
            "description": self.description,
            "level": self.level,
            "status": self.status,
            "version": self.version,
            "skills": self.skills,
            "free_feasibility": self.free_feasibility,
            "created_at": self.created_at,
        }