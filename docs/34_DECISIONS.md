# Décisions

## Décisions prises

| ID | Décision | Motif / état |
|---|---|---|
| DEC-001 | Backend Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2, SQLite | Stack demandée ; Python 3.14.3 local, cible minimale 3.11. Migration initiale Alembic appliquée et testée. |
| DEC-002 | Données de seed versionnées en JSON | Standard intégré, diff lisible, pas de dépendance YAML. |
| DEC-003 | Ollama local comme provider réel initial ; aucun fallback factice | Ollama 0.35.1 et Qwen3-4B ont été exécutés localement. Les routes runtime/évaluation échouent clairement si Ollama est absent ; les fonctions indépendantes du modèle (registre, calcul, permissions) restent utilisables. |
| DEC-004 | Licence MIT | Licence permissive gratuite autorisant l'usage commercial ; composants tiers conservent leurs licences. |
| DEC-005 | SQLite jusqu'à M9 inclus | Zéro service requis, portable ; PostgreSQL seulement si un besoin mesuré apparaît. |
| DEC-006 | Nom et e-mail Git locaux = miantsaaaa / fitimiantsa1@gmail.com | Valeurs explicitement demandées ; visibilité publique à considérer avant tout premier push. |
| DEC-007 | Aucun push avant v0.1.0 validée | Application non fonctionnelle complète à ce stade ; remote configuré uniquement. |
| DEC-008 | Branches main stable, dev intégration, feature locale ; hooks Git natifs | Conforme au workflow demandé ; aucune CI GitHub obligatoire. |
| DEC-009 | Apprentissage sans fine-tuning en V1 | Changements versionnés de knowledge/skills/exemples/configuration, réversible et compatible CPU. |
| DEC-010 | Pilotes proposés : Helpdesk L1 (HAUTE), QA automation (HAUTE), DevOps/cloud (HAUTE) | Couvre assistance, vérification et opérations ; DevOps en validation humaine. Sélection finale à confirmer avant M8 si le compromis métier diffère. |
| DEC-011 | Dépôt distant non vérifié pour visibilité/contenu ; aucun push autorisé actuellement | `gh` absent ; vérifier `git ls-remote` et visibilité avant v0.1.0. |
| DEC-012 | Modèle par défaut Qwen3-4B sous Apache-2.0 | Ollama affiche `qwen3:4b`, ID local `359d7dd4bcda`; la carte officielle Qwen indique Apache-2.0. Génération locale observée ; utiliser un autre modèle implique de revalider sa licence et les benchmarks. |
| DEC-013 | Alembic est la source de vérité du schéma SQLite | `create_schema` applique `upgrade head`; un schéma complet non versionné est estampillé à head sans recréation. Un schéma partiel est refusé et demande une migration dédiée. Upgrade/downgrade et adoption sont testés. |
| DEC-014 | Le workflow des agents est contrôlé par `AGENTS.md` et un check local | Les changements sont petits, testés avant commit, synchronisés avec la doc et limités au workspace ; l'index documentaire et les dossiers requis sont vérifiés par lint, hook et porte de release. |

## En attente / PLANNED

Recommandation de modèles adaptés à plusieurs configurations matérielles reste à formaliser. Ollama et le modèle Qwen sont des installations locales, jamais versionnés dans Git. Les hooks et la porte de release sont amorcés mais incomplets ; la release reste explicitement bloquée.