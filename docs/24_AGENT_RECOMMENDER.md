# Recommandation

## Statut : TESTED (moteur déterministe)

`POST /api/recommendations` normalise les mots, compare demande aux noms, domaines, descriptions et compétences, pondère niveau/statut et retourne scores, termes correspondants, justification et lacunes. Ce chemin est déterministe et testé sans génération artificielle. L'orchestration multi-agent et l'amélioration optionnelle par LLM sont PLANNED.