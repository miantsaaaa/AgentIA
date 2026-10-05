import json
from pathlib import Path

from app.models.agent import Agent
from app.models.evaluation import ActivityEvent, Certificate, Evaluation
from sqlalchemy import select
from sqlalchemy.orm import Session

BENCHMARK_FILE = Path(__file__).resolve().parents[3] / "data" / "seed" / "benchmarks.json"


def evaluate_agent(session: Session, agent: Agent, benchmark_id: str) -> Evaluation:
    benchmarks = json.loads(BENCHMARK_FILE.read_text(encoding="utf-8"))
    benchmark = next((item for item in benchmarks if item["id"] == benchmark_id), None)
    if benchmark is None:
        raise ValueError("Benchmark introuvable")

    required_skills = set(benchmark["required_skills"])
    present_skills = required_skills.intersection(agent.skills)
    score = len(present_skills) / len(required_skills) if required_skills else 1.0
    passed = score >= benchmark["minimum_score"]
    result = Evaluation(
        agent_id=agent.id,
        benchmark_id=benchmark_id,
        score=score,
        passed=passed,
        details={
            "required_skills": sorted(required_skills),
            "present_skills": sorted(present_skills),
            "missing_skills": sorted(required_skills - present_skills),
        },
    )
    session.add(result)
    session.flush()
    session.add(
        ActivityEvent(
            agent_id=agent.id,
            event_type="EVALUATION_COMPLETED",
            details={"benchmark_id": benchmark_id, "score": score, "passed": passed},
        )
    )
    if passed and agent.level == "N0" and benchmark["certifies_level"] == "N1":
        session.add(Certificate(agent_id=agent.id, level="N1", evaluation_id=result.id))
        agent.level = "N1"
        agent.status = "CERTIFIED"
        session.add(
            ActivityEvent(
                agent_id=agent.id,
                event_type="AGENT_CERTIFIED",
                details={"level": "N1", "evaluation_id": result.id},
            )
        )
    elif agent.status in {"DRAFT", "TRAINING"}:
        agent.status = "EVALUATION" if passed else "TRAINING"
    session.commit()
    session.refresh(result)
    return result


def certificates_for_agent(session: Session, agent_id: str) -> list[Certificate]:
    return list(
        session.scalars(
            select(Certificate)
            .where(Certificate.agent_id == agent_id)
            .order_by(Certificate.issued_at)
        )
    )