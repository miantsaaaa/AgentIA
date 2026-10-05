from app.core.database import get_db
from app.models.agent import Agent
from app.services.evaluation import evaluate_agent
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api", tags=["evaluations"])


class EvaluationRequest(BaseModel):
    benchmark_id: str


@router.post("/agents/{agent_id}/evaluations")
def run_evaluation(
    agent_id: str,
    request: EvaluationRequest,
    session: Session = Depends(get_db),
) -> dict[str, object]:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent introuvable")
    try:
        result = evaluate_agent(session, agent, request.benchmark_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {
        "id": result.id,
        "benchmark_id": result.benchmark_id,
        "score": result.score,
        "passed": result.passed,
        "details": result.details,
        "agent_level": agent.level,
        "agent_status": agent.status,
    }