from collections.abc import Generator

import pytest
from app.core import database
from app.main import app
from app.services.registry import seed_agents
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    monkeypatch.setattr(database, "engine", test_engine)
    with TestClient(app) as test_client:
        yield test_client
    test_engine.dispose()


def test_health_and_agent_seed_are_available_and_idempotent(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}
    with Session(database.engine) as session:
        assert seed_agents(session) == 35
        assert seed_agents(session) == 0
    response = client.get("/api/agents?page_size=100")
    assert response.status_code == 200
    assert response.json()["total"] == 35


def test_agent_creation_cannot_assign_a_certified_level(client: TestClient) -> None:
    response = client.post(
        "/api/agents",
        json={
            "slug": "nouvel-agent",
            "name": "Nouvel agent",
            "domain": "Test",
            "tier": 1,
            "description": "Agent de test",
            "level": "N7",
        },
    )
    assert response.status_code == 201
    assert response.json()["level"] == "N0"


def test_agent_filters_and_pagination(client: TestClient) -> None:
    with Session(database.engine) as session:
        seed_agents(session)
    response = client.get("/api/agents", params={"tier": 1, "page_size": 2})
    assert response.status_code == 200
    assert response.json()["total"] == 5
    assert len(response.json()["items"]) == 2


def test_only_successful_evaluation_issues_level_certificate(client: TestClient) -> None:
    with Session(database.engine) as session:
        seed_agents(session)
    agent = client.get("/api/agents", params={"q": "Helpdesk L1"}).json()["items"][0]
    result = client.post(
        f"/api/agents/{agent['id']}/evaluations",
        json={"benchmark_id": "helpdesk-l1-foundations-v1"},
    )
    assert result.status_code == 200
    assert result.json()["passed"] is True
    assert result.json()["agent_level"] == "N1"
    assert result.json()["agent_status"] == "CERTIFIED"


def test_failed_evaluation_keeps_agent_at_n0(client: TestClient) -> None:
    with Session(database.engine) as session:
        seed_agents(session)
    agent = client.get("/api/agents", params={"q": "Backend"}).json()["items"][0]
    result = client.post(
        f"/api/agents/{agent['id']}/evaluations",
        json={"benchmark_id": "helpdesk-l1-foundations-v1"},
    )
    assert result.status_code == 200
    assert result.json()["passed"] is False
    assert result.json()["agent_level"] == "N0"
    assert result.json()["details"]["missing_skills"]


def test_invalid_lifecycle_transition_is_rejected(client: TestClient) -> None:
    with Session(database.engine) as session:
        seed_agents(session)
    agent = client.get("/api/agents", params={"page_size": 1}).json()["items"][0]
    response = client.post(
        f"/api/agents/{agent['id']}/transitions",
        json={"target_status": "PRODUCTION"},
    )
    assert response.status_code == 409
