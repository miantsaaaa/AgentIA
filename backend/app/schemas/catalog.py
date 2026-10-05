from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SkillData(BaseModel):
    slug: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    name: str = Field(min_length=1, max_length=160)
    domain: str = Field(min_length=1, max_length=120)
    description: str
    prerequisites: list[str] = Field(default_factory=list)
    required_tools: list[str] = Field(default_factory=list)
    required_level: str = Field(default="N0", pattern=r"^N[0-7]$")
    version: str = "1.0.0"
    state: str = "AVAILABLE"


class SkillRead(SkillData):
    model_config = ConfigDict(from_attributes=True)

    id: str


class KnowledgeData(BaseModel):
    slug: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    name: str = Field(min_length=1, max_length=160)
    domain: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1)
    source: str = Field(min_length=1, max_length=500)
    source_license: str = Field(min_length=1, max_length=100)
    reliability: float = Field(ge=0, le=1)
    version: str = "1.0.0"


class KnowledgeRead(KnowledgeData):
    model_config = ConfigDict(from_attributes=True)

    id: str
    last_verified: datetime


class KnowledgeProposalCreate(BaseModel):
    proposed_content: str = Field(min_length=1, max_length=100000)
    source: str = Field(min_length=1, max_length=500)
    source_license: str = Field(min_length=1, max_length=100)
    reliability: float = Field(ge=0, le=1)
    change_reason: str = Field(min_length=5, max_length=2000)
    proposed_by: str = Field(min_length=1, max_length=160)
    minimum_score: float = Field(default=1.0, ge=0.5, le=1.0)


class KnowledgeProposalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    knowledge_pack_id: str
    base_version: str
    proposed_content: str
    source: str
    source_license: str
    reliability: float
    change_reason: str
    proposed_by: str
    minimum_score: float
    status: str
    evaluation_score: float | None
    evaluation_details: dict[str, object] | None
    evaluated_at: datetime | None
    created_at: datetime


class KnowledgeEvaluationRequest(BaseModel):
    agent_id: str
    scenario: str = Field(min_length=5, max_length=5000)
    required_terms: list[str] = Field(min_length=1, max_length=20)


class KnowledgeApprovalRequest(BaseModel):
    confirm: Literal[True]


class ToolRecordData(BaseModel):
    name: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
    description: str
    input_schema: dict[str, object] = Field(default_factory=dict)
    output_schema: dict[str, object] = Field(default_factory=dict)
    risk: Literal["READ", "LOW_RISK", "MEDIUM_RISK", "HIGH_RISK", "CRITICAL"]
    requires_approval: bool = False
    sandbox_compatible: bool = True
    rollback_supported: bool = False
    dependencies: list[str] = Field(default_factory=list)
    version: str = "1.0.0"
    license: str = "MIT"


class ToolRecordRead(ToolRecordData):
    model_config = ConfigDict(from_attributes=True)

    id: str
    executable: bool