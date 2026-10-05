# Modèle de données

## Statut : IMPLEMENTED (premières entités)

SQLite contient agents, skills, liaison `agent_skills`, `tool_registry`, `knowledge_packs`, évaluations, certificats, événements d'activité, permissions, approbations, paramètres runtime, audit, missions et événements mission. Le journal d'audit est hash-chaîné côté application ; un accès direct à SQLite peut le modifier. Les tables sont créées par SQLAlchemy ; les migrations Alembic, snapshots et historique versionné d'agent restent PLANNED.