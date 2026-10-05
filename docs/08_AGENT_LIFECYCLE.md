# Cycle de vie

## Statut : IMPLEMENTED (transitions partielles)

Transitions permises par l'API : DRAFT→TRAINING, TRAINING→DRAFT/EVALUATION, EVALUATION→TRAINING, CERTIFIED→AVAILABLE, AVAILABLE→PRODUCTION/TRAINING, PRODUCTION→IMPROVEMENT, IMPROVEMENT→TRAINING. Toute autre transition répond 409 et chaque transition permise ajoute un événement d'activité. CERTIFIED est atteint par l'évaluateur uniquement. Snapshots, branche d'apprentissage et promotion versionnée restent PLANNED.