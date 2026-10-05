from app.core.database import get_db
from app.schemas.agent import AgentCreate, AgentPage, AgentRead
from app.services.registry import create_agent, get_agent, list_agents
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("", response_model=AgentPage)
def read_agents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str | None = None,
    tier: int | None = Query(None, ge=1, le=5),
    level: str | None = Query(None, pattern=r"^N[0-7]$"),
    status_filter: str | None = Query(None, alias="status"),
    session: Session = Depends(get_db),
) -> AgentPage:
    items, total = list_agents(
        session,
        page=page,
        page_size=page_size,
        query=q,
        tier=tier,
        level=level,
        status=status_filter,
    )
    return AgentPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{agent_id}", response_model=AgentRead)
def read_agent(agent_id: str, session: Session = Depends(get_db)) -> AgentRead:
    agent = get_agent(session, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent introuvable")
    return AgentRead.model_validate(agent)


@router.post("", response_model=AgentRead, status_code=status.HTTP_201_CREATED)
def add_agent(agent_data: AgentCreate, session: Session = Depends(get_db)) -> AgentRead:
    return AgentRead.model_validate(create_agent(session, agent_data))