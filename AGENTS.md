# Règles de travail des agents

Ces règles s'appliquent à IAntsaM, aux agents spécialisés et aux contributeurs humains.

## Organisation du travail

1. Commencer par `git status`, le TODO et les fichiers propriétaires du comportement. Lire les modifications existantes avant d'éditer et ne jamais les écraser sans accord.
2. Formuler une hypothèse locale vérifiable et le test le moins coûteux qui peut l'infirmer.
3. Travailler en petites étapes cohérentes. Après chaque modification, exécuter immédiatement le test ciblé, puis élargir aux tests/lint nécessaires.
4. Une fonctionnalité n'est `TESTED` qu'après exécution réelle. Une panne ou une dépendance absente doit rester visible ; aucun résultat de modèle factice ne peut la masquer.
5. Synchroniser dans le même jalon le code, les tests, le contrat API, les documents concernés, `docs/33_TODO.md`, `CHANGELOG.md` et `docs/34_DECISIONS.md` si une décision évolue.
6. Après validation, créer un commit local Conventional Commit qui décrit précisément cette étape. Ne pas pousser une branche de travail ; aucune publication avant la porte de release.
7. Terminer chaque étape par un rapport concis : changements, commandes et résultats, limites restantes, hash du commit.

## Sécurité et limites

- Rester dans le workspace autorisé. Les agents utilisent leurs tools via le Permission Manager, jamais un accès direct au système.
- Refuser par défaut ; prévisualiser les changements de fichiers et exiger une approbation explicite avant toute écriture ou action à risque.
- Ne jamais demander, recevoir, journaliser ou transmettre au modèle un PIN Windows, mot de passe, jeton ou clé privée. Une élévation éventuelle relève d'une interface native du système, jamais d'un champ de chat.
- Le réseau et l'exécution de commandes hôte restent désactivés par défaut. Pas d'accès administrateur arbitraire.
- Le code applicatif et la documentation sont en français ; identifiants techniques en anglais.

## États

Employer exclusivement les états `CONCEPT`, `DESIGN`, `PLANNED`, `IMPLEMENTED`, `TESTED`, `PRODUCTION`. Pour les tâches, employer `TODO`, `IN_PROGRESS`, `BLOCKED`, `DONE`, `DEPRECATED`. Un statut décrit les preuves disponibles, pas l'intention.

## Rapport d'étape

Inclure le résultat des tests réellement exécutés, les éléments non vérifiés, les approbations encore nécessaires et le commit local créé. Ne jamais annoncer une release ou un push non exécuté.