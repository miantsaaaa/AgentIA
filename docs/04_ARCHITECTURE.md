# Architecture

## Statut : IMPLEMENTED (socle)

Backend FastAPI + Pydantic v2 + SQLAlchemy 2, SQLite local. Données de départ et benchmark versionnés en JSON. Le runtime dépend du protocole `ModelProvider`, actuellement implémenté par Ollama local avec Qwen3-4B testé. L'évaluation utilise une réponse réelle ; en cas d'indisponibilité le runtime retourne 503 et aucune certification n'est créée. L'interface, les autres registres, migrations Alembic et sandbox restent planifiés.