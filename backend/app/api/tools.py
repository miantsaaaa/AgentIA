from app.core.database import get_db
from app.models.agent import Agent
from app.models.tool_access import Approval, AuditRecord
from app.permissions.manager import (
    approve_request,
    execute_tool,
    grant_tool,
    set_kill_switch,
    verify_audit_chain,
)
from app.tools.registry import tool_catalog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api", tags=["permissions-and-tools"])


class PermissionRequest(BaseModel):
    granted: bool


class ActionRequest(BaseModel):
    inputs: dict[str, object] = Field(default_factory=dict)
    approval_id: str | None = None


class KillSwitchRequest(BaseModel):
    enabled: bool


@router.get("/tools")
def list_tools() -> list[dict[str, object]]:
    return tool_catalog()


@router.put("/agents/{agent_id}/permissions/{tool_name}")
def change_permission(
    agent_id: str,
    tool_name: str,
    request: PermissionRequest,
    session: Session = Depends(get_db),
) -> dict[str, object]:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent introuvable")
    try:
        grant_tool(session, agent, tool_name, request.granted)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"agent_id": agent_id, "tool_name": tool_name, "granted": request.granted}


@router.post("/agents/{agent_id}/tools/{tool_name}/actions")
def run_tool(
    agent_id: str,
    tool_name: str,
    request: ActionRequest,
    session: Session = Depends(get_db),
) -> dict[str, object]:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent introuvable")
    try:
        result = execute_tool(session, agent, tool_name, request.inputs, request.approval_id)
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=423, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except OSError as error:
        raise HTTPException(
            status_code=400,
            detail="Lecture impossible dans le dossier autorisé",
        ) from error
    except ArithmeticError as error:
        raise HTTPException(status_code=400, detail="Calcul arithmétique invalide") from error
    return {"status": result.status, "result": result.result, "approval_id": result.approval_id}


@router.post("/approvals/{approval_id}/approve")
def approve_action(approval_id: str, session: Session = Depends(get_db)) -> dict[str, str]:
    approval = session.get(Approval, approval_id)
    if approval is None:
        raise HTTPException(status_code=404, detail="Demande d'approbation introuvable")
    if approval.status != "WAITING_APPROVAL":
        raise HTTPException(status_code=409, detail="Cette demande n'attend plus d'approbation")
    approve_request(session, approval)
    return {"approval_id": approval.id, "status": approval.status}


@router.put("/system/kill-switch")
def update_kill_switch(
    request: KillSwitchRequest,
    session: Session = Depends(get_db),
) -> dict[str, bool]:
    set_kill_switch(session, request.enabled)
    return {"enabled": request.enabled}


@router.get("/audit/verify")
def verify_audit(session: Session = Depends(get_db)) -> dict[str, object]:
    return {"valid": verify_audit_chain(session), "entries": session.query(AuditRecord).count()}