from app.core.database import get_db
from app.models.agent import Agent
from app.models.catalog import AgentKnowledge, KnowledgePack, KnowledgeProposal, KnowledgeRevision
from app.models_provider.ollama import ModelProviderError
from app.schemas.catalog import (
    KnowledgeApprovalRequest,
    KnowledgeEvaluationRequest,
    KnowledgeProposalCreate,
    KnowledgeProposalRead,
    KnowledgeRead,
)
from app.services.knowledge import (
    approve_knowledge_proposal,
    assign_knowledge,
    evaluate_knowledge_proposal,
    knowledge_context_for_agent,
    propose_knowledge,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api", tags=["knowledge-workflow"])


class RejectionRequest(BaseModel):
    reason: str = Field(min_length=5, max_length=2000)


@router.post(
    "/knowledge/{pack_id}/proposals",
    response_model=KnowledgeProposalRead,
    status_code=status.HTTP_201_CREATED,
)
def create_proposal(
    pack_id: str,
    request: KnowledgeProposalCreate,
    session: Session = Depends(get_db),
) -> KnowledgeProposalRead:
    pack = session.get(KnowledgePack, pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Knowledge pack introuvable")
    proposal = propose_knowledge(
        session,
        pack,
        content=request.proposed_content,
        source=request.source,
        source_license=request.source_license,
        reliability=request.reliability,
        change_reason=request.change_reason,
        proposed_by=request.proposed_by,
        minimum_score=request.minimum_score,
    )
    return KnowledgeProposalRead.model_validate(proposal)


@router.get("/knowledge-proposals", response_model=list[KnowledgeProposalRead])
def list_proposals(
    proposal_status: str | None = Query(None, alias="status"),
    session: Session = Depends(get_db),
) -> list[KnowledgeProposalRead]:
    query = select(KnowledgeProposal).order_by(KnowledgeProposal.created_at.desc())
    if proposal_status:
        query = query.where(KnowledgeProposal.status == proposal_status.upper())
    return [KnowledgeProposalRead.model_validate(item) for item in session.scalars(query)]


@router.post("/knowledge-proposals/{proposal_id}/evaluate", response_model=KnowledgeProposalRead)
def evaluate_proposal(
    proposal_id: str,
    request: KnowledgeEvaluationRequest,
    session: Session = Depends(get_db),
) -> KnowledgeProposalRead:
    proposal = session.get(KnowledgeProposal, proposal_id)
    agent = session.get(Agent, request.agent_id)
    if proposal is None or agent is None:
        raise HTTPException(status_code=404, detail="Proposition ou agent introuvable")
    try:
        evaluated = evaluate_knowledge_proposal(
            session,
            proposal,
            agent,
            request.scenario,
            request.required_terms,
        )
    except ModelProviderError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return KnowledgeProposalRead.model_validate(evaluated)


@router.post("/knowledge-proposals/{proposal_id}/approve", response_model=KnowledgeRead)
def approve_proposal(
    proposal_id: str,
    request: KnowledgeApprovalRequest,
    session: Session = Depends(get_db),
) -> KnowledgeRead:
    proposal = session.get(KnowledgeProposal, proposal_id)
    if proposal is None:
        raise HTTPException(status_code=404, detail="Proposition introuvable")
    try:
        pack = approve_knowledge_proposal(session, proposal)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return KnowledgeRead.model_validate(pack)


@router.post("/knowledge-proposals/{proposal_id}/reject", response_model=KnowledgeProposalRead)
def reject_proposal(
    proposal_id: str,
    request: RejectionRequest,
    session: Session = Depends(get_db),
) -> KnowledgeProposalRead:
    proposal = session.get(KnowledgeProposal, proposal_id)
    if proposal is None:
        raise HTTPException(status_code=404, detail="Proposition introuvable")
    if proposal.status not in {"PENDING_REVIEW", "EVALUATED"}:
        raise HTTPException(status_code=409, detail="Cette proposition est déjà close")
    details = dict(proposal.evaluation_details or {})
    details["rejection_reason"] = request.reason
    proposal.evaluation_details = details
    proposal.status = "REJECTED"
    session.commit()
    session.refresh(proposal)
    return KnowledgeProposalRead.model_validate(proposal)


@router.put("/agents/{agent_id}/knowledge/{pack_id}", status_code=status.HTTP_204_NO_CONTENT)
def assign_pack(agent_id: str, pack_id: str, session: Session = Depends(get_db)) -> None:
    agent = session.get(Agent, agent_id)
    pack = session.get(KnowledgePack, pack_id)
    if agent is None or pack is None:
        raise HTTPException(status_code=404, detail="Agent ou knowledge pack introuvable")
    assign_knowledge(session, agent, pack)


@router.delete("/agents/{agent_id}/knowledge/{pack_id}", status_code=status.HTTP_204_NO_CONTENT)
def unassign_pack(agent_id: str, pack_id: str, session: Session = Depends(get_db)) -> None:
    assignment = session.scalar(
        select(AgentKnowledge).where(
            AgentKnowledge.agent_id == agent_id,
            AgentKnowledge.knowledge_pack_id == pack_id,
        )
    )
    if assignment is not None:
        session.delete(assignment)
        session.commit()


@router.get("/agents/{agent_id}/knowledge")
def list_agent_knowledge(agent_id: str, session: Session = Depends(get_db)) -> dict[str, object]:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent introuvable")
    return {"agent_id": agent_id, "context": knowledge_context_for_agent(session, agent_id)}


@router.get("/knowledge/{pack_id}/revisions")
def list_revisions(pack_id: str, session: Session = Depends(get_db)) -> list[dict[str, object]]:
    if session.get(KnowledgePack, pack_id) is None:
        raise HTTPException(status_code=404, detail="Knowledge pack introuvable")
    revisions = session.scalars(
        select(KnowledgeRevision)
        .where(KnowledgeRevision.knowledge_pack_id == pack_id)
        .order_by(KnowledgeRevision.created_at.desc())
    ).all()
    return [
        {
            "id": item.id,
            "version": item.version,
            "content": item.content,
            "source": item.source,
            "source_license": item.source_license,
            "reliability": item.reliability,
            "change_reason": item.change_reason,
            "created_at": item.created_at,
        }
        for item in revisions
    ]