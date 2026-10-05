from app.core.database import get_db
from app.models.mission import Mission
from app.schemas.mission import MissionCreate, MissionRead, MissionTransition
from app.services.missions import create_mission, transition_mission
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/missions", tags=["missions"])


@router.get("")
def list_missions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_db),
) -> dict[str, object]:
    total = session.scalar(select(func.count()).select_from(Mission)) or 0
    items = session.scalars(
        select(Mission)
        .order_by(Mission.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return {"items": [MissionRead.model_validate(item) for item in items], "total": total}


@router.post("", response_model=MissionRead, status_code=201)
def add_mission(request: MissionCreate, session: Session = Depends(get_db)) -> MissionRead:
    try:
        mission = create_mission(
            session,
            request.objective,
            request.mission_context,
            request.agent_ids,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return MissionRead.model_validate(mission)


@router.post("/{mission_id}/transitions", response_model=MissionRead)
def change_mission_status(
    mission_id: str,
    request: MissionTransition,
    session: Session = Depends(get_db),
) -> MissionRead:
    mission = session.get(Mission, mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail="Mission introuvable")
    try:
        transition_mission(session, mission, request.target_status.upper())
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return MissionRead.model_validate(mission)