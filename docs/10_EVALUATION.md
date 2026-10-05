# Évaluation

## Statut : TESTED (évaluateur minimal)

`POST /api/agents/{id}/evaluations` compare les compétences de la fiche à celles d'un benchmark JSON, conserve score/détails/résultat et journalise l'événement. Un résultat réussi sur le benchmark L1 crée un certificat N1 et change le statut en CERTIFIED ; un échec laisse l'agent N0. Ce premier évaluateur est déterministe et ne mesure que la présence de compétences, pas encore la précision, sécurité, autonomie, temps ni usage d'outils.