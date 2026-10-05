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
