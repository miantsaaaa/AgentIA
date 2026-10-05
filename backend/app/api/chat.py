from typing import Literal

from app.core.database import get_db
from app.models.agent import Agent
from app.models.evaluation import ActivityEvent
from app.models.system_agent import SystemAgent
from app.models_provider.ollama import ModelProviderError
from app.services.knowledge import knowledge_context_for_agent
from app.services.recommender import recommend_agents
from app.services.runtime import run_agent, run_system_agent
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    assistant_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=10000)
    history: list[ChatTurn] = Field(default_factory=list, max_length=20)


@router.post("")
def chat(request: ChatRequest, session: Session = Depends(get_db)) -> dict[str, object]:
    system_agent = session.scalar(
        select(SystemAgent).where(SystemAgent.slug == request.assistant_id)
    )
    ordinary_agent = None if system_agent else session.get(Agent, request.assistant_id)
    if system_agent is None and ordinary_agent is None:
        raise HTTPException(status_code=404, detail="Agent sélectionné introuvable")
    if system_agent is not None and not system_agent.active:
        raise HTTPException(status_code=409, detail="Cet agent système est désactivé")

    turns = [turn.model_dump() for turn in request.history]
    try:
        if system_agent is not None:
            generation = run_system_agent(system_agent, request.message, turns)
            recommendations = recommend_agents(session, request.message, limit=3)
            event_agent_id = None
            assistant_name = system_agent.name
        else:
            generation = run_agent(
                ordinary_agent,
                request.message,
                turns,
                knowledge_context_for_agent(session, ordinary_agent.id),
            )
            recommendations = None
            event_agent_id = ordinary_agent.id
            assistant_name = ordinary_agent.name
    except ModelProviderError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    session.add(
        ActivityEvent(
            agent_id=event_agent_id,
            event_type="CHAT_COMPLETED",
            details={
                "assistant_id": request.assistant_id,
                "provider": generation.provider,
                "model": generation.model,
            },
        )
    )
    session.commit()
    return {
        "assistant_id": request.assistant_id,
        "assistant_name": assistant_name,
        "provider": generation.provider,
        "model": generation.model,
        "response": generation.text,
        "recommendations": recommendations,
    }