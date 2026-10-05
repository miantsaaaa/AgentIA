from app.models.agent import Agent
from app.models.mission import Mission, MissionEvent
from sqlalchemy import select
from sqlalchemy.orm import Session

MISSION_TRANSITIONS = {
    "CREATED": {"PLANNED", "CANCELLED"},
    "PLANNED": {"RUNNING", "CANCELLED"},
    "RUNNING": {"WAITING_APPROVAL", "PAUSED", "FAILED", "COMPLETED", "CANCELLED"},
    "WAITING_APPROVAL": {"RUNNING", "CANCELLED"},
    "PAUSED": {"RUNNING", "CANCELLED"},
    "FAILED": {"PLANNED", "CANCELLED"},
    "COMPLETED": set(),
    "CANCELLED": set(),
}


def create_mission(
    session: Session,
    objective: str,
    mission_context: str,
    agent_ids: list[str],
) -> Mission:
    unique_ids = list(dict.fromkeys(agent_ids))
    agents = session.scalars(select(Agent).where(Agent.id.in_(unique_ids))).all()
    if len(agents) != len(unique_ids):
        raise ValueError("Un ou plusieurs agents sont introuvables")
    mission = Mission(
        objective=objective,
        mission_context=mission_context,
        agent_ids=unique_ids,
        status="CREATED",
    )
    session.add(mission)
    session.flush()
    session.add(MissionEvent(mission_id=mission.id, previous_status=None, current_status="CREATED"))
    session.commit()
    session.refresh(mission)
    return mission


def transition_mission(session: Session, mission: Mission, target_status: str) -> None:
    if target_status not in MISSION_TRANSITIONS[mission.status]:
        raise ValueError(f"Transition de mission interdite : {mission.status} vers {target_status}")
    previous_status = mission.status
    mission.status = target_status
    session.add(
        MissionEvent(
            mission_id=mission.id,
            previous_status=previous_status,
            current_status=target_status,
        )
    )
    session.commit()