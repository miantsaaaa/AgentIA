# Décisions

## Décisions prises

| ID | Décision | Motif / état |
|---|---|---|
| DEC-001 | Backend Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2, SQLite | Stack demandée ; Python 3.14.3 local, cible minimale 3.11. Migrations Alembic à ajouter. |
| DEC-002 | Données de seed versionnées en JSON | Standard intégré, diff lisible, pas de dépendance YAML. |
| DEC-003 | Fournisseur `mock` comme voie de base | Fonctionnement déterministe sans modèle ni service externe ; abstraction à implémenter. |
| DEC-004 | Licence MIT | Licence permissive gratuite autorisant l'usage commercial ; composants tiers conservent leurs licences. |
| DEC-005 | SQLite jusqu'à M9 inclus | Zéro service requis, portable ; PostgreSQL seulement si un besoin mesuré apparaît. |
| DEC-006 | Nom et e-mail Git locaux = miantsaaaa / fitimiantsa1@gmail.com | Valeurs explicitement demandées ; visibilité publique à considérer avant tout premier push. |
| DEC-007 | Aucun push avant v0.1.0 validée | Application non fonctionnelle complète à ce stade ; remote configuré uniquement. |
| DEC-008 | Branches main stable, dev intégration, feature locale ; hooks Git natifs | Conforme au workflow demandé ; aucune CI GitHub obligatoire. |
| DEC-009 | Apprentissage sans fine-tuning en V1 | Changements versionnés de knowledge/skills/exemples/configuration, réversible et compatible CPU. |
| DEC-010 | Pilotes proposés : Helpdesk L1 (HAUTE), QA automation (HAUTE), DevOps/cloud (HAUTE) | Couvre assistance, vérification et opérations ; DevOps en validation humaine. Sélection finale à confirmer avant M8 si le compromis métier diffère. |
| DEC-011 | Dépôt distant non vérifié pour visibilité/contenu ; aucun push autorisé actuellement | `gh` absent ; vérifier `git ls-remote` et visibilité avant v0.1.0. |

## En attente / PLANNED

Recommandation des modèles locaux adaptée à la mémoire matérielle non mesurée ; Ollama (MIT) ou llama.cpp (MIT) en options, modèles à choisir selon leur licence individuelle. Aucun modèle livré. Les hooks et la porte de release sont amorcés mais incomplets ; la release reste explicitement bloquée.