import hashlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models.workspace import WorkspaceChange
from app.services import workspace as ws_service


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(ws_service, "_workspace_root", lambda: tmp_path)
    return tmp_path


def sha256(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Unit tests — service layer
# ---------------------------------------------------------------------------


def test_propose_creates_pending(db_session, workspace):
    """propose_change crée une proposition PENDING avec le bon hash et diff."""
    change = ws_service.propose_change(db_session, "foo.txt", "new content\n", "test-agent")
    assert change.status == "PENDING"
    assert change.expected_hash == sha256("")  # fichier inexistant → contenu vide
    assert "new content" in change.unified_diff
    assert change.requester == "test-agent"
    assert change.proposed_content == "new content\n"


def test_propose_existing_file(db_session, workspace):
    """propose_change calcule le hash du contenu actuel quand le fichier existe."""
    target = workspace / "existing.txt"
    target.write_text("old content\n", encoding="utf-8")
    change = ws_service.propose_change(db_session, "existing.txt", "new content\n", "agent")
    assert change.expected_hash == sha256("old content\n")
    assert "-old content" in change.unified_diff
    assert "+new content" in change.unified_diff


def test_approve_change_transitions_status(db_session, workspace):
    """approve_change passe le statut à APPROVED et renseigne approved_at."""
    change = ws_service.propose_change(db_session, "a.txt", "contenu\n", "agent")
    approved = ws_service.approve_change(db_session, change.id, decision_note="LGTM")
    assert approved.status == "APPROVED"
    assert approved.approved_at is not None
    assert approved.decision_note == "LGTM"


def test_reject_change_transitions_status(db_session, workspace):
    """reject_change passe le statut à REJECTED."""
    change = ws_service.propose_change(db_session, "b.txt", "contenu\n", "agent")
    rejected = ws_service.reject_change(db_session, change.id, decision_note="Non conforme")
    assert rejected.status == "REJECTED"
    assert rejected.decision_note == "Non conforme"


def test_apply_change_writes_file_and_sets_applied(db_session, workspace):
    """apply_change écrit le fichier sur disque et passe le statut à APPLIED."""
    change = ws_service.propose_change(db_session, "output.txt", "contenu final\n", "agent")
    ws_service.approve_change(db_session, change.id)
    applied = ws_service.apply_change(db_session, change.id)
    assert applied.status == "APPLIED"
    assert applied.applied_hash == sha256("contenu final\n")
    written = (workspace / "output.txt").read_text(encoding="utf-8")
    assert written == "contenu final\n"


def test_apply_change_creates_parent_dirs(db_session, workspace):
    """apply_change crée les répertoires parents si nécessaire."""
    change = ws_service.propose_change(db_session, "sub/dir/file.txt", "texte\n", "agent")
    ws_service.approve_change(db_session, change.id)
    ws_service.apply_change(db_session, change.id)
    assert (workspace / "sub" / "dir" / "file.txt").read_text(encoding="utf-8") == "texte\n"


def test_apply_change_raises_on_hash_mismatch(db_session, workspace):
    """apply_change lève ValueError si le fichier a été modifié après la proposition."""
    target = workspace / "mutable.txt"
    target.write_text("original\n", encoding="utf-8")
    change = ws_service.propose_change(db_session, "mutable.txt", "mise à jour\n", "agent")
    ws_service.approve_change(db_session, change.id)
    # Modifier le fichier entre la proposition et l'application
    target.write_text("modifié entre temps\n", encoding="utf-8")
    with pytest.raises(ValueError, match="modifié depuis la proposition"):
        ws_service.apply_change(db_session, change.id)


def test_approve_already_approved_raises(db_session, workspace):
    """approve_change sur une proposition déjà APPROVED lève ValueError."""
    change = ws_service.propose_change(db_session, "c.txt", "contenu\n", "agent")
    ws_service.approve_change(db_session, change.id)
    with pytest.raises(ValueError, match="Statut invalide pour approbation"):
        ws_service.approve_change(db_session, change.id)


def test_reject_non_pending_raises(db_session, workspace):
    """reject_change sur une proposition REJECTED lève ValueError."""
    change = ws_service.propose_change(db_session, "d.txt", "contenu\n", "agent")
    ws_service.reject_change(db_session, change.id)
    with pytest.raises(ValueError, match="Statut invalide pour rejet"):
        ws_service.reject_change(db_session, change.id)


def test_list_changes_status_filter(db_session, workspace):
    """list_changes avec filtre de statut retourne uniquement les enregistrements correspondants."""
    ws_service.propose_change(db_session, "e.txt", "e\n", "agent")
    c2 = ws_service.propose_change(db_session, "f.txt", "f\n", "agent")
    ws_service.approve_change(db_session, c2.id)

    pending = ws_service.list_changes(db_session, status="PENDING")
    approved = ws_service.list_changes(db_session, status="APPROVED")
    all_changes = ws_service.list_changes(db_session)

    assert len(pending) == 1
    assert pending[0].relative_path == "e.txt"
    assert len(approved) == 1
    assert approved[0].relative_path == "f.txt"
    assert len(all_changes) == 2


def test_approve_unknown_id_raises(db_session, workspace):
    """approve_change sur un identifiant inconnu lève KeyError."""
    with pytest.raises(KeyError, match="Proposition introuvable"):
        ws_service.approve_change(db_session, "inexistant")


def test_apply_unknown_id_raises(db_session, workspace):
    """apply_change sur un identifiant inconnu lève KeyError."""
    with pytest.raises(KeyError, match="Proposition introuvable"):
        ws_service.apply_change(db_session, "inexistant")


def test_apply_pending_raises(db_session, workspace):
    """apply_change sur une proposition PENDING (non approuvée) lève ValueError."""
    change = ws_service.propose_change(db_session, "g.txt", "g\n", "agent")
    with pytest.raises(ValueError, match="Statut invalide pour application"):
        ws_service.apply_change(db_session, change.id)


# ---------------------------------------------------------------------------
# API round-trip via TestClient
# ---------------------------------------------------------------------------


@pytest.fixture
def api_client(tmp_path, monkeypatch):
    """Client FastAPI configuré avec une base in-memory et un workspace temporaire."""
    from sqlalchemy.pool import StaticPool

    from app.core import database as db_module
    from app.main import app

    # Base in-memory partagée via StaticPool (même connexion pour toutes les sessions)
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    monkeypatch.setattr(db_module, "engine", test_engine)
    monkeypatch.setattr(ws_service, "_workspace_root", lambda: tmp_path)

    with TestClient(app) as client:
        yield client, tmp_path

    test_engine.dispose()


def test_api_full_round_trip(api_client):
    """Cycle complet : propose → GET /{id} → approve → apply → vérification fichier."""
    client, tmp_path = api_client

    # 1. Proposer
    resp = client.post(
        "/api/workspace/propose",
        json={
            "relative_path": "roundtrip.txt",
            "proposed_content": "contenu final\n",
            "requester": "test-bot",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    change_id = data["id"]
    assert data["status"] == "PENDING"

    # 2. GET /{id}
    resp = client.get(f"/api/workspace/{change_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == change_id

    # 3. Approuver
    resp = client.post(f"/api/workspace/{change_id}/approve", json={"decision_note": "OK"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "APPROVED"

    # 4. Appliquer
    resp = client.post(f"/api/workspace/{change_id}/apply")
    assert resp.status_code == 200
    result = resp.json()
    assert result["status"] == "APPLIED"
    assert result["applied_hash"] == sha256("contenu final\n")

    # 5. Vérifier le fichier sur disque
    written = (tmp_path / "roundtrip.txt").read_text(encoding="utf-8")
    assert written == "contenu final\n"


def test_api_list_with_status_filter(api_client):
    """GET /api/workspace/?status=PENDING filtre correctement."""
    client, _ = api_client

    client.post(
        "/api/workspace/propose",
        json={"relative_path": "p1.txt", "proposed_content": "x\n", "requester": "bot"},
    )
    resp2 = client.post(
        "/api/workspace/propose",
        json={"relative_path": "p2.txt", "proposed_content": "y\n", "requester": "bot"},
    )
    change_id = resp2.json()["id"]
    client.post(f"/api/workspace/{change_id}/reject", json={})

    pending = client.get("/api/workspace/?status=PENDING").json()
    rejected = client.get("/api/workspace/?status=REJECTED").json()
    assert len(pending) == 1
    assert len(rejected) == 1


def test_api_get_unknown_returns_404(api_client):
    """GET /api/workspace/{id} sur un id inexistant retourne 404."""
    client, _ = api_client
    resp = client.get("/api/workspace/inexistant-id")
    assert resp.status_code == 404


def test_api_approve_conflict_on_non_pending(api_client):
    """POST /api/workspace/{id}/approve sur une proposition APPROVED retourne 409."""
    client, _ = api_client
    resp = client.post(
        "/api/workspace/propose",
        json={"relative_path": "x.txt", "proposed_content": "x\n", "requester": "bot"},
    )
    change_id = resp.json()["id"]
    client.post(f"/api/workspace/{change_id}/approve", json={})
    resp2 = client.post(f"/api/workspace/{change_id}/approve", json={})
    assert resp2.status_code == 409


def test_api_hash_mismatch_returns_409(api_client):
    """POST /apply retourne 409 avec code HASH_MISMATCH si le fichier a dérivé."""
    client, tmp_path = api_client

    # 1. Proposer
    resp = client.post(
        "/api/workspace/propose",
        json={
            "relative_path": "drift.txt",
            "proposed_content": "nouveau contenu\n",
            "requester": "test-bot",
        },
    )
    assert resp.status_code == 200
    change_id = resp.json()["id"]

    # 2. Approuver
    resp = client.post(f"/api/workspace/{change_id}/approve", json={})
    assert resp.status_code == 200

    # 3. Écrire un contenu différent sur disque (simule une dérive)
    (tmp_path / "drift.txt").write_text("contenu différent\n", encoding="utf-8")

    # 4. Appliquer — doit retourner 409 HASH_MISMATCH
    resp = client.post(f"/api/workspace/{change_id}/apply")
    assert resp.status_code == 409
    assert resp.json()["code"] == "HASH_MISMATCH"
