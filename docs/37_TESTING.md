# Tests et qualité

## Statut : TESTED (registre ciblé)

Commande backend : `python -m pytest` dans l'environnement virtuel du projet. Le premier résultat observé sous Python 3.14.3 est 3 tests réussis : health/seed idempotent (35 puis 0), niveau N0 non modifiable à la création, filtres et pagination. L'avertissement Starlette/httpx est sans échec mais devra être résolu en industrialisation.

`make release-check` et son script PowerShell ne sont pas encore des portes de release complètes et échouent volontairement tant que frontend et contrôles manquent.