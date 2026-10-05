from datetime import UTC, datetime
from uuid import uuid4

from app.core.database import Base
from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class SystemAgent(Base):
    __tablename__ = "system_agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    role: Mapped[str] = mapped_column(String(40))
    description: Mapped[str] = mapped_column(Text)
    operating_instructions: Mapped[str] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(30), default="1.0.0")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )