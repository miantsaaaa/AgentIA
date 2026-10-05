import os
from collections.abc import Generator

import pytest
from app.core import database
from app.main import app
from app.models.system_agent import SystemAgent
from app.services.catalog import seed_catalog, seed_system_agents
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


@pytest.mark.integration
def test_knowledge_candidate_requires_real_evaluation_before_agent_runtime_uses_it(
    client: TestClient,
) -> None:
    if os.getenv("AGENTIA_RUN_MODEL_TESTS") != "1":
        pytest.skip("Activer AGENTIA_RUN_MODEL_TESTS=1 pour évaluer avec Qwen local")
    with Session(database.engine) as session:
        seed_agents(session)
        seed_catalog(session)
    agent = client.get("/api/agents", params={"q": "Helpdesk L1"}).json()["items"][0]
    pack = client.get("/api/knowledge").json()["items"][0]
    original_content = pack["content"]
    assert client.put(f"/api/agents/{agent['id']}/knowledge/{pack['id']}").status_code == 204
    scenario = "Quel est le code de référence du diagnostic de démonstration ? Réponds brièvement."

    candidate_content = "Pour le diagnostic de démonstration, le code de référence est ORION-731."
    proposal = client.post(
        f"/api/knowledge/{pack['id']}/proposals",
        json={
            "proposed_content": candidate_content,
            "source": "Créé en interne pour l'évaluation locale",
            "source_license": "MIT",
            "reliability": 1.0,
            "change_reason": "Ajouter un code de référence vérifiable par benchmark.",
            "proposed_by": "local_user",
            "minimum_score": 1.0,
        },
    ).json()
    pending_context = client.get(f"/api/agents/{agent['id']}/knowledge").json()["context"]
    assert "ORION-731" not in pending_context

    evaluated = client.post(
        f"/api/knowledge-proposals/{proposal['id']}/evaluate",
        json={
            "agent_id": agent["id"],
            "scenario": scenario,
            "required_terms": ["ORION-731"],
        },
    )
    assert evaluated.status_code == 200
    assert evaluated.json()["status"] == "EVALUATED"
    assert evaluated.json()["evaluation_score"] == 1.0
    assert evaluated.json()["evaluation_details"]["provider"] == "ollama"

    approved = client.post(
        f"/api/knowledge-proposals/{proposal['id']}/approve",
        json={"confirm": True},
    )
    assert approved.status_code == 200
    assert approved.json()["version"] == "1.0.1"
    revisions = client.get(f"/api/knowledge/{pack['id']}/revisions").json()
    assert revisions[0]["version"] == "1.0.0"
    assert revisions[0]["content"] == original_content

    runtime = client.post(
        f"/api/agents/{agent['id']}/run",
        json={"prompt": scenario},
    )
    assert runtime.status_code == 200
    assert "ORION-731" in runtime.json()["response"]