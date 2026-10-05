# Moteur de missions

## Statut : IMPLEMENTED (persistance et transitions)

`POST /api/missions` crée une mission persistée avec objectif, contexte et agents existants. `GET /api/missions` pagine et `POST /api/missions/{id}/transitions` applique la machine d'état documentée dans le service, avec historique `mission_events`. Les agents n'exécutent pas encore les missions ; plan d'actions, handoff, résultats et rapport sont PLANNED.