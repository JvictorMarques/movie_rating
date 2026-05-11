# Getting Started

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker + Docker Compose

## 1. Clone and install dependencies

```bash
git clone https://github.com/JvictorMarques/movie-rating
cd movie_rating
uv sync
```

## 2. Configure environment variables

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

```dotenv
# PostgreSQL connection
DB_USER=postgres
DB_PASSWORD=postgres
DB_DATABASE=movie_rating
DB_ADDRESS=localhost
DB_PORT=5432

# JWT — use a long random string (e.g. openssl rand -hex 32)
JWT_SECRET_KEY=your_secret_key_here
```

### Optional variables

| Variable | Default | Description |
|---|---|---|
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Token lifetime in minutes |

## 3. Start the database

```bash
docker compose up -d
```

This starts a PostgreSQL 16 container with a health check. The database name and credentials come from your `.env`.

## 4. Run migrations

```bash
uv run alembic upgrade head
```

This applies all migrations from the `migrations/` directory and creates the five tables: `users`, `movies`, `actors`, `users_movies`, `movies_actors`.

## 5. Start the development server

```bash
uv run task app
```

This command runs `lint_fix → format → mypy → test_check → docker compose up -d` before starting `fastapi dev app.py`.

The API will be available at `http://127.0.0.1:8000`.
Interactive docs: `http://127.0.0.1:8000/docs`

## Available tasks

| Command | Description |
|---|---|
| `uv run task lint` | Run ruff check |
| `uv run task lint_fix` | Auto-fix lint issues |
| `uv run task format` | Format code with ruff |
| `uv run task mypy` | Type-check `src/` |
| `uv run task test_check` | Run tests without coverage |
| `uv run task test` | Run tests with HTML coverage report |
| `uv run task app` | Full pre-flight + start dev server |

## Health check

```bash
curl http://127.0.0.1:8000/health
# {"message": "Hello World"}
```
