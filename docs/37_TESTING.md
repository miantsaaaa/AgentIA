# Tests et qualité

## Statut : TESTED (registre ciblé)

Commande backend : `.venv/Scripts/python.exe -m pytest` sous Windows, `python -m pytest` dans le venv sous Linux/macOS. Les tests standard utilisent SQLite éphémère pour isoler l'API et n'exigent pas Ollama ; les parcours de certification/runtime réels sont activés par `AGENTIA_RUN_MODEL_TESTS=1` et appellent le service local et Qwen3-4B. Résultats au 2026-10-05 : suite standard après M1 15 passed / 2 skipped ; intégration Ollama (génération provider + certification L1) 2 passed en 66,19 s. Seed CLI sur base neuve : 35 agents, 3 skills, 5 tools, 1 knowledge pack ; seconde exécution : 0 ajout pour chaque registre. Ces tests d'intégration ne sont pas remplacés par des stubs. L'avertissement Starlette/httpx reste à résoudre en industrialisation.

`make release-check` et son script PowerShell ne sont pas encore des portes de release complètes et échouent volontairement tant que frontend et contrôles manquent.