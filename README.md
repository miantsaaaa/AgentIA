# AgentIA

![Version](https://img.shields.io/badge/version-0.0.0-informational)

Plateforme locale, extensible et contrôlable pour créer, évaluer et exploiter une bibliothèque d'agents professionnels. Le fournisseur de modèle `mock` est la cible du socle ; aucun service payant n'est requis.

## Démarrage rapide

Prérequis : Python 3.11 ou plus récent. Sous Windows, exécuter `./scripts/setup.ps1`, puis `./scripts/seed.ps1` et `./scripts/dev.ps1`. Sous Linux/macOS, utiliser `sh scripts/setup.sh`, `sh scripts/seed.sh` et `sh scripts/dev.sh`. Avec GNU Make : `make setup`, `make seed`, `make dev`.

L'API est disponible sur `http://127.0.0.1:8000`, sa documentation OpenAPI sur `/docs`, et son contrôle de santé sur `/health`. À ce stade, l'API du registre est en cours de construction ; l'interface et les parcours métier complets ne sont pas encore disponibles.

## État

Version locale `0.0.0`, sans release publiée. Le seed fournit les 35 agents au niveau N0. Voir [l'index documentaire](docs/00_INDEX.md), [le TODO](docs/33_TODO.md) et [le workflow Git](docs/41_GIT_WORKFLOW.md).