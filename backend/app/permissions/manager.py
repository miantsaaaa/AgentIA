import hashlib
import json
from dataclasses import dataclass
from typing import Any

from app.models.agent import Agent
from app.models.tool_access import AgentPermission, Approval, AuditRecord, RuntimeSetting
from app.tools.registry import TOOLS
from app.tools.safe_tools import TOOL_RUNNERS
from sqlalchemy import select
from sqlalchemy.orm import Session

GENESIS_HASH = "0" * 64


@dataclass(frozen=True)
class ActionResult:
    status: str
    result: dict[str, Any] | None = None
    approval_id: str | None = None


def append_audit(
    session: Session,
    agent_id: str | None,
    action: str,
    risk: str,
    outcome: str,
    details: dict[str, Any],
) -> None:
    previous = session.scalar(select(AuditRecord).order_by(AuditRecord.sequence.desc()).limit(1))
    previous_hash = previous.entry_hash if previous else GENESIS_HASH
    payload = {
        "agent_id": agent_id,
        "action": action,
        "risk": risk,
        "outcome": outcome,
        "details": details,
    }
    entry_hash = hashlib.sha256(
        previous_hash.encode() + json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    session.add(
        AuditRecord(
            agent_id=agent_id,
            action=action,
            risk=risk,
            outcome=outcome,
            details=details,
            previous_hash=previous_hash,
            entry_hash=entry_hash,
        )
    )


def verify_audit_chain(session: Session) -> bool:
    previous_hash = GENESIS_HASH
    records = session.scalars(select(AuditRecord).order_by(AuditRecord.sequence)).all()
    for record in records:
        payload = {
            "agent_id": record.agent_id,
            "action": record.action,
            "risk": record.risk,
            "outcome": record.outcome,
            "details": record.details,
        }
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        expected = hashlib.sha256(previous_hash.encode() + serialized).hexdigest()
        if record.previous_hash != previous_hash or record.entry_hash != expected:
            return False
        previous_hash = record.entry_hash
    return True


def grant_tool(session: Session, agent: Agent, tool_name: str, granted: bool) -> None:
    if tool_name not in TOOLS:
        raise ValueError("Outil inconnu")
    permission = session.scalar(
        select(AgentPermission).where(
            AgentPermission.agent_id == agent.id,
            AgentPermission.tool_name == tool_name,
        )
    )
    if permission is None:
        permission = AgentPermission(agent_id=agent.id, tool_name=tool_name, granted=granted)
        session.add(permission)
    else:
        permission.granted = granted
    append_audit(
        session,
        agent.id,
        f"permission:{tool_name}",
        "LOW_RISK",
        "GRANTED" if granted else "REVOKED",
        {},
    )
    session.commit()


def set_kill_switch(session: Session, enabled: bool) -> None:
    setting = session.get(RuntimeSetting, "kill_switch")
    if setting is None:
        setting = RuntimeSetting(key="kill_switch", value=str(enabled).lower())
        session.add(setting)
    else:
        setting.value = str(enabled).lower()
    outcome = "ENABLED" if enabled else "DISABLED"
    append_audit(session, None, "kill_switch", "HIGH_RISK", outcome, {})
    session.commit()


def execute_tool(
    session: Session,
    agent: Agent,
    tool_name: str,
    inputs: dict[str, Any],
    approval_id: str | None = None,
) -> ActionResult:
    tool = TOOLS.get(tool_name)
    if tool is None:
        raise ValueError("Outil inconnu")
    setting = session.get(RuntimeSetting, "kill_switch")
    if setting is not None and setting.value == "true":
        append_audit(session, agent.id, tool_name, tool.risk, "KILL_SWITCHED", {})
        session.commit()
        raise RuntimeError("Le kill switch global est activé")

    permission = session.scalar(
        select(AgentPermission).where(
            AgentPermission.agent_id == agent.id,
            AgentPermission.tool_name == tool_name,
        )
    )
    if permission is None or not permission.granted:
        append_audit(session, agent.id, tool_name, tool.risk, "DENIED", {})
        session.commit()
        raise PermissionError("Permission explicite requise")

    if tool.requires_approval:
        approval = session.get(Approval, approval_id) if approval_id else None
        if approval_id and (
            approval is None or approval.agent_id != agent.id or approval.tool_name != tool_name
        ):
            append_audit(
                session,
                agent.id,
                tool_name,
                tool.risk,
                "DENIED",
                {"reason": "approval_mismatch"},
            )
            session.commit()
            raise PermissionError("Approbation invalide pour cette action")
        if approval is not None and approval.status == "APPROVED":
            if approval.inputs != inputs:
                append_audit(
                    session,
                    agent.id,
                    tool_name,
                    tool.risk,
                    "DENIED",
                    {"reason": "inputs_changed"},
                )
                session.commit()
                raise PermissionError("Les entrées diffèrent de celles approuvées")
            approval.status = "CONSUMED"
        elif approval is not None and approval.status == "WAITING_APPROVAL":
            append_audit(session, agent.id, tool_name, tool.risk, "WAITING_APPROVAL", {})
            session.commit()
            return ActionResult("WAITING_APPROVAL", approval_id=approval.id)
        else:
            approval = Approval(agent_id=agent.id, tool_name=tool_name, inputs=inputs)
            session.add(approval)
            append_audit(session, agent.id, tool_name, tool.risk, "WAITING_APPROVAL", {})
            session.commit()
            session.refresh(approval)
            return ActionResult("WAITING_APPROVAL", approval_id=approval.id)
        approval.status = "CONSUMED"

    result = TOOL_RUNNERS[tool_name](inputs)
    append_audit(
        session,
        agent.id,
        tool_name,
        tool.risk,
        "EXECUTED",
        {"result_keys": sorted(result)},
    )
    session.commit()
    return ActionResult("EXECUTED", result=result)


def approve_request(session: Session, approval: Approval) -> None:
    approval.status = "APPROVED"
    append_audit(
        session,
        approval.agent_id,
        f"approval:{approval.tool_name}",
        "CRITICAL",
        "APPROVED",
        {"approval_id": approval.id},
    )
    session.commit()