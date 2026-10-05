from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AgentCreate(BaseModel):
    slug: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    name: str = Field(min_length=1, max_length=160)
    domain: str = Field(min_length=1, max_length=120)
    tier: int = Field(ge=1, le=5)
    description: str
    skills: list[str] = Field(default_factory=list)
    free_feasibility: str = "MOYENNE"


class AgentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    slug: str
    name: str
    domain: str
    tier: int
    description: str
    level: str
    status: str
    version: str
    skills: list[str]
    free_feasibility: str
    created_at: datetime


class AgentPage(BaseModel):
    items: list[AgentRead]
    total: int
    page: int
    page_size: int