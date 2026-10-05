from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MissionCreate(BaseModel):
    objective: str = Field(min_length=5, max_length=2000)
    mission_context: str = Field(default="", max_length=10000)
    agent_ids: list[str] = Field(min_length=1, max_length=10)


class MissionTransition(BaseModel):
    target_status: str = Field(min_length=1, max_length=30)


class MissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    objective: str
    mission_context: str
    agent_ids: list[str]
    status: str
    created_at: datetime