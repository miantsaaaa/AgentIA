# Changelog

Les changements notables sont consignés ici, selon Keep a Changelog. Le format de version suit SemVer.

## [0.0.0] - 2026-10-05
### Ajouté
- Fondations locales, documentation initiale, API FastAPI de registre et seed idempotent des 35 agents.
- Tests du health check, du seed, de la pagination et du niveau N0 imposé à la création.
- Transitions d'état contrôlées, benchmark déterministe L1, évaluations, certificat N1 et événements d'activité.
- Permission Manager refusant par défaut, outils lecture/calcul/paper trading, kill switch et audit SHA-256 chaîné.
- Provider Ollama réel, runtime d'agent et benchmark L1 basé sur la réponse réelle de Qwen3-4B.

### Sécurité
- Aucun endpoint ne permet de modifier librement le niveau d'un agent.
- Aucun push distant n'a été effectué.