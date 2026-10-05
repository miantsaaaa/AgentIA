# Modèle de données

## Statut : IMPLEMENTED (premières entités)

SQLite contient agents, agents système, skills, liaison `agent_skills`, `tool_registry`, `knowledge_packs`, évaluations, certificats, événements d'activité, permissions, approbations, paramètres runtime, audit, missions et événements mission. La nouvelle table `system_agents` est versionnée par migration Alembic. Un schéma complet préexistant est marqué à head sans recréation ; un schéma incomplet non versionné est refusé. Snapshots et historique versionné d'agent restent PLANNED.