# Service Catalogue API

A FastAPI application for registering and discovering services across teams. The API exposes CRUD operations, filtering/search, CSV import, operational endpoints, metrics instrumentation, authentication, and an OpenAPI definition.

## Features
- RESTful CRUD for services with bearer-token auth
- Filter by owner team, tier, lifecycle, and free-text search over service name/tags
- Idempotent CSV import for bulk create/update
- Health, readiness, and Prometheus metrics endpoints
- SQLite (tests) and PostgreSQL (production/docker) support via SQLModel
- CI pipeline covering linting, tests & coverage, dependency audit, container build, and OpenAPI artifact

## Getting Started

### Prerequisites
- Python 3.13+
- `make` (optional but recommended)

### Installation
```bash
make install
```

### Running Locally
```bash
make run
```
The API is available at `http://localhost:8000`. Use the default token `change-me` in the `Authorization: Bearer` header.

### Running with Docker
```bash
docker-compose up --build
```
A PostgreSQL instance is provided and the API listens on port `8000`.

### Running Tests
```bash
make test
```
Generates coverage (target >=70%) for `src/svc_catalogue`.

### Linting & Formatting
```bash
make lint      # check
make format    # auto-format
```

### Export OpenAPI Specification
```bash
make openapi
```
Outputs `openapi.json` at the repository root.

## API Overview
- `POST /api/v1/services` create service
- `GET /api/v1/services` list services with filters: `owner_team`, `tier`, `lifecycle`, `search`, pagination (`offset`, `limit`)
- `GET /api/v1/services/{id}` fetch service
- `PUT /api/v1/services/{id}` update service
- `DELETE /api/v1/services/{id}` remove service
- `POST /api/v1/services/import` upload CSV (semicolon-separated `endpoints`/`tags` columns)
- `GET /health` liveness
- `GET /ready` readiness (verifies DB)
- `GET /metrics` Prometheus metrics

#### Example cURL
```bash
TOKEN=change-me
curl -X POST http://localhost:8000/api/v1/services \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "name": "service-a",
        "owner_team": "platform",
        "tier": "gold",
        "lifecycle": "production",
        "endpoints": ["https://service-a.internal"],
        "tags": ["payments", "critical"]
      }'
```

### CSV Import Format
Required headers: `name, owner_team, tier, lifecycle, endpoints, tags, id`. `endpoints` and `tags` accept semicolon-separated values. Leave `id` blank for new entries; matching by `name` ensures idempotent updates.

## Configuration
Environment variables (see `svc_catalogue/config.py`):
- `DATABASE_URL`
- `AUTH_TOKEN`
- `CSV_MAX_ROWS` (optional import guard)
- `ENVIRONMENT`

## Metrics and Observability
Metrics exposed at `/metrics` via `prometheus-fastapi-instrumentator`. Readiness checks run a simple SQL statement to validate DB connectivity.

## Project Layout
```
.
├── src/svc_catalogue             # Application package
├── tests                         # Unit and integration tests
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── ADR-0001.md
├── TECHNOTES.md
└── .github/workflows/ci.yml
```

## CSV Validation
Rows failing validation are reported in the response under `errors` with row numbers and messages. Successful rows are applied within a transaction per request.

## License
MIT
