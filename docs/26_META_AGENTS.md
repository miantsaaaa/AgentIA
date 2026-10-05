# Méta-agents

## Statut : IMPLEMENTED (IAntsaM initial)

IAntsaM est un `SystemAgent` distinct des 35 agents métier, seedé séparément. `POST /api/chat` appelle Ollama réellement et, pour IAntsaM, ajoute une recommandation déterministe justifiée. Il n'exécute pas de tools et n'a pas d'accès PC implicite. Plan d'actions, délégation multi-agent et orchestration restent PLANNED. Trainer/Evaluator autonomes et Research/Benchmark/Optimizer/Agent Architect restent futurs.