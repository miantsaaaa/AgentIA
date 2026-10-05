# Changelog

Les changements notables sont consignés ici, selon Keep a Changelog. Le format de version suit SemVer.

## [0.0.0] - 2026-10-05
### Ajouté
- Fondations locales, documentation initiale, API FastAPI de registre et seed idempotent des 35 agents.
- Tests du health check, du seed, de la pagination et du niveau N0 imposé à la création.
- Transitions d'état contrôlées, benchmark déterministe L1, évaluations, certificat N1 et événements d'activité.
- Permission Manager refusant par défaut, outils lecture/calcul/paper trading, kill switch et audit SHA-256 chaîné.
- Provider Ollama réel, runtime d'agent et benchmark L1 basé sur la réponse réelle de Qwen3-4B.
- Recommandation déterministe explicable et machine d'état de mission persistée.
- Registres CRUD de skills, tools et knowledge packs, avec seeds versionnés et idempotents.
- Liens AgentSkill et scripts PowerShell/Bash installant uniquement dans le venv du projet.
- Migration initiale Alembic et adoption sans perte des bases complètes préexistantes.
- Règles communes de travail des agents et vérification automatisée de l'organisation documentaire.
- Registre central `docs/43_IMPLEMENTATION_STATUS.md` validé par le checker pre-commit.
- Agent système IAntsaM seedé séparément, chat Ollama réel et recommandation Helpdesk.
- Boucle de knowledge pack candidat, évalué par Ollama puis promu avec révision SemVer et assignation explicite.
- Rejet des propositions évaluées sur une version obsolète et backfill de la version cible en migration.

### Sécurité
- Aucun endpoint ne permet de modifier librement le niveau d'un agent.
- Aucun push distant n'a été effectué.