# Workflow Git

## Configuration

Identité locale uniquement : `user.name=miantsaaaa`, `user.email=fitimiantsa1@gmail.com`. Remote `origin` : `https://github.com/miantsaaaa/AgentIA.git`. `main` est stable, `dev` intègre le travail, `feature/<jalon>-<sujet>` porte les changements. Les branches de travail restent locales. Fusionner avec `--no-ff`.

## Commits et publication

Commits atomiques Conventional Commits (`feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `build`, `perf`), sans secrets ni artefacts lourds. Aucun push avant une version fonctionnelle complète. Releases prévues : v0.1.0 après M6, v0.2.0 après M7, v0.3.0 après M8, v1.0.0 après M9 ; pousser uniquement `main` puis le tag explicite.

## Porte et release

Une boîte fonctionnelle exige interface réelle, 35 agents idempotents, parcours API/UI d'évaluation et recommandation, tests de sécurité, doc cohérente, dépôt propre et contrôles de build/tests/lint/secrets/fichiers. La porte `release-check` est actuellement INCOMPLETE et configurée pour échouer : aucun release ni push ne peut être revendiqué.

Avant la première release, vérifier contenu et visibilité distants via `git ls-remote origin` et une source GitHub. Si l'historique distant existe, l'intégrer sans écrasement ; arrêter en cas de conflit non trivial. Ne jamais forcer un push. Un tag publié n'est pas supprimé. Utiliser exclusivement les credentials déjà configurés ; aucun secret en chat ou dans Git. `gh` n'est pas installé. L'adresse e-mail de commits demandée peut être visible si le dépôt est public.