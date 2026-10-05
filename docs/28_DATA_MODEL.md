# Modèle de données

## Statut : IMPLEMENTED (premières entités)

SQLite contient `agents`, `evaluations`, `certificates` et `activity_events`. Les événements sont append-only via l'API actuelle mais sans chaîne de hash ni protection contre un accès direct à la base. Migrations Alembic, skills, tools, knowledge, missions et snapshots restent PLANNED.