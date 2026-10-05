# Changelog

Les changements notables sont consignés ici, selon Keep a Changelog. Le format de version suit SemVer.

## [0.0.0] - 2026-10-05
### Ajouté
- Fondations locales, documentation initiale, API FastAPI de registre et seed idempotent des 35 agents.
- Tests du health check, du seed, de la pagination et du niveau N0 imposé à la création.
- Transitions d'état contrôlées, benchmark déterministe L1, évaluations, certificat N1 et événements d'activité.

### Sécurité
- Aucun endpoint ne permet de modifier librement le niveau d'un agent.
- Aucun push distant n'a été effectué.