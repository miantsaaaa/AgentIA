import os
from collections.abc import Generator

import pytest
from app.core import database
from app.main import app
from app.models.system_agent import SystemAgent
from app.services.catalog import seed_system_agents
from app.services.registry import seed_agents
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    monkeypatch.setattr(database, "engine", engine)
    with TestClient(app) as test_client:
        yield test_client
    engine.dispose()


def test_iantsam_seed_is_idempotent(client: TestClient) -> None:
    with Session(database.engine) as session:
        assert seed_system_agents(session) == 1
        assert seed_system_agents(session) == 0
        assert session.scalar(select(func.count()).select_from(SystemAgent)) == 1


@pytest.mark.integration
def test_iantsam_chat_uses_real_model_and_returns_agent_recommendations(
    client: TestClient,
) -> None:
    if os.getenv("AGENTIA_RUN_MODEL_TESTS") != "1":
        pytest.skip("Activer AGENTIA_RUN_MODEL_TESTS=1 pour appeler Qwen local")
    with Session(database.engine) as session:
        seed_agents(session)
        assert seed_system_agents(session) == 1
    response = client.post(
        "/api/chat",
        json={
            "assistant_id": "iantsam",
            "message": "Je dois automatiser le support utilisateur et le triage.",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["assistant_name"] == "IAntsaM"
    assert payload["provider"] == "ollama"
    assert payload["response"]
    assert payload["recommendations"]["recommendations"][0]["name"] == "Helpdesk L1"