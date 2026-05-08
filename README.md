# Movie Rating API

![Python](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135%2B-009688?logo=fastapi)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![Version](https://img.shields.io/badge/version-1.0.0-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

A REST API for managing and rating movies, built with FastAPI and async SQLAlchemy. Users can register, movies can be created with a cast of actors, and each user can rate any movie on a scale from 0 to 10.

---

## Features

- **Authentication** — JWT-based login (`POST /api/v1/auth/token`) and token refresh; protected routes require a `Bearer` token
- **Users** — create, list, retrieve, update, and delete users (update/delete require ownership via JWT)
- **Movies** — create movies with director, synopsis, release date, and cast; list with optional filters by name and rating; update and delete
- **Ratings** — authenticated users can rate movies and update their existing ratings
- **Actors** — create, list, retrieve, update, and delete actors/actresses; linked to movies via a many-to-many relationship
- **Health check** — `GET /health` endpoint for liveness probes

---

## Technologies

| Layer | Technology |
|---|---|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| ORM | [SQLAlchemy 2.0](https://docs.sqlalchemy.org/) (async) |
| Database | PostgreSQL 16 |
| Validation | [Pydantic v2](https://docs.pydantic.dev/) |
| Authentication | [PyJWT](https://pyjwt.readthedocs.io/) (JWT Bearer tokens) |
| Password hashing | [pwdlib](https://github.com/frankie567/pwdlib) (Argon2) |
| Configuration | [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) |
| Migrations | [Alembic](https://alembic.sqlalchemy.org/) |
| Container | Docker + Docker Compose |
| Observability | OpenTelemetry SDK, Grafana, Mimir, Tempo, Loki |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| Linter / Formatter | [Ruff](https://docs.astral.sh/ruff/) |

---

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) — package and project manager
- Docker and Docker Compose — to run PostgreSQL

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/JvictorMarques/movie-rating.git
cd movie-rating
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

```env
ENVIRONMENT=development

DB_USER=postgres
DB_PASSWORD=postgres
DB_DATABASE=movie_rating
DB_ADDRESS=localhost
DB_PORT=5432

JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15

# Optional — omit or leave blank to disable telemetry
OTLP_ENDPOINT=http://localhost:4317
```

---

## Running the application

There are two ways to run the application, depending on the scenario. **Run only one at a time** — both bind to the same ports and will conflict if started simultaneously.

### Option 1 — Local development (`task app`)

Runs the FastAPI server locally with hot reload. Docker Compose is started automatically to provide PostgreSQL.

```bash
uv run task app
```

> The `app` task automatically runs lint, format, type checking, tests, starts the PostgreSQL container, and applies migrations before launching the server.

The API will be available at `http://localhost:8000`. Interactive docs are at `http://localhost:8000/docs`.

### Option 2 — Docker container (recommended for production simulation)

Spins up the entire stack — app, PostgreSQL, Grafana, Mimir, Tempo, Loki, and the OpenTelemetry Collector — all containerized. This is the closest environment to production and the recommended way to validate the full observability pipeline.

```bash
docker compose up -d
```

> Make sure `uv run task app` is not running before starting this option, as both expose the app on the same port.

All environment variables are read from your `.env` file. Grafana is available at `http://localhost:3000` (no login required).

---

## Observability

The project ships a full OpenTelemetry observability stack:

| Component | Role | Port |
|---|---|---|
| OpenTelemetry Collector | Receives traces/metrics/logs from the app; scrapes host metrics | 4317 (gRPC) |
| Grafana Mimir | Prometheus-compatible remote-write metrics storage | 9009 |
| Grafana Tempo | Distributed tracing backend | 3200 |
| Grafana Loki | Log aggregation | 3100 |
| Grafana | Unified dashboards for all signals | 3000 |

The app exports traces, metrics, and structured logs via OTLP gRPC to the collector. A custom `Middleware` layer records `http_request` (counter) and `http_request_duration` (histogram) per route, method, and status code. Host-level CPU, memory, disk, network, and filesystem metrics are scraped via the `hostmetrics` receiver.

A pre-built Grafana dashboard (`observability/grafana-dashboards/metrics.json`) is automatically provisioned on startup.

### Telemetry environment variable

| Variable | Required | Description |
|---|---|---|
| `OTLP_ENDPOINT` | No | gRPC endpoint of the OTel Collector (e.g. `http://localhost:4317`). If not set, telemetry setup is skipped entirely. |

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `ENVIRONMENT` | No | `development` | Deployment environment label |
| `DB_USER` | Yes | — | PostgreSQL username |
| `DB_PASSWORD` | Yes | — | PostgreSQL password |
| `DB_DATABASE` | Yes | — | Database name |
| `DB_ADDRESS` | Yes | — | Database host address |
| `DB_PORT` | Yes | 5432 | PostgreSQL port (typically `5432`) |
| `JWT_SECRET_KEY` | Yes | — | Secret key for signing JWT tokens |
| `JWT_ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | No | `15` | Token TTL in minutes |
| `OTLP_ENDPOINT` | No | — | OTel Collector gRPC endpoint (e.g. `http://localhost:4317`). If omitted, telemetry is disabled. |

---

## API Reference

All endpoints are prefixed with `/api/v1`. Endpoints marked 🔒 require a `Authorization: Bearer <token>` header.

### Auth — `/api/v1/auth`

```http
POST   /api/v1/auth/token          # Obtain a JWT access token
POST   /api/v1/auth/refresh_token  # Refresh token (🔒 requires valid token)
```

**Login — request body:**
```json
{
  "email": "john@example.com",
  "password": "secret"
}
```

**Response:**
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

---

### Users — `/api/v1/users`

```http
GET    /api/v1/users               # List all users (supports ?limit, ?offset, ?search_filter)
GET    /api/v1/users/{id}          # Get a user by ID
POST   /api/v1/users               # Create a user
PUT    /api/v1/users/{id}          # 🔒 Update a user (must own the account)
DELETE /api/v1/users/{id}          # 🔒 Delete a user (must own the account)
```

**Create user — request body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 28,
  "password": "secret"
}
```

---

### Movies — `/api/v1/movies`

```http
GET    /api/v1/movies              # List movies (supports ?limit, ?offset, ?name_filter, ?rating_filter)
GET    /api/v1/movies/{id}         # Get a movie by ID (includes cast and rating)
POST   /api/v1/movies              # Create a movie
PUT    /api/v1/movies/{id}         # Update a movie
DELETE /api/v1/movies/{id}         # Delete a movie
POST   /api/v1/movies/{id}/ratings # 🔒 Rate a movie
PUT    /api/v1/movies/{id}/ratings # 🔒 Update an existing rating
```

**Create movie — request body:**
```json
{
  "name": "Inception",
  "synopsis": "A thief who steals corporate secrets through dream-sharing technology.",
  "director": "Christopher Nolan",
  "release_date": "2010-07-16",
  "cast_ids": [1, 2]
}
```

**Rate a movie — request body:**
```json
{
  "rating": 9.5
}
```

> Rating must be between 0 (exclusive) and 10 (inclusive). The authenticated user is identified via the `Bearer` token.

---

### Actors — `/api/v1/actors`

```http
GET    /api/v1/actors              # List all actors (supports ?limit, ?offset, ?search_filter)
GET    /api/v1/actors/{id}         # Get an actor by ID
POST   /api/v1/actors              # Create an actor/actress
PUT    /api/v1/actors/{id}         # Update an actor/actress
DELETE /api/v1/actors/{id}         # Delete an actor/actress
```

**Create actor — request body:**
```json
{
  "name": "Leonardo DiCaprio",
  "age": 49
}
```

---

### Health Check

```http
GET /health
```

```json
{ "message": "Hello World" }
```

---

## Project Structure

```
movie-rating/
├── app.py                  # FastAPI application entry point
├── compose.yaml            # Docker Compose (full observability stack)
├── pyproject.toml          # Project metadata, dependencies, tool config
├── alembic.ini             # Alembic configuration
├── migrations/             # Alembic migration scripts
├── observability/
│   ├── otel-collector.yaml               # OTel Collector config (OTLP + hostmetrics)
│   ├── grafana-datasources.yaml          # Grafana datasource provisioning
│   ├── grafana-dashboard-provisioning.yaml
│   └── grafana-dashboards/
│       └── metrics.json                  # Pre-built HTTP metrics dashboard
├── scripts/
│   ├── load_test.py        # End-to-end load test (creates users, movies, ratings)
│   └── latency_sim.py      # Burst traffic simulator for p99 latency testing
├── src/
│   ├── core/
│   │   ├── database.py     # Async engine and session factory
│   │   ├── settings.py     # Environment-based config (pydantic-settings)
│   │   ├── security.py     # JWT creation/verification, password hashing
│   │   ├── telemetry.py    # OpenTelemetry SDK setup (traces, metrics, logs)
│   │   ├── metrics.py      # OTel meter instruments (http_request, http_request_duration)
│   │   ├── middleware.py   # Starlette middleware that records HTTP metrics
│   │   └── constants.py    # Shared error message strings
│   ├── models/
│   │   ├── base.py         # SQLAlchemy declarative base
│   │   ├── users.py
│   │   ├── movies.py
│   │   ├── actors.py
│   │   ├── users_movies.py # User ↔ Movie with rating
│   │   └── movies_actors.py
│   ├── repositories/       # Raw SQLAlchemy queries
│   │   ├── users.py
│   │   ├── movies.py
│   │   └── actors.py
│   ├── services/           # Business logic, raises HTTPException
│   │   ├── auth.py         # get_current_user dependency, ownership check
│   │   ├── users.py
│   │   ├── movies.py
│   │   └── actors.py
│   ├── routers/            # FastAPI route handlers
│   │   ├── auth.py         # POST /token, POST /refresh_token
│   │   ├── users.py
│   │   ├── movies.py
│   │   └── actors.py
│   └── schemas/            # Pydantic request/response models
│       ├── auth.py         # Token, LoginRequest
│       ├── common.py       # Shared type aliases (Age, Name, Rating)
│       ├── users.py
│       ├── movies.py
│       └── actors.py
└── tests/
    ├── conftest.py         # Fixtures (session, client)
    ├── test_auth.py
    ├── test_users.py
    ├── test_movies.py
    └── test_actors.py
```

---

## Scripts

The `scripts/` directory contains utilities for manual testing and observability validation. They require `httpx` (`uv add httpx` or install it separately) and a running API instance.

### Load test

Exercises the full API lifecycle — creates users, actors, and movies, authenticates each user, submits ratings, queries all resources, and fires intentional 4xx errors to populate error metrics.

```bash
uv run scripts/load_test.py
```

### Latency simulation

Sends bursts of requests with variable artificial delay to produce realistic p50/p99 latency distributions in Grafana dashboards.

```bash
uv run scripts/latency_sim.py
```

Both scripts target `http://localhost:8080/api/v1` by default.

---

## Running Tests

```bash
uv run task test
```

Generates an HTML coverage report at `htmlcov/index.html`.

---

## License

This project is licensed under the [MIT License](LICENSE).
