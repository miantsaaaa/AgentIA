import os
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
    if os.getenv("AGENTIA_RUN_MODEL_TESTS") != "1":
        pytest.skip("Activer AGENTIA_RUN_MODEL_TESTS=1 pour certifier avec le vrai modèle local")
    with Session(database.engine) as session:
        seed_agents(session)
    agent = client.get("/api/agents", params={"q": "Helpdesk L1"}).json()["items"][0]
    result = client.post(
        f"/api/agents/{agent['id']}/evaluations",
        json={"benchmark_id": "helpdesk-l1-foundations-v1"},
    )
    assert result.status_code == 200
    assert result.json()["passed"] is True, result.json()
    assert result.json()["agent_level"] == "N1"
    assert result.json()["agent_status"] == "CERTIFIED"
    assert result.json()["details"]["generated_response"]
    assert result.json()["details"]["provider"] == "ollama"


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


def seeded_agent(client: TestClient) -> dict[str, object]:
    with Session(database.engine) as session:
        seed_agents(session)
    return client.get("/api/agents", params={"q": "Helpdesk L1"}).json()["items"][0]


def test_tool_permissions_are_denied_by_default_and_audit_is_valid(client: TestClient) -> None:
    agent = seeded_agent(client)
    response = client.post(
        f"/api/agents/{agent['id']}/tools/calculator/actions",
        json={"inputs": {"expression": "1 + 2 * 3"}},
    )
    assert response.status_code == 403
    assert client.get("/api/audit/verify").json()["valid"] is True


def test_explicit_calculator_permission_executes_safe_math(client: TestClient) -> None:
    agent = seeded_agent(client)
    permission = client.put(
        f"/api/agents/{agent['id']}/permissions/calculator",
        json={"granted": True},
    )
    result = client.post(
        f"/api/agents/{agent['id']}/tools/calculator/actions",
        json={"inputs": {"expression": "1 + 2 * 3"}},
    )
    assert permission.status_code == 200
    assert result.status_code == 200
    assert result.json()["result"]["result"] == 7
    assert client.get("/api/audit/verify").json()["valid"] is True


def test_critical_tool_waits_for_human_approval(client: TestClient) -> None:
    agent = seeded_agent(client)
    client.put(
        f"/api/agents/{agent['id']}/permissions/quant.paper_trade",
        json={"granted": True},
    )
    action = client.post(
        f"/api/agents/{agent['id']}/tools/quant.paper_trade/actions",
        json={"inputs": {"symbol": "DEMO", "quantity": 1}},
    )
    assert action.status_code == 200
    assert action.json()["status"] == "WAITING_APPROVAL"
    approval = client.post(f"/api/approvals/{action.json()['approval_id']}/approve")
    assert approval.status_code == 200
    altered = client.post(
        f"/api/agents/{agent['id']}/tools/quant.paper_trade/actions",
        json={
            "inputs": {"symbol": "OTHER", "quantity": 99},
            "approval_id": action.json()["approval_id"],
        },
    )
    assert altered.status_code == 403
    execution = client.post(
        f"/api/agents/{agent['id']}/tools/quant.paper_trade/actions",
        json={
            "inputs": {"symbol": "DEMO", "quantity": 1},
            "approval_id": action.json()["approval_id"],
        },
    )
    assert execution.status_code == 200
    assert execution.json()["result"]["mode"] == "PAPER_ONLY"
    assert client.get("/api/audit/verify").json()["valid"] is True


def test_kill_switch_blocks_even_a_permitted_tool(client: TestClient) -> None:
    agent = seeded_agent(client)
    client.put(
        f"/api/agents/{agent['id']}/permissions/calculator",
        json={"granted": True},
    )
    client.put("/api/system/kill-switch", json={"enabled": True})
    result = client.post(
        f"/api/agents/{agent['id']}/tools/calculator/actions",
        json={"inputs": {"expression": "1 + 1"}},
    )
    assert result.status_code == 423
    client.put("/api/system/kill-switch", json={"enabled": False})


def test_file_tool_cannot_escape_authorized_workspace(client: TestClient) -> None:
    agent = seeded_agent(client)
    client.put(
        f"/api/agents/{agent['id']}/permissions/file.read",
        json={"granted": True},
    )
    result = client.post(
        f"/api/agents/{agent['id']}/tools/file.read/actions",
        json={"inputs": {"path": "../VERSION"}},
    )
    assert result.status_code == 403
