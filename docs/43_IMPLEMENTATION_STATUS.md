# État de l'implémentation

> Source de vérité synthétique : ce qui existe, la preuve disponible et la suite attendue. Le détail des tâches reste dans `docs/33_TODO.md`. Toute modification de code doit mettre à jour ce registre dans le même commit.

État vérifié le 2026-10-05. Le dépôt est sur `dev`; aucune release ni aucun push n'a été effectué. Les états ont le sens défini dans `AGENTS.md` : ils décrivent des preuves, pas une intention.

## Tableau de bord

| Composant | Statut | Preuve disponible | Suite |
|---|---|---|---|
| Fondations et setup cross-platform | TESTED | Wrappers PowerShell/Git Bash setup/test/lint exécutés ; `.venv` local | Ajouter les contrôles de release complets |
| API agents et seed | TESTED | CRUD de base, filtres, pagination ; base vierge seedée 35 puis 0 | API d'activité consultable |
| Skills, tools, knowledge et Alembic | TESTED | CRUD/relations ; seeds 3/5/1 ; upgrade/downgrade, adoption legacy/backfill, évaluation Qwen, promotion versionnée et rejet des candidats périmés | Découverte de sources fiable/périodique, revue de licences et exercices ciblés |
| Cycle de vie agent | TESTED | Transitions autorisées/interdites vérifiées | Étendre les arcs selon le workflow complet |
| Versions, snapshots et rollback agent | PLANNED | Pas encore implémenté | Version candidate, comparaison et rollback |
| Certification N0 vers N1 | TESTED | Benchmark L1 exécuté avec Ollama/Qwen3-4B réel | Augmenter la couverture et la qualité des benchmarks |
| Certifications N2 à N7 | PLANNED | Aucun certificat livré à ces niveaux | Définir les benchmarks exigés par niveau |
| Permissions, audit et tools natifs | TESTED | Refus par défaut, approbation CRITICAL, kill switch, hash-chain et tests | Authentification et audit résistant à l'accès DB direct |
| Recommandation Smart Box | TESTED | Classement déterministe avec correspondances et manques | Comparaison multi-agent et workflows |
| Cycle de mission | TESTED | Persistance, événements et transitions invalides refusées | Exécuter les étapes et produire un rapport réel |
| Apprentissage knowledge | TESTED | Ollama évalue la candidate ; approbation versionne/révise ; runtime injecte uniquement les packs assignés ; évaluations périmées refusées | Extension aux skills/exercices, rollback de révision et veille sourcée |
| IAntsaM, chat local | TESTED | `POST /api/chat` exécuté avec Ollama/Qwen3 réel ; seed idempotent et recommandation Helpdesk vérifiés | Mémoire conversationnelle persistante, plan d'actions et orchestration multi-agent |
| Modifications de fichiers par IAntsaM | PLANNED | Le chat n'a aucun accès implicite au système de fichiers | IDE workspace-only, preview diff et approbation |
| Interface IDE et chat latéral | PLANNED | Aucun frontend n'est encore présent dans le dépôt | M6 : React, explorateur, éditeur, choix IAntsaM/agent |
| Sandbox et PC Gateway | PLANNED | Aucun accès terminal hôte ni élévation | LAB isolé, lecture workspace et preview uniquement |
| Orchestration et agents pilotes | PLANNED | Aucun workflow multi-agent livré | Exécuter une démo bornée à 3 agents |
| Industrialisation et release | PLANNED | Pas de release-check complet ni de tag | CI locale, tests UI, sauvegarde et porte v0.1.0 |

## Sécurité et limites

- IAntsaM utilise réellement le provider Ollama configuré ; il ne simule pas ses réponses. Une indisponibilité du modèle reste une erreur visible.
- Le chat ne lance pas de commande et ne modifie aucun fichier. Tout futur changement IDE devra être limité au workspace, présenté en diff et confirmé avant application.
- Le PIN Windows ne sera jamais demandé, reçu, stocké ou transmis au modèle. Les permissions applicatives ne constituent pas une authentification Windows ; toute élévation relève exclusivement d'une interface native contrôlée par l'utilisateur.
- La détection d'un projet, le changement de thème ou toute opération PC ne sont pas prétendus disponibles tant qu'un outil réel et ses tests ne sont pas livrés.

## Reprise

Commencer par `git status`, `git log -5`, puis lire `docs/33_TODO.md`. Prochaine tranche fonctionnelle : IDE local réel (sélection IAntsaM/agent, explorateur de workspace et propositions de diff), sans terminal hôte. M1 conserve une tâche ouverte pour l'API de consultation d'activité. L'IDE, l'édition de fichiers par IAntsaM et les actions PC ne sont pas encore livrés.