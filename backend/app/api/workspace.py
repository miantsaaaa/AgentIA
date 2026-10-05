from app.core.database import get_db
from app.services import workspace as ws_service
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/workspace", tags=["workspace"])


class ProposeRequest(BaseModel):
    relative_path: str
    proposed_content: str
    requester: str


class DecisionRequest(BaseModel):
    decision_note: str | None = None


@router.get("/")
def list_proposals(status: str | None = None, session: Session = Depends(get_db)) -> list[dict]:
    return [c.to_dict() for c in ws_service.list_changes(session, status=status)]


@router.post("/propose")
def propose(request: ProposeRequest, session: Session = Depends(get_db)) -> dict:
    change = ws_service.propose_change(
        session, request.relative_path, request.proposed_content, request.requester
    )
    return change.to_dict()


@router.get("/{change_id}")
def get_proposal(change_id: str, session: Session = Depends(get_db)) -> dict:
    from app.models.workspace import WorkspaceChange

    change = session.get(WorkspaceChange, change_id)
    if change is None:
        raise HTTPException(status_code=404, detail="Proposition introuvable")
    return change.to_dict()


@router.post("/{change_id}/approve")
def approve(
    change_id: str,
    request: DecisionRequest = DecisionRequest(),
    session: Session = Depends(get_db),
) -> dict:
    try:
        change = ws_service.approve_change(session, change_id, request.decision_note)
    except KeyError:
        raise HTTPException(status_code=404, detail="Proposition introuvable")
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return change.to_dict()


@router.post("/{change_id}/reject")
def reject(
    change_id: str,
    request: DecisionRequest = DecisionRequest(),
    session: Session = Depends(get_db),
) -> dict:
    try:
        change = ws_service.reject_change(session, change_id, request.decision_note)
    except KeyError:
        raise HTTPException(status_code=404, detail="Proposition introuvable")
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return change.to_dict()


@router.post("/{change_id}/apply")
def apply(change_id: str, session: Session = Depends(get_db)) -> dict:
    try:
        change = ws_service.apply_change(session, change_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Proposition introuvable")
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return change.to_dict()
