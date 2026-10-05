from datetime import UTC, datetime
from re import fullmatch

from app.models.agent import Agent
from app.models.catalog import AgentKnowledge, KnowledgePack, KnowledgeProposal, KnowledgeRevision
from app.models.evaluation import ActivityEvent
from app.permissions.manager import append_audit
from app.services.runtime import run_agent
from sqlalchemy import select
from sqlalchemy.orm import Session


def propose_knowledge(
    session: Session,
    pack: KnowledgePack,
    *,
    content: str,
    source: str,
    source_license: str,
    reliability: float,
    change_reason: str,
    proposed_by: str,
    minimum_score: float,
) -> KnowledgeProposal:
    proposal = KnowledgeProposal(
        knowledge_pack_id=pack.id,
        base_version=pack.version,
        proposed_content=content,
        source=source,
        source_license=source_license,
        reliability=reliability,
        change_reason=change_reason,
        proposed_by=proposed_by,
        minimum_score=minimum_score,
        status="PENDING_REVIEW",
    )
    session.add(proposal)
    session.add(
        ActivityEvent(
            agent_id=None,
            event_type="KNOWLEDGE_PROPOSED",
            details={"pack_id": pack.id, "proposed_by": proposed_by},
        )
    )
    session.commit()
    session.refresh(proposal)
    return proposal


def evaluate_knowledge_proposal(
    session: Session,
    proposal: KnowledgeProposal,
    agent: Agent,
    scenario: str,
    required_terms: list[str],
) -> KnowledgeProposal:
    if proposal.status not in {"PENDING_REVIEW", "EVALUATED"}:
        raise ValueError("Cette proposition ne peut plus être évaluée")
    pack = session.get(KnowledgePack, proposal.knowledge_pack_id)
    if pack is None:
        raise ValueError("Knowledge pack introuvable")
    assigned_packs = session.scalars(
        select(KnowledgePack)
        .join(AgentKnowledge, AgentKnowledge.knowledge_pack_id == KnowledgePack.id)
        .where(AgentKnowledge.agent_id == agent.id)
        .order_by(KnowledgePack.name)
    ).all()
    existing_context = "\n\n".join(item.content for item in assigned_packs if item.id != pack.id)
    candidate_context = (
        f"{existing_context}\n\n" if existing_context else ""
    ) + f"PROPOSITION CANDIDATE (non approuvée) : {pack.name}\n{proposal.proposed_content}"
    generation = run_agent(
        agent,
        scenario,
        knowledge_context=candidate_context,
        knowledge_status="CANDIDATE",
    )
    normalized_response = generation.text.casefold()
    matched_terms = [term for term in required_terms if term.casefold() in normalized_response]
    score = len(matched_terms) / len(required_terms)
    proposal.evaluation_score = score
    proposal.evaluation_details = {
        "model": generation.model,
        "provider": generation.provider,
        "scenario": scenario,
        "required_terms": required_terms,
        "matched_terms": matched_terms,
        "missing_terms": [term for term in required_terms if term not in matched_terms],
        "generated_response": generation.text,
    }
    proposal.evaluated_at = datetime.now(UTC)
    proposal.status = "EVALUATED"
    session.add(
        ActivityEvent(
            agent_id=agent.id,
            event_type="KNOWLEDGE_EVALUATED",
            details={"proposal_id": proposal.id, "score": score, "model": generation.model},
        )
    )
    session.commit()
    session.refresh(proposal)
    return proposal


def assign_knowledge(session: Session, agent: Agent, pack: KnowledgePack) -> None:
    existing = session.scalar(
        select(AgentKnowledge).where(
            AgentKnowledge.agent_id == agent.id,
            AgentKnowledge.knowledge_pack_id == pack.id,
        )
    )
    if existing is None:
        session.add(AgentKnowledge(agent_id=agent.id, knowledge_pack_id=pack.id))
        session.commit()


def knowledge_context_for_agent(session: Session, agent_id: str) -> str:
    packs = session.scalars(
        select(KnowledgePack)
        .join(AgentKnowledge, AgentKnowledge.knowledge_pack_id == KnowledgePack.id)
        .where(AgentKnowledge.agent_id == agent_id)
        .order_by(KnowledgePack.name)
        .limit(20)
    ).all()
    context = "\n\n".join(f"{pack.name} (v{pack.version}):\n{pack.content}" for pack in packs)
    return context[:20000]


def approve_knowledge_proposal(
    session: Session,
    proposal: KnowledgeProposal,
) -> KnowledgePack:
    if proposal.status != "EVALUATED" or proposal.evaluation_score is None:
        raise ValueError("La proposition doit être évaluée par le modèle avant approbation")
    if proposal.evaluation_score < proposal.minimum_score:
        raise ValueError("Le score de la proposition est inférieur au seuil exigé")
    pack = session.get(KnowledgePack, proposal.knowledge_pack_id)
    if pack is None:
        raise ValueError("Knowledge pack introuvable")
    if proposal.base_version != pack.version:
        raise ValueError("Cette proposition cible une version obsolète ; elle doit être réévaluée")
    if not fullmatch(r"\d+\.\d+\.\d+", pack.version):
        raise ValueError("Version du knowledge pack invalide ; SemVer X.Y.Z est exigé")

    session.add(
        KnowledgeRevision(
            knowledge_pack_id=pack.id,
            version=pack.version,
            content=pack.content,
            source=pack.source,
            source_license=pack.source_license,
            reliability=pack.reliability,
            change_reason=proposal.change_reason,
        )
    )
    major, minor, patch = (int(part) for part in pack.version.split("."))
    pack.content = proposal.proposed_content
    pack.source = proposal.source
    pack.source_license = proposal.source_license
    pack.reliability = proposal.reliability
    pack.version = f"{major}.{minor}.{patch + 1}"
    pack.last_verified = datetime.now(UTC)
    proposal.status = "APPROVED"
    append_audit(
        session,
        None,
        "knowledge:approve",
        "MEDIUM_RISK",
        "APPROVED",
        {"proposal_id": proposal.id, "pack_id": pack.id},
    )
    session.add(
        ActivityEvent(
            agent_id=None,
            event_type="KNOWLEDGE_PROMOTED",
            details={"proposal_id": proposal.id, "pack_id": pack.id, "version": pack.version},
        )
    )
    session.commit()
    session.refresh(pack)
    return pack