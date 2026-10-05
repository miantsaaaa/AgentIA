# Stack gratuite

Licences déclarées par leurs projets amont ; compatibilité commerciale selon la licence standard. Les versions exactes résolues se trouvent dans l'environnement venv et seront figées par lockfiles lors de l'industrialisation.

| Dépendance | Version déclarée | Licence | Commercial | Usage | Alternative |
|---|---|---|---|---|---|
| Python | 3.11+ (local 3.14.3) | PSF | Oui | Backend | CPython libre |
| FastAPI | >=0.115,<1 | MIT | Oui | API | Starlette (BSD-3-Clause) |
| Pydantic | >=2.10,<3 | MIT | Oui | Validation | dataclasses + validation maison déconseillée |
| SQLAlchemy | >=2.0.36,<3 | MIT | Oui | ORM | sqlite3 standard |
| Alembic | >=1.14,<2 | MIT | Oui | Migrations (prévu) | scripts SQL versionnés |
| Uvicorn | >=0.34,<1 | BSD-3-Clause | Oui | Serveur ASGI | Hypercorn (MIT) |
| pytest | >=8.3,<9 | MIT | Oui | Tests | unittest standard |
| HTTPX | >=0.28,<1 | BSD-3-Clause | Oui | Tests API | urllib standard |
| Ruff | >=0.9,<1 | MIT | Oui | Lint | flake8 + Black |
| mypy | >=1.14,<2 | MIT | Oui | Typage (pas encore configuré) | Pyright |
| React / Vite / TypeScript / Tailwind | PLANNED | MIT / Apache-2.0 (TypeScript) | Oui | Frontend futur | Aucun |
| Mock model provider | interne | MIT du dépôt | Oui | Tests/démo | Aucun modèle requis |
| Ollama / llama.cpp | PLANNED, optionnels | MIT | Oui | Inférence locale future | Mock |
| Docker Engine / Podman | PLANNED, optionnels | Apache-2.0 (Podman) ; Docker Engine licence spécifique | Vérification requise | Sandbox future | Sandbox processus |

Versions précises, licences des dépendances transitives et modèles open-weight à vérifier lors du lockfile et avant tout usage redistribué. Aucun service payant ni modèle n'est requis actuellement.