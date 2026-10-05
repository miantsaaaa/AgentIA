# Architecture

## Statut : IMPLEMENTED (socle)

Backend FastAPI + Pydantic v2 + SQLAlchemy 2, SQLite local. Seeds versionnés JSON couvrent agents, skills, métadonnées de tools, knowledge packs et benchmark. API CRUD pour agents/skills/tools/knowledge et lien AgentSkill ; tools personnalisés sans runner restent inertes. Le runtime dépend de `ModelProvider`, implémenté par Ollama local avec Qwen3-4B testé. Évaluation réelle ; sans Ollama, runtime répond 503 et ne certifie pas. Migrations Alembic, API de consultation d'activité, UI et sandbox restent planifiées.