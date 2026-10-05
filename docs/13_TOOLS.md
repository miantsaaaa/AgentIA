# Outils

## Statut : TESTED (tools initiaux)

Le registre d'exécution expose `file.read`, `filesystem.list`, `text.search`, `calculator` et `quant.paper_trade`. Le catalogue persistant versionné est seedé depuis `data/seed/tools.json` et administré sous `/api/tool-registry`. Une entrée personnalisée reste `executable=false` tant qu'aucun runner réel n'est enregistré ; les runners natifs ne peuvent être modifiés par ce CRUD. Le calcul utilise un AST restreint sans `eval`; les tools fichiers sont en lecture seule, confinés sous `AGENTIA_WORKSPACE_ROOT` et limités en taille/volume. Quant ne produit qu'un résultat `PAPER_ONLY`.