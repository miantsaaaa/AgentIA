# AgentIA

![Version](https://img.shields.io/badge/version-0.0.0-informational)

Plateforme locale, extensible et contrôlable pour créer, évaluer et exploiter une bibliothèque d'agents professionnels. La génération s'appuie sur Ollama et un modèle open-weight local ; aucune réponse de modèle factice ni aucun service payant n'est utilisé.

## Démarrage rapide

Prérequis : Python 3.11 ou plus récent. Le registre fonctionne sans modèle ; pour le runtime et les évaluations, installer [Ollama](https://ollama.com/) et télécharger un modèle autorisé commercialement (par défaut `qwen3:4b` via `ollama pull qwen3:4b`). Sous Windows, exécuter `./scripts/setup.ps1`, puis `./scripts/seed.ps1` et `./scripts/dev.ps1`. Sous Linux/macOS, utiliser `sh scripts/setup.sh`, `sh scripts/seed.sh` et `sh scripts/dev.sh`. Avec GNU Make : `make setup`, `make seed`, `make dev`.

L'API est disponible sur `http://127.0.0.1:8000`, sa documentation OpenAPI sur `/docs`, et son contrôle de santé sur `/health`. L'interface et plusieurs registres métier restent à construire.

## État

Version locale `0.0.0`, sans release publiée. Le seed fournit les 35 agents au niveau N0. Voir [l'index documentaire](docs/00_INDEX.md), [le TODO](docs/33_TODO.md) et [le workflow Git](docs/41_GIT_WORKFLOW.md).