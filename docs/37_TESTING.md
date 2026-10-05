# Tests et qualité

## Statut : TESTED (registre ciblé)

Les wrappers setup/test/lint PowerShell ou Bash ciblent `.venv` dans le workspace, sans installation dans le Python système. Les tests standard utilisent SQLite éphémère et n'exigent pas Ollama ; certification/runtime réels utilisent `AGENTIA_RUN_MODEL_TESTS=1` avec Ollama et Qwen3-4B. Résultats au 2026-10-05 : suite standard 24 passed / 4 skipped ; migrations incluent upgrade/downgrade, adoption legacy et backfill des propositions existantes ; checker d'organisation testé. Intégrations Ollama : provider + certification L1, chat IAntsaM et évolution d'un knowledge pack sont passés séparément. Seed CLI après migration sur base neuve : 35 agents, 3 skills, 5 tools, 1 knowledge pack ; seconde exécution : 0 ajout. Avertissement Starlette/httpx reste à résoudre en industrialisation.

`make release-check` et son script PowerShell ne sont pas encore des portes de release complètes et échouent volontairement tant que frontend et contrôles manquent.