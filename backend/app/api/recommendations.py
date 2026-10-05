from app.core.database import get_db
from app.services.recommender import recommend_agents
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


class RecommendationRequest(BaseModel):
    request: str = Field(min_length=3, max_length=2000)
    limit: int = Field(default=3, ge=1, le=10)


@router.post("")
def recommend(
    request: RecommendationRequest,
    session: Session = Depends(get_db),
) -> dict[str, object]:
    return recommend_agents(session, request.request, request.limit)