# Architecture

## Statut : IMPLEMENTED (socle)

Backend FastAPI + Pydantic v2 + SQLAlchemy 2, SQLite local sous migrations Alembic. Le bootstrap adopte à `head` un schéma legacy complet sans recréer ses tables et refuse un schéma partiel. Seeds versionnés JSON couvrent agents, skills, métadonnées de tools, knowledge packs et benchmark. API CRUD agents/skills/tools/knowledge et lien AgentSkill ; tools personnalisés sans runner restent inertes. Le runtime dépend d'Ollama local avec Qwen3-4B testé. Sans Ollama, runtime répond 503 et ne certifie pas. API d'activité, UI et sandbox restent planifiées.