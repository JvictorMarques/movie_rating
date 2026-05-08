# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All tasks are run via `taskipy` using `uv run`:

```bash
uv run task lint          # ruff check
uv run task lint_fix      # ruff check --fix
uv run task format        # ruff format (runs lint_fix after)
uv run task mypy          # mypy src/
uv run task test_check    # pytest -s -x -vv (no coverage)
uv run task test          # pytest -s -x --cov=src/ -vv (generates coverage HTML)
uv run task app           # fastapi dev app.py (runs lint_fix, format, mypy, test_check, docker compose up -d first)
```

Run a single test file:
```bash
uv run pytest tests/path/to/test_file.py -s -x -vv
```

## Architecture

The app is a FastAPI REST API (`app.py`) with routes mounted at `/api/v1/<resource>`. It uses async SQLAlchemy with PostgreSQL in production and SQLite in-memory for tests.

**Layer structure** (each resource follows this pattern):
- `src/routers/` — FastAPI route handlers; inject `AsyncSession` via `Depends(get_session)`
- `src/services/` — business logic; raise `HTTPException` for domain errors; call repository functions
- `src/repositories/` — raw SQLAlchemy queries; no HTTP concerns
- `src/schemas/` — Pydantic models for request/response validation; `common.py` holds shared type aliases (`Age`, `Name`, `Rating`)
- `src/models/` — SQLAlchemy ORM models; all inherit from `src/models/base.py`
- `src/core/` — `database.py` (engine + session factory), `settings.py` (env-based config via pydantic-settings), `security.py` (password hashing + JWT encode/decode), `constants.py` (shared error message strings)

**Data model overview:**
- `User` ↔ `Movie` via `UserMovie` (many-to-many with `rating` field)
- `Movie` ↔ `Actor` via `MovieActor` (many-to-many)
- Passwords are hashed with `pwdlib[argon2]`; stored as `str`, exposed as `SecretStr` in schemas

**Authentication** uses JWT (PyJWT). `src/core/security.py` handles token creation/verification and password hashing. `src/services/auth.py` exposes `get_current_user` (FastAPI dependency) and `verify_user_ownership`. Routes that mutate user data (`PUT`/`DELETE /api/v1/users/{id}`) and rating endpoints require a `Bearer` token. The `src/routers/auth.py` router provides `POST /token` and `POST /refresh_token`.

**Settings** are read from `.env` with these required vars: `DB_USER`, `DB_PASSWORD`, `DB_DATABASE`, `DB_ADDRESS`, `DB_PORT`, `JWT_SECRET_KEY`. Optional: `JWT_ALGORITHM` (default `HS256`), `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` (default `15`), `OTLP_ENDPOINT` (default `None` — if not set, `setup_telemetry` is not called and the app runs without telemetry).

**Tests** use `pytest-asyncio` with an in-memory SQLite engine. The `session` fixture creates/drops tables per test; the `client` fixture overrides `get_session` dependency via `app.dependency_overrides`. Tests live in `tests/`, fixtures in `tests/conftest.py`.

**Migrations** are managed with Alembic (`alembic.ini` at project root).

A `/health` GET endpoint is defined directly in `app.py` (not under `/api/v1`).

## Code style

- Ruff with `line-length = 79`, single quotes, preview mode
- `select = ['I', 'F', 'E', 'W', 'PL', 'PT']`; ignored: `PLR2004`, `PLR0917`, `PLR0913`
- mypy with `pydantic.mypy` plugin; check `src/` only
