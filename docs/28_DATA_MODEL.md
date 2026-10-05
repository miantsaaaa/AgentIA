# Modèle de données

## Statut : IMPLEMENTED (premières entités)

SQLite contient agents, agents système, skills, liaison `agent_skills`, `tool_registry`, `knowledge_packs`, propositions, révisions, liaison `agent_knowledge`, évaluations, certificats, événements d'activité, permissions, approbations, paramètres runtime, audit, missions et événements mission. Les migrations Alembic couvrent ces entités. Un schéma complet préexistant est marqué à head sans recréation ; un schéma incomplet non versionné est refusé. Snapshots et historique versionné d'agent restent PLANNED.