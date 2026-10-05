# Tests et qualité

## Statut : TESTED (registre ciblé)

Les wrappers setup/test/lint PowerShell ou Bash ciblent `.venv` dans le workspace, sans installation dans le Python système. Les tests standard utilisent SQLite éphémère et n'exigent pas Ollama ; certification/runtime réels utilisent `AGENTIA_RUN_MODEL_TESTS=1` avec Ollama et Qwen3-4B. Résultats au 2026-10-05 : suite standard 17 passed / 2 skipped ; migrations SQLite upgrade/downgrade et adoption legacy 2 passed ; intégration Ollama (génération provider + certification L1) 2 passed en 66,19 s. Seed CLI après migration sur base neuve : 35 agents, 3 skills, 5 tools, 1 knowledge pack ; seconde exécution : 0 ajout pour chaque registre. Avertissement Starlette/httpx reste à résoudre en industrialisation.

`make release-check` et son script PowerShell ne sont pas encore des portes de release complètes et échouent volontairement tant que frontend et contrôles manquent.