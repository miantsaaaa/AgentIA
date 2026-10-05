# Permissions

## Statut : TESTED (contrôles de base)

Le Permission Manager refuse si aucun octroi explicite par agent/tool n'existe. Les actions CRITICAL créent `WAITING_APPROVAL`; leur approbation est liée à l'agent, l'outil et aux entrées exactes, puis consommée à l'exécution. Le kill switch bloque les actions, même autorisées. Les contrôles sont couverts par tests. L'API est prévue pour un usage local seulement et ne comporte pas encore d'authentification multi-utilisateur ; ne pas l'exposer au réseau.