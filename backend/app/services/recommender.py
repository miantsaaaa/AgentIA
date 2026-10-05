import re
import unicodedata

from app.models.agent import Agent
from sqlalchemy import select
from sqlalchemy.orm import Session

STOP_WORDS = {"avec", "dans", "pour", "une", "des", "les", "sur", "qui", "est", "faire"}
STATUS_WEIGHT = {"PRODUCTION": 5, "AVAILABLE": 3, "CERTIFIED": 2, "DRAFT": -2}


def _terms(text: str) -> set[str]:
    normalized = unicodedata.normalize("NFKD", text.casefold())
    ascii_text = "".join(char for char in normalized if not unicodedata.combining(char))
    words = re.findall(r"[a-z0-9]+", ascii_text)
    return {term for term in words if len(term) > 2 and term not in STOP_WORDS}


def recommend_agents(session: Session, request: str, limit: int = 3) -> dict[str, object]:
    request_terms = _terms(request)
    agents = session.scalars(select(Agent)).all()
    candidates = []
    matched_anywhere: set[str] = set()
    for agent in agents:
        searchable = _terms(" ".join([agent.name, agent.domain, agent.description, *agent.skills]))
        matches = sorted(request_terms & searchable)
        matched_anywhere.update(matches)
        level_weight = int(agent.level[1]) * 1.5
        score = round(len(matches) * 10 + level_weight + STATUS_WEIGHT.get(agent.status, 0), 2)
        gaps = []
        if int(agent.level[1]) < 4:
            gaps.append(
                f"N{agent.level[1]} : certification N4 minimum absente, "
                "validation humaine requise"
            )
        if agent.status not in {"AVAILABLE", "PRODUCTION"}:
            gaps.append(f"Statut {agent.status} : agent non disponible en production")
        candidates.append(
            {
                "agent_id": agent.id,
                "name": agent.name,
                "domain": agent.domain,
                "tier": agent.tier,
                "level": agent.level,
                "status": agent.status,
                "score": score,
                "matched_terms": matches,
                "justification": (
                    f"Correspondance sur {', '.join(matches)}"
                    if matches
                    else "Aucune compétence textuelle directe"
                ),
                "gaps": gaps,
            }
        )
    candidates.sort(key=lambda item: (-item["score"], item["tier"], item["name"]))
    relevant = [candidate for candidate in candidates if candidate["matched_terms"]][:limit]
    return {
        "request": request,
        "method": "deterministic_keyword_skill_level_status_v1",
        "recommendations": relevant,
        "unmatched_terms": sorted(request_terms - matched_anywhere),
    }