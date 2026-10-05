# Évaluation

## Statut : TESTED (évaluateur minimal)

`POST /api/agents/{id}/evaluations` vérifie d'abord les compétences requises, appelle ensuite le vrai modèle local Ollama, conserve la réponse finale (hors blocs `<think>`), calcule les critères du benchmark et journalise résultat et score. Un résultat réussi sur le benchmark L1 crée un certificat N1 ; une indisponibilité modèle répond 503 sans certificat. Cette première grille mesure des critères textuels, la sécurité lexicale et les compétences déclarées ; elle ne prétend pas mesurer complètement précision, autonomie ou qualité métier.