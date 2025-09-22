# TECHNOTES

- **Track:** Python (FastAPI, SQLModel, PostgreSQL)
- **Local Run:** `make run` (uses SQLite) or `docker-compose up --build`
- **Tests:** `make test` (PyTest + coverage >=70%)
- **Lint:** `make lint`
- **OpenAPI Export:** `make openapi`
- **CI:** `.github/workflows/ci.yml` (lint, tests+coverage artefact, pip-audit, docker build, OpenAPI artefact)

## Deviations & Assumptions
- CSV import expects `endpoints` and `tags` columns with semicolon-separated values.
- Authentication uses a single static bearer token sourced from `AUTH_TOKEN`.
- Alembic migrations omitted due to scoped timeframe; SQLModel auto-creates tables on startup.
- Pagination defaults: `limit=50`, `offset=0` (cap at 100) to cover suggested nice-to-have.
