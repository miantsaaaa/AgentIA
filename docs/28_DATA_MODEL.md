# Modèle de données

## Statut : IMPLEMENTED (premières entités)

SQLite contient `agents`, `evaluations`, `certificates`, `activity_events`, `agent_permissions`, `approvals`, `runtime_settings` et `audit_records`. Le journal d'audit est hash-chaîné côté application ; un accès direct à SQLite peut le modifier. Migrations Alembic, skills, knowledge, missions et snapshots restent PLANNED.