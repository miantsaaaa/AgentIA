from app.core.database import get_db
from app.models.agent import Agent
from app.services.lifecycle import transition_agent
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/agents", tags=["lifecycle"])


class TransitionRequest(BaseModel):
    target_status: str = Field(min_length=1, max_length=30)


@router.post("/{agent_id}/transitions")
def change_status(
    agent_id: str,
    request: TransitionRequest,
    session: Session = Depends(get_db),
) -> dict[str, str]:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent introuvable")
    try:
        transition_agent(session, agent, request.target_status.upper())
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return {"id": agent.id, "status": agent.status}