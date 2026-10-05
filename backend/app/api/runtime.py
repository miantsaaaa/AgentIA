from app.core.database import get_db
from app.models.agent import Agent
from app.models.evaluation import ActivityEvent
from app.models_provider.factory import get_model_provider
from app.models_provider.ollama import ModelProviderError
from app.services.runtime import run_agent
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api", tags=["runtime"])


class RunRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=10000)


@router.get("/model/status")
def model_status() -> dict[str, object]:
    try:
        return get_model_provider().health()
    except ModelProviderError as error:
        return {"provider": "ollama", "available": False, "error": str(error)}


@router.post("/agents/{agent_id}/run")
def run_agent_route(
    agent_id: str,
    request: RunRequest,
    session: Session = Depends(get_db),
) -> dict[str, str]:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent introuvable")
    try:
        response = run_agent(agent, request.prompt)
    except ModelProviderError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    session.add(
        ActivityEvent(
            agent_id=agent.id,
            event_type="AGENT_RUN_COMPLETED",
            details={"provider": response.provider, "model": response.model},
        )
    )
    session.commit()
    return {"provider": response.provider, "model": response.model, "response": response.text}