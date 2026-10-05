# Skills

## Statut : TESTED (CRUD et relation agent-skill)

Les skills versionnées sont seedées depuis `data/seed/skills.json` et exposées par GET/POST/GET-ID/PUT/DELETE sous `/api/skills`. La relation plusieurs-à-plusieurs agent-skill est stockée dans `agent_skills`, avec liens idempotents. Benchmark dédié de compétence et progression sont PLANNED.