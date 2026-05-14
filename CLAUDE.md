# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository layout

The repo is a mono-repo with two top-level directories:

```
movie-rating/
├── app/                # FastAPI application (source, tests, migrations, scripts)
├── k8s/                # Kubernetes manifests (Helm chart + Helmfile)
├── docker/             # OTel Collector, Grafana, Mimir, Tempo, Loki configs
├── compose.yaml        # Root orchestration — includes app/ and docker/ composes
├── CHANGELOG.md
└── .pre-commit-config.yaml
```

All application work happens inside `app/`. All taskipy and uv commands must be run from `app/`.

## Commands

All tasks are run via `taskipy` using `uv run` **from the `app/` directory**:

```bash
uv run task lint          # ruff check
uv run task lint_fix      # ruff check --fix
uv run task format        # ruff format (runs lint_fix after)
uv run task mypy          # mypy src/
uv run task test_check    # pytest -s -x -vv (no coverage)
uv run task test          # pytest -s -x --cov=src/ -vv (generates coverage HTML)
uv run task app           # fastapi dev app.py (runs lint_fix, format, mypy, test_check, starts postgres via ../compose.yaml, applies migrations)
uv run task docs          # mkdocs serve -a 127.0.0.1:8001
```

Run a single test file:
```bash
uv run pytest tests/path/to/test_file.py -s -x -vv
```

The `pre_app` hook runs `docker compose -f ../compose.yaml up -d postgres --wait && alembic upgrade head` — it targets the root `compose.yaml`, not `app/compose.yaml`.

To bring up the full stack (app + observability) run from the repo root:
```bash
docker compose up -d
```

## Architecture

The app is a FastAPI REST API (`app/app.py`) with routes mounted at `/api/v1/<resource>`. It uses async SQLAlchemy with PostgreSQL in production and SQLite in-memory for tests.

**Layer structure** (each resource follows this pattern):
- `src/routers/` — FastAPI route handlers; inject `AsyncSession` via `Depends(get_session)`
- `src/services/` — business logic; raise `HTTPException` for domain errors; call repository functions; emit structured log messages (WARNING for conflicts/403s, INFO for mutations, DEBUG for lookups)
- `src/repositories/` — raw SQLAlchemy queries; no HTTP concerns
- `src/schemas/` — Pydantic models for request/response validation; `common.py` holds shared type aliases (`Age`, `Name`, `Rating`)
- `src/models/` — SQLAlchemy ORM models; all inherit from `src/models/base.py`
- `src/core/` — `database.py` (engine + session factory), `settings.py` (env-based config via pydantic-settings), `security.py` (password hashing + JWT encode/decode), `constants.py` (shared error message strings), `telemetry.py` (OTel SDK setup), `metrics.py` (OTel instruments), `middleware.py` (HTTP metrics middleware)

**Data model overview:**
- `User` ↔ `Movie` via `UserMovie` (many-to-many with `rating` field)
- `Movie` ↔ `Actor` via `MovieActor` (many-to-many)
- Passwords are hashed with `pwdlib[argon2]`; stored as `str`, exposed as `SecretStr` in schemas

**Authentication** uses JWT (PyJWT). `src/core/security.py` handles token creation/verification and password hashing. `src/services/auth.py` exposes `get_current_user` (FastAPI dependency) and `verify_user_ownership`. Routes that mutate user data (`PUT`/`DELETE /api/v1/users/{id}`) and rating endpoints require a `Bearer` token. The `src/routers/auth.py` router provides `POST /token` and `POST /refresh_token`.

**Settings** are read from `app/.env` with these required vars: `DB_USER`, `DB_PASSWORD`, `DB_DATABASE`, `DB_ADDRESS`, `DB_PORT`, `JWT_SECRET_KEY`. Optional: `ENVIRONMENT` (default `development` — controls log level: DEBUG in development, INFO otherwise), `JWT_ALGORITHM` (default `HS256`), `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` (default `15`), `OTLP_ENDPOINT` (default `None` — if not set, `setup_telemetry` is not called and the app runs without telemetry).

**Tests** use `pytest-asyncio` with an in-memory SQLite engine. The `session` fixture creates/drops tables per test; the `client` fixture overrides `get_session` dependency via `app.dependency_overrides`. Tests live in `app/tests/`, fixtures in `app/tests/conftest.py`.

**Migrations** are managed with Alembic (`app/alembic.ini`).

A `/health` GET endpoint is defined directly in `app/app.py` (not under `/api/v1`).

## Kubernetes

Config files live in `k8s/` — a Helm chart for the app plus a Helmfile that manages all releases.

```
k8s/
├── helmfile.yaml.gotmpl          # Helmfile — declares all releases (kong, goldilocks, movie-rating)
├── kind-config.yaml              # kind cluster config (1 control-plane + 2 workers, ports 80/443)
├── startup-cluster.sh            # Automated setup: creates cluster, builds/loads images, deploys, waits for health
├── movie-rating/                 # Helm chart for the app
│   ├── Chart.yaml                # Chart metadata; postgresql bitnami dependency (condition: local.enabled)
│   ├── values.yaml               # Default values (resources, image tags, secrets, ingress)
│   └── templates/
│       ├── _helpers.tpl          # Named templates: movie-rating.app.env, movie-rating.migrations.env
│       ├── app.yaml              # Deployment, Service, Ingress
│       ├── migrations.yaml       # Helm hook Job that runs alembic upgrade head
│       └── NOTES.txt
└── values/
    ├── kong.yaml                 # Kong ingress controller values
    └── goldilocks.yaml           # Goldilocks VPA recommender values
```

**Releases managed by Helmfile** (`helmfile -e local sync` from `k8s/`):
- `kong/kong` — Kong ingress controller (namespace `kong`)
- `goldilocks/goldilocks` — VPA resource recommender (namespace `goldilocks`); namespace `movie-rating` is labelled `goldilocks.fairwinds.com/enabled=true` via a `postsync` hook
- `movie-rating/movie-rating` — the app chart (namespace `movie-rating`); depends on kong and goldilocks in local env

**Helm chart details:**
- PostgreSQL is included as a bitnami dependency and only deployed when `local.enabled: true`
- Env vars are derived from `values.yaml` `secrets:` block via `_helpers.tpl` (camelCase keys → UPPER_SNAKE_CASE)
- `migrations.yaml` runs as a `pre-upgrade` Helm hook Job; it uses the `movie-rating-migrations` image whose ENTRYPOINT runs `alembic upgrade head` directly (build deps and `uv sync` are baked into the image at build time)
- The migration Job only runs on `helm upgrade`, not on `helm install` — on first install PostgreSQL is deployed as part of the chart resources and is not yet available when `pre-install` hooks fire

**Local setup (kind):**

```bash
# Create cluster
kind create cluster --config k8s/kind-config.yaml

# Load images into kind (must be done before helmfile sync)
kind load docker-image movie-rating:1.0.0
kind load docker-image movie-rating-migrations:1.0.0

# Deploy all releases
helmfile -e local sync -f k8s/helmfile.yaml.gotmpl

# Access the app
# Add to /etc/hosts: 127.0.0.1 movie-rating.local.com
curl http://movie-rating.local.com/health
```

## Observability

Config files live in `docker/` with one subdirectory per component:

```
docker/
├── compose.yaml
├── grafana/
│   ├── datasources.yaml       # Grafana datasource provisioning
│   ├── dashboards.yaml        # Grafana dashboard provisioning pointer
│   └── dashboards/
│       ├── metrics.json       # HTTP + DB pool metrics dashboard
│       └── logs.json          # Structured logs dashboard (tabbed: Errors/Warnings/Info)
├── loki/loki.yaml
├── mimir/mimir.yaml
├── otel/collector.yaml        # OTLP receiver + hostmetrics scraper
└── tempo/tempo.yaml
```

The app exports traces, metrics, and structured logs via OTLP gRPC to the collector. `src/core/middleware.py` records `http_request` (counter) and `http_request_duration` (histogram) per route/method/status.

## Code style

- Ruff with `line-length = 79`, single quotes, preview mode
- `select = ['I', 'F', 'E', 'W', 'PL', 'PT']`; ignored: `PLR2004`, `PLR0917`, `PLR0913`
- mypy with `pydantic.mypy` plugin; check `src/` only
- pre-commit hooks at repo root: trailing whitespace, EOF fixer, YAML check, ruff lint+format, mypy, pytest
