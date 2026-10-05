# Niveaux d'agents

## Statut : TESTED (N0→N1)

Les niveaux N0 à N7 représentent une autonomie certifiée. Le POST de création n'accepte pas le champ niveau et crée toujours un agent N0. Le benchmark `helpdesk-l1-foundations-v1` appelle Qwen3-4B via Ollama, puis vérifie la réponse générée et les compétences requises avant de délivrer N1. Ce parcours réel a été exécuté avec succès ; sans Ollama disponible il échoue en 503, sans certificat. Niveaux N2-N7 et catalogue complet de critères restent PLANNED.