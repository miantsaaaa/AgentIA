# Installation et démarrage

## Prérequis

Python 3.11+ et accès réseau uniquement pour installer les dépendances Python. Aucun modèle, Docker, compte cloud ou carte bancaire n'est requis. Node.js devient nécessaire avec le frontend.

## Windows PowerShell

```powershell
./scripts/setup.ps1
./scripts/seed.ps1
./scripts/dev.ps1
```

## Linux/macOS

```sh
sh scripts/setup.sh
sh scripts/seed.sh
sh scripts/dev.sh
```

Avec GNU Make : `make setup`, `make seed`, `make dev`. Le seed charge sans doublon les 35 agents et les catalogues initiaux skills/tools/knowledge depuis `data/seed/*.json`. La base locale est créée sous `data/agentia.db` et ignorée par Git. Pour cloner à terme : `git clone https://github.com/miantsaaaa/AgentIA.git` (publication pas encore effectuée).

Les poids de modèles, si ajoutés ultérieurement, seront téléchargés séparément et jamais stockés dans Git. La commande de démarrage UI n'est pas encore disponible.