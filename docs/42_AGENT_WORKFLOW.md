# Méthode de travail d'IAntsaM et des agents

## Statut : DESIGN (contrat de travail adopté)

IAntsaM est le coordinateur du workspace, pas un passe-droit de sécurité. Il découpe une demande en tâches traçables, choisit un agent avec la Smart Box, conserve le contexte utile, délègue les tâches bornées, puis rassemble leurs résultats.

Chaque tâche suit la même boucle :

1. Lire le TODO, l'état Git et les fichiers concernés ; préserver les changements en cours.
2. Reformuler le résultat attendu, une hypothèse testable et le contrôle qui la réfute.
3. Proposer un plan court pour les travaux multi-fichiers et désigner le responsable.
4. Modifier seulement le workspace autorisé, avec preview des diffs.
5. Exécuter les tests ciblés, corriger les échecs et synchroniser API/docs/TODO/CHANGELOG.
6. Après validation, créer un commit local atomique et rapporter hash, résultats et limites.

Les travaux indépendants peuvent être délégués, mais les changements concurrents sur les mêmes fichiers doivent être séquencés. Un agent ne peut ni certifier son propre niveau, ni contourner le Permission Manager, ni présenter une réponse de modèle synthétique comme une exécution réelle.

## PC et privilèges

Le PIN de déverrouillage Windows est un secret de l'utilisateur et ne sera jamais saisi dans l'IDE, envoyé à Ollama, stocké ou journalisé. Les permissions de l'application ne prouvent pas l'identité Windows. Si une opération exige des droits administrateur, l'application s'arrête et demande une action explicite via un mécanisme natif Windows ; aucun agent n'obtient une session administrateur permanente.

Le premier IDE n'écrit que dans les dossiers de workspace explicitement ouverts. Les modifications sont proposées sous forme de diff, puis appliquées après approbation. Terminal hôte, services, registre Windows, GUI et opérations hors workspace restent `PLANNED` et désactivés.

## État de reprise

Le tableau de bord des composants est `docs/43_IMPLEMENTATION_STATUS.md` ; le journal détaillé est `docs/33_TODO.md`, les jalons `docs/32_ROADMAP.md`, les décisions `docs/34_DECISIONS.md` et les preuves `docs/37_TESTING.md`. Le checker pre-commit vérifie que le registre existe et que ses statuts appartiennent à l'enum autorisé. Le dernier commit local constitue la base stable pour reprendre ; consulter `git log` et `git status` avant toute nouvelle intervention.