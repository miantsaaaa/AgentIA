import json
from pathlib import Path
from typing import Any

from app.models.catalog import KnowledgePack, Skill, ToolRecord
from sqlalchemy import select
from sqlalchemy.orm import Session

SEED_ROOT = Path(__file__).resolve().parents[3] / "data" / "seed"


def _seed_records(session: Session, model: type[Any], filename: str, unique_key: str) -> int:
    records = json.loads((SEED_ROOT / filename).read_text(encoding="utf-8"))
    existing = set(session.scalars(select(getattr(model, unique_key))).all())
    created = 0
    for record in records:
        if record[unique_key] in existing:
            continue
        session.add(model(**record))
        existing.add(record[unique_key])
        created += 1
    session.commit()
    return created


def seed_catalog(session: Session) -> dict[str, int]:
    return {
        "skills": _seed_records(session, Skill, "skills.json", "slug"),
        "tools": _seed_records(session, ToolRecord, "tools.json", "name"),
        "knowledge": _seed_records(session, KnowledgePack, "knowledge_packs.json", "slug"),
    }