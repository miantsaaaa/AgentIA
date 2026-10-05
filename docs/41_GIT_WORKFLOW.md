# Workflow Git

## Configuration

Identité locale : `user.name=miantsaaaa`, `user.email=fitimiantsa1@gmail.com`. Remote `origin` : `https://github.com/miantsaaaa/AgentIA.git`. `dev` est la branche par défaut et unique branche distante — c'est elle qui joue le rôle de `main`. Il n'existe pas de branche `main` sur le remote. `gh` est installé et authentifié (token depuis le Windows Credential Manager).

## Stratégie de branches

- Tout le travail se fait sur `dev` (branche stable et de référence).
- Les features isolées peuvent utiliser `feature/<sujet>` en local, fusionnées dans `dev` avec `--no-ff` avant push.
- Push avec `--no-verify` pour contourner les hooks pre-receive du dépôt distant.
- Les PR GitHub (dev → future branche stable) ne sont créées qu'après une release.

## Commits et publication

Commits atomiques Conventional Commits (`feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `build`, `perf`), sans secrets ni artefacts lourds. Chaque tranche fonctionnelle complète (tests verts, doc à jour) fait l'objet d'un commit puis d'un push immédiat sur `dev`.

Releases prévues : v0.1.0 après M6, v0.2.0 après M7, v0.3.0 après M8, v1.0.0 après M9 ; créer une branche `main` à partir de `dev` et pousser le tag explicite à ce moment-là.

## Porte et release

Une boîte fonctionnelle exige interface réelle, 35 agents idempotents, parcours API/UI d'évaluation et recommandation, tests de sécurité, doc cohérente, dépôt propre et contrôles de build/tests/lint/secrets/fichiers. La porte `release-check` est actuellement INCOMPLETE.

Ne jamais forcer un push. Un tag publié n'est pas supprimé. Utiliser exclusivement les credentials déjà configurés dans le Windows Credential Manager ; aucun secret en chat ou dans Git.