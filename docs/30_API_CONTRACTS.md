# Contrats API

## Statut : IMPLEMENTED (contrat courant)

Contrat généré par FastAPI : `GET /health`, `GET /api/agents`, `GET /api/agents/{agent_id}`, `POST /api/agents`, `POST /api/agents/{agent_id}/transitions`, `POST /api/agents/{agent_id}/evaluations`. La liste accepte `page` (défaut 1), `page_size` (1-100, défaut 20), `q`, `tier` (1-5), `level` (N0-N7) et `status`. La création ne prend pas `level` et fixe N0/DRAFT/0.1.0. La transition reçoit `target_status` et refuse les arcs non autorisés (409). L'évaluation reçoit `benchmark_id`. `/openapi.json` est la source générée.