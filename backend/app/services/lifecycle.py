from app.models.agent import Agent
from app.models.evaluation import ActivityEvent
from sqlalchemy.orm import Session

ALLOWED_TRANSITIONS = {
    "DRAFT": {"TRAINING"},
    "TRAINING": {"DRAFT", "EVALUATION"},
    "EVALUATION": {"TRAINING"},
    "CERTIFIED": {"AVAILABLE"},
    "AVAILABLE": {"PRODUCTION", "TRAINING"},
    "PRODUCTION": {"IMPROVEMENT"},
    "IMPROVEMENT": {"TRAINING"},
}


def transition_agent(session: Session, agent: Agent, target: str) -> None:
    if target not in ALLOWED_TRANSITIONS.get(agent.status, set()):
        raise ValueError(f"Transition interdite : {agent.status} vers {target}")
    previous = agent.status
    agent.status = target
    session.add(
        ActivityEvent(
            agent_id=agent.id,
            event_type="AGENT_STATUS_CHANGED",
            details={"from": previous, "to": target},
        )
    )
    session.commit()