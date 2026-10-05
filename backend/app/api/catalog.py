from app.core.database import get_db
from app.models.agent import Agent
from app.models.catalog import AgentSkill, KnowledgePack, Skill
from app.schemas.catalog import KnowledgeData, KnowledgeRead, SkillData, SkillRead
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api", tags=["catalog"])


@router.get("/skills")
def list_skills(
    page: int = 1,
    page_size: int = 50,
    session: Session = Depends(get_db),
) -> dict[str, object]:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    total = session.scalar(select(func.count()).select_from(Skill)) or 0
    items = session.scalars(
        select(Skill).order_by(Skill.name).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return {"items": [SkillRead.model_validate(item) for item in items], "total": total}


@router.post("/skills", response_model=SkillRead, status_code=status.HTTP_201_CREATED)
def create_skill(request: SkillData, session: Session = Depends(get_db)) -> SkillRead:
    skill = Skill(**request.model_dump())
    session.add(skill)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=409, detail="Identifiant de skill déjà utilisé") from error
    session.refresh(skill)
    return SkillRead.model_validate(skill)


@router.get("/skills/{skill_id}", response_model=SkillRead)
def get_skill(skill_id: str, session: Session = Depends(get_db)) -> SkillRead:
    skill = session.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill introuvable")
    return SkillRead.model_validate(skill)


@router.put("/skills/{skill_id}", response_model=SkillRead)
def update_skill(
    skill_id: str,
    request: SkillData,
    session: Session = Depends(get_db),
) -> SkillRead:
    skill = session.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill introuvable")
    for key, value in request.model_dump().items():
        setattr(skill, key, value)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=409, detail="Identifiant de skill déjà utilisé") from error
    session.refresh(skill)
    return SkillRead.model_validate(skill)


@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(skill_id: str, session: Session = Depends(get_db)) -> Response:
    skill = session.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill introuvable")
    session.query(AgentSkill).filter(AgentSkill.skill_id == skill.id).delete()
    session.delete(skill)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/agents/{agent_id}/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def assign_skill(agent_id: str, skill_id: str, session: Session = Depends(get_db)) -> Response:
    agent = session.get(Agent, agent_id)
    skill = session.get(Skill, skill_id)
    if agent is None or skill is None:
        raise HTTPException(status_code=404, detail="Agent ou skill introuvable")
    assignment = session.scalar(
        select(AgentSkill).where(
            AgentSkill.agent_id == agent_id,
            AgentSkill.skill_id == skill_id,
        )
    )
    if assignment is None:
        session.add(AgentSkill(agent_id=agent_id, skill_id=skill_id))
        session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/agents/{agent_id}/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def unassign_skill(agent_id: str, skill_id: str, session: Session = Depends(get_db)) -> Response:
    assignment = session.scalar(
        select(AgentSkill).where(
            AgentSkill.agent_id == agent_id,
            AgentSkill.skill_id == skill_id,
        )
    )
    if assignment is not None:
        session.delete(assignment)
        session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/knowledge")
def list_knowledge(
    page: int = 1,
    page_size: int = 50,
    session: Session = Depends(get_db),
) -> dict[str, object]:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    total = session.scalar(select(func.count()).select_from(KnowledgePack)) or 0
    items = session.scalars(
        select(KnowledgePack)
        .order_by(KnowledgePack.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return {"items": [KnowledgeRead.model_validate(item) for item in items], "total": total}


@router.post("/knowledge", response_model=KnowledgeRead, status_code=status.HTTP_201_CREATED)
def create_knowledge(request: KnowledgeData, session: Session = Depends(get_db)) -> KnowledgeRead:
    pack = KnowledgePack(**request.model_dump())
    session.add(pack)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Identifiant de knowledge pack déjà utilisé",
        ) from error
    session.refresh(pack)
    return KnowledgeRead.model_validate(pack)


@router.get("/knowledge/{pack_id}", response_model=KnowledgeRead)
def get_knowledge(pack_id: str, session: Session = Depends(get_db)) -> KnowledgeRead:
    pack = session.get(KnowledgePack, pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Knowledge pack introuvable")
    return KnowledgeRead.model_validate(pack)


@router.put("/knowledge/{pack_id}", response_model=KnowledgeRead)
def update_knowledge(
    pack_id: str,
    request: KnowledgeData,
    session: Session = Depends(get_db),
) -> KnowledgeRead:
    pack = session.get(KnowledgePack, pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Knowledge pack introuvable")
    for key, value in request.model_dump().items():
        setattr(pack, key, value)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Identifiant de knowledge pack déjà utilisé",
        ) from error
    session.refresh(pack)
    return KnowledgeRead.model_validate(pack)


@router.delete("/knowledge/{pack_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge(pack_id: str, session: Session = Depends(get_db)) -> Response:
    pack = session.get(KnowledgePack, pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Knowledge pack introuvable")
    session.delete(pack)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)