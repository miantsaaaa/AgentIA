# Knowledge

## Statut : TESTED (proposition, évaluation et version)

Les packs conservent contenu, source, version, fiabilité, date de vérification et licence ; CRUD initial sous `/api/knowledge`, association explicite aux agents, propositions sous `/api/knowledge/{id}/proposals`, testées par génération Ollama, puis approbation humaine et historique de révisions. Une candidate ne modifie pas le contexte actif avant promotion ; une proposition obsolète est rejetée. La note actuelle est un score lexical de démonstration, pas une preuve de vérité factuelle. Aucune collecte Internet automatique n'est activée. Les sources tierces doivent avoir une provenance/licence compatible vérifiée avant approbation.