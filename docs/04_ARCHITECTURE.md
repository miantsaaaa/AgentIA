# Architecture

## Statut : IMPLEMENTED (socle)

Backend FastAPI + Pydantic v2 + SQLAlchemy 2, SQLite local. Données de départ versionnées en JSON. Le modèle Agent et le registre sont dans `backend/app`; l'API expose `/health` et `/api/agents`. L'interface, les autres registres, migrations Alembic et couches d'exécution restent planifiés.