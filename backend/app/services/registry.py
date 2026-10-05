import json
from pathlib import Path

from app.models.agent import Agent
from app.schemas.agent import AgentCreate
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

SEED_FILE = Path(__file__).resolve().parents[3] / "data" / "seed" / "agents.json"


def seed_agents(session: Session, seed_file: Path = SEED_FILE) -> int:
    records = json.loads(seed_file.read_text(encoding="utf-8"))
    existing = set(session.scalars(select(Agent.slug)).all())
    created = 0
    for record in records:
        if record["slug"] in existing:
            continue
        session.add(Agent(**record))
        existing.add(record["slug"])
        created += 1
    session.commit()
    return created


def create_agent(session: Session, agent_data: AgentCreate) -> Agent:
    agent = Agent(**agent_data.model_dump())
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


def get_agent(session: Session, agent_id: str) -> Agent | None:
    return session.get(Agent, agent_id)


def list_agents(
    session: Session,
    *,
    page: int,
    page_size: int,
    query: str | None,
    tier: int | None,
    level: str | None,
    status: str | None,
) -> tuple[list[Agent], int]:
    statement = select(Agent)
    filters = []
    if query:
        term = f"%{query.strip()}%"
        filters.append(
            or_(Agent.name.ilike(term), Agent.domain.ilike(term), Agent.slug.ilike(term))
        )
    if tier is not None:
        filters.append(Agent.tier == tier)
    if level:
        filters.append(Agent.level == level.upper())
    if status:
        filters.append(Agent.status == status.upper())
    if filters:
        statement = statement.where(*filters)
    total = session.scalar(select(func.count()).select_from(statement.subquery())) or 0
    items = list(
        session.scalars(
            statement.order_by(Agent.tier, Agent.name)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    )
    return items, total