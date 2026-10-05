from app.core.database import get_db
from app.models.catalog import ToolRecord
from app.schemas.catalog import ToolRecordData, ToolRecordRead
from app.tools.registry import TOOLS
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/tool-registry", tags=["tool-registry"])


@router.get("")
def list_tool_records(session: Session = Depends(get_db)) -> list[ToolRecordRead]:
    records = session.scalars(select(ToolRecord).order_by(ToolRecord.name)).all()
    return [ToolRecordRead.model_validate(record) for record in records]


@router.post("", response_model=ToolRecordRead, status_code=status.HTTP_201_CREATED)
def create_tool_record(
    request: ToolRecordData,
    session: Session = Depends(get_db),
) -> ToolRecordRead:
    if request.name in TOOLS:
        raise HTTPException(status_code=409, detail="Cet outil natif est géré par son runner")
    record = ToolRecord(**request.model_dump(), executable=False)
    session.add(record)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=409, detail="Nom de tool déjà utilisé") from error
    session.refresh(record)
    return ToolRecordRead.model_validate(record)


@router.get("/{tool_id}", response_model=ToolRecordRead)
def get_tool_record(tool_id: str, session: Session = Depends(get_db)) -> ToolRecordRead:
    record = session.get(ToolRecord, tool_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Tool introuvable")
    return ToolRecordRead.model_validate(record)


@router.put("/{tool_id}", response_model=ToolRecordRead)
def update_tool_record(
    tool_id: str,
    request: ToolRecordData,
    session: Session = Depends(get_db),
) -> ToolRecordRead:
    record = session.get(ToolRecord, tool_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Tool introuvable")
    if record.executable or record.name in TOOLS or request.name in TOOLS:
        raise HTTPException(
            status_code=409,
            detail="Un tool natif exécutable ne peut pas être modifié ici",
        )
    for key, value in request.model_dump().items():
        setattr(record, key, value)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=409, detail="Nom de tool déjà utilisé") from error
    session.refresh(record)
    return ToolRecordRead.model_validate(record)


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tool_record(tool_id: str, session: Session = Depends(get_db)) -> Response:
    record = session.get(ToolRecord, tool_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Tool introuvable")
    if record.executable or record.name in TOOLS:
        raise HTTPException(
            status_code=409,
            detail="Un tool natif exécutable ne peut pas être supprimé ici",
        )
    session.delete(record)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)