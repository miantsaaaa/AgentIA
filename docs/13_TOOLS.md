# Outils

## Statut : TESTED (tools initiaux)

Le registre expose `file.read`, `filesystem.list`, `text.search`, `calculator` et `quant.paper_trade`. Le calcul utilise un AST restreint sans `eval`; les tools fichiers sont en lecture seule, sous `AGENTIA_WORKSPACE_ROOT`, et limités en taille/volume. Quant ne produit qu'un résultat `PAPER_ONLY`. Les schémas détaillés, versions et licences de chaque tool restent à enrichir.