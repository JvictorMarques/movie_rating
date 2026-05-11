# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository layout

The repo is a mono-repo with two top-level directories:

```
movie-rating/
├── app/                # FastAPI application (source, tests, migrations, scripts)
├── observability/      # OTel Collector, Grafana, Mimir, Tempo, Loki configs
├── compose.yaml        # Root orchestration — includes app/ and observability/ composes
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

## Observability

Config files live in `observability/` with one subdirectory per component:

```
observability/
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
