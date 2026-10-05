from datetime import UTC, datetime
from uuid import uuid4

from app.core.database import Base
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    domain: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text)
    prerequisites: Mapped[list[str]] = mapped_column(JSON, default=list)
    required_tools: Mapped[list[str]] = mapped_column(JSON, default=list)
    required_level: Mapped[str] = mapped_column(String(2), default="N0")
    version: Mapped[str] = mapped_column(String(30), default="1.0.0")
    state: Mapped[str] = mapped_column(String(30), default="AVAILABLE")


class AgentSkill(Base):
    __tablename__ = "agent_skills"
    __table_args__ = (UniqueConstraint("agent_id", "skill_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    agent_id: Mapped[str] = mapped_column(ForeignKey("agents.id"), index=True)
    skill_id: Mapped[str] = mapped_column(ForeignKey("skills.id"), index=True)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class ToolRecord(Base):
    __tablename__ = "tool_registry"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text)
    input_schema: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    output_schema: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    risk: Mapped[str] = mapped_column(String(20))
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    sandbox_compatible: Mapped[bool] = mapped_column(Boolean, default=True)
    rollback_supported: Mapped[bool] = mapped_column(Boolean, default=False)
    dependencies: Mapped[list[str]] = mapped_column(JSON, default=list)
    version: Mapped[str] = mapped_column(String(30), default="1.0.0")
    license: Mapped[str] = mapped_column(String(100), default="MIT")
    executable: Mapped[bool] = mapped_column(Boolean, default=False)


class KnowledgePack(Base):
    __tablename__ = "knowledge_packs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    domain: Mapped[str] = mapped_column(String(120), index=True)
    content: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(500))
    source_license: Mapped[str] = mapped_column(String(100))
    reliability: Mapped[float] = mapped_column()
    version: Mapped[str] = mapped_column(String(30), default="1.0.0")
    last_verified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class AgentKnowledge(Base):
    __tablename__ = "agent_knowledge"
    __table_args__ = (UniqueConstraint("agent_id", "knowledge_pack_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    agent_id: Mapped[str] = mapped_column(ForeignKey("agents.id"), index=True)
    knowledge_pack_id: Mapped[str] = mapped_column(ForeignKey("knowledge_packs.id"), index=True)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class KnowledgeProposal(Base):
    __tablename__ = "knowledge_proposals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    knowledge_pack_id: Mapped[str] = mapped_column(ForeignKey("knowledge_packs.id"), index=True)
    base_version: Mapped[str] = mapped_column(String(30))
    proposed_content: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(500))
    source_license: Mapped[str] = mapped_column(String(100))
    reliability: Mapped[float] = mapped_column(Float)
    change_reason: Mapped[str] = mapped_column(Text)
    proposed_by: Mapped[str] = mapped_column(String(160))
    minimum_score: Mapped[float] = mapped_column(Float, default=1.0)
    status: Mapped[str] = mapped_column(String(30), default="PENDING_REVIEW", index=True)
    evaluation_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    evaluation_details: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    evaluated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class KnowledgeRevision(Base):
    __tablename__ = "knowledge_revisions"
    __table_args__ = (UniqueConstraint("knowledge_pack_id", "version"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    knowledge_pack_id: Mapped[str] = mapped_column(ForeignKey("knowledge_packs.id"), index=True)
    version: Mapped[str] = mapped_column(String(30))
    content: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(500))
    source_license: Mapped[str] = mapped_column(String(100))
    reliability: Mapped[float] = mapped_column(Float)
    change_reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )