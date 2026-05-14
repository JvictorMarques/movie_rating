# Movie Rating API

![Python](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135%2B-009688?logo=fastapi)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-2.0-E92063?logo=pydantic&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-425CC7?logo=opentelemetry&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=white)
![Version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2FJvictorMarques%2Fmovie_rating%2Frefs%2Fheads%2Fmain%2Fapp%2Fpyproject.toml&query=%24.project.version&label=version&color=brightgreen)
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
| Kubernetes | [kind](https://kind.sigs.k8s.io/), [Helm](https://helm.sh/), [Helmfile](https://helmfile.readthedocs.io/), Kong, Goldilocks |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| Linter / Formatter | [Ruff](https://docs.astral.sh/ruff/) |

---

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) — package and project manager
- Docker and Docker Compose — to run PostgreSQL

**For Kubernetes (local):**
- [kind](https://kind.sigs.k8s.io/) — local Kubernetes clusters via Docker
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/docs/intro/install/)
- [Helmfile](https://helmfile.readthedocs.io/en/latest/#installation)

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/JvictorMarques/movie-rating.git
cd movie-rating
```

### 2. Enter the application directory and install dependencies

```bash
cd movie-rating/app
uv sync
```

### 3. Configure environment variables

Copy `app/.env.example` to `app/.env` and fill in the values:

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

There are three ways to run the application, depending on the scenario. **Run only one at a time** — options 1 and 2 bind to the same ports and will conflict if started simultaneously.

### Option 1 — Local development (`task app`)

Runs the FastAPI server locally with hot reload. Docker Compose is started automatically to provide PostgreSQL. Run from inside `app/`.

```bash
uv run task app
```

> The `app` task automatically runs lint, format, type checking, tests, starts the PostgreSQL container local `compose.yaml`, and applies migrations before launching the server.

The API will be available at `http://localhost:8000`. Interactive docs are at `http://localhost:8000/docs`.

### Option 2 — Docker container

Spins up the entire stack — app, PostgreSQL, Grafana, Mimir, Tempo, Loki, and the OpenTelemetry Collector — all containerized. Run from the **repo root**:

```bash
docker compose up -d
```

> Make sure `uv run task app` is not running before starting this option, as both expose the app on the same port.

All environment variables are read from `app/.env`. Grafana is available at `http://localhost:3000` (no login required).

### Option 3 — Kubernetes (kind) (recommended for production simulation)

Deploys the full application on a local [kind](https://kind.sigs.k8s.io/) cluster using Helm and Helmfile. Requires the prerequisites listed in the [Kubernetes section](#kubernetes-local) below.

> Before deploying, update `app.image.tag` and `migrations.image.tag` in `k8s/movie-rating/values.yaml` to match the image tag you will build.

```bash
# Create the cluster
kind create cluster --config k8s/kind-config.yaml

# Build and load images — replace <tag> with the value set in values.yaml
docker build -t movie-rating:<tag> app/
docker build --target builder -t movie-rating-migrations:<tag> app/
kind load docker-image movie-rating:<tag>
kind load docker-image movie-rating-migrations:<tag>

# Deploy all releases
helmfile -f k8s/helmfile.yaml.gotmpl -e local sync
```

Add the ingress host to your local DNS resolver and access the API:

```bash
echo "127.0.0.1  movie-rating.local.com" | sudo tee -a /etc/hosts
curl http://movie-rating.local.com/health
```

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

Two pre-built Grafana dashboards are automatically provisioned on startup:
- `docker/grafana/dashboards/metrics.json` — HTTP request metrics + database connection pool
- `docker/grafana/dashboards/logs.json` — structured logs with tabs for Errors, Warnings, and Info

### Telemetry environment variable

| Variable | Required | Description |
|---|---|---|
| `OTLP_ENDPOINT` | No | gRPC endpoint of the OTel Collector (e.g. `http://localhost:4317`). If not set, telemetry setup is skipped entirely. |

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `ENVIRONMENT` | No | `development` | Controls log level: `DEBUG` in development, `INFO` otherwise |
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
├── compose.yaml                # Root orchestration — includes app/ and docker/ composes
├── CHANGELOG.md
├── .pre-commit-config.yaml
├── app/                        # FastAPI application
│   ├── app.py                  # Entry point
│   ├── compose.yaml            # App + PostgreSQL + migrations services
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── migrations/             # Alembic migration scripts
│   ├── scripts/
│   │   ├── load_test.py        # End-to-end load test
│   │   └── latency_sim.py      # Burst traffic / p99 latency simulator
│   ├── src/
│   │   ├── core/
│   │   │   ├── database.py     # Async engine and session factory
│   │   │   ├── settings.py     # Environment-based config (pydantic-settings)
│   │   │   ├── security.py     # JWT creation/verification, password hashing
│   │   │   ├── telemetry.py    # OpenTelemetry SDK setup (traces, metrics, logs)
│   │   │   ├── metrics.py      # OTel meter instruments (http_request, http_request_duration)
│   │   │   ├── middleware.py   # Starlette middleware that records HTTP metrics
│   │   │   └── constants.py    # Shared error message strings
│   │   ├── models/
│   │   │   ├── base.py         # SQLAlchemy declarative base
│   │   │   ├── users.py
│   │   │   ├── movies.py
│   │   │   ├── actors.py
│   │   │   ├── users_movies.py # User ↔ Movie with rating
│   │   │   └── movies_actors.py
│   │   ├── repositories/       # Raw SQLAlchemy queries
│   │   │   ├── users.py
│   │   │   ├── movies.py
│   │   │   └── actors.py
│   │   ├── services/           # Business logic, raises HTTPException; emits structured logs
│   │   │   ├── auth.py         # get_current_user dependency, ownership check
│   │   │   ├── users.py
│   │   │   ├── movies.py
│   │   │   └── actors.py
│   │   ├── routers/            # FastAPI route handlers
│   │   │   ├── auth.py         # POST /token, POST /refresh_token
│   │   │   ├── users.py
│   │   │   ├── movies.py
│   │   │   └── actors.py
│   │   └── schemas/            # Pydantic request/response models
│   │       ├── auth.py         # Token, LoginRequest
│   │       ├── common.py       # Shared type aliases (Age, Name, Rating)
│   │       ├── users.py
│   │       ├── movies.py
│   │       └── actors.py
│   └── tests/
│       ├── conftest.py         # Fixtures (session, client)
│       ├── test_auth.py
│       ├── test_users.py
│       ├── test_movies.py
│       └── test_actors.py
└── docker/
    ├── compose.yaml
    ├── grafana/
    │   ├── datasources.yaml    # Grafana datasource provisioning
    │   ├── dashboards.yaml     # Grafana dashboard provisioning pointer
    │   └── dashboards/
    │       ├── metrics.json    # HTTP metrics + DB pool dashboard
    │       └── logs.json       # Structured logs dashboard (Errors/Warnings/Info tabs)
    ├── loki/loki.yaml
    ├── mimir/mimir.yaml
    ├── otel/collector.yaml     # OTLP receiver + hostmetrics scraper
    └── tempo/tempo.yaml
```

---

## Kubernetes (local)

The `k8s/` directory contains everything needed to run the application on a local [kind](https://kind.sigs.k8s.io/) cluster using [Helm](https://helm.sh/) and [Helmfile](https://helmfile.readthedocs.io/).

```
k8s/
├── kind-config.yaml              # kind cluster definition (1 control-plane + 2 workers, ports 80/443 mapped to host)
├── helmfile.yaml.gotmpl          # Helmfile with kong, goldilocks, and movie-rating releases
├── values/
│   ├── kong.yaml                 # Values for Kong Ingress Controller
│   └── goldilocks.yaml           # Values for Goldilocks (VPA recommendations)
└── movie-rating/                 # Application Helm chart
    ├── Chart.yaml                # Chart metadata; depends on Bitnami PostgreSQL 18.3.x
    ├── values.yaml               # Default values (local mode, image tags, resource requests/limits, ingress host)
    └── templates/
        ├── app.yaml              # Deployment + Service + Ingress
        ├── migrations.yaml       # pre-upgrade Job that runs Alembic migrations (local only)
        └── _helpers.tpl          # Template helpers for env var injection
```

### Prerequisites

- [kind](https://kind.sigs.k8s.io/) — local Kubernetes clusters via Docker
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/docs/intro/install/)
- [Helmfile](https://helmfile.readthedocs.io/en/latest/#installation)

### 1. Create the kind cluster

```bash
kind create cluster --config k8s/kind-config.yaml
```

### 2. Build the Docker images

The application uses a multi-stage Dockerfile. The **runtime** image is used by the API deployment; the **builder** stage is used as the migrations image (it retains `alembic.ini`, `migrations/`, and the full `uv` toolchain).

Run from the **repo root**, replacing `1.0.0` with the desired tag (must match `app.image.tag` and `migrations.image.tag` in `values.yaml`):

```bash
# Runtime image — used by the API Deployment
docker build -t movie-rating:1.0.0 app/

# Builder image — used by the migrations Job
docker build --target builder -t movie-rating-migrations:1.0.0 app/
```

### 3. Load the images into kind

kind clusters use their own container runtime, so images must be loaded explicitly:

```bash
kind load docker-image movie-rating:1.0.0
kind load docker-image movie-rating-migrations:1.0.0
```

### 4. Deploy with Helmfile

```bash
helmfile -f k8s/helmfile.yaml.gotmpl -e local sync
```

This installs:
- **Kong Ingress Controller** (`kong` namespace) — routes external traffic into the cluster
- **Goldilocks** (`goldilocks` namespace) — VPA-based resource recommendations
- **movie-rating** (`movie-rating` namespace) — the application chart, which includes PostgreSQL as a subchart and runs migrations as a pre-upgrade Job

> The application may take a few moments to become ready while the migration Job completes. Monitor progress with:
> ```bash
> kubectl get jobs -n movie-rating -w
> ```

### 5. Configure /etc/hosts

Add the Ingress host to your local DNS resolver:

```bash
echo "127.0.0.1  movie-rating.local.com" | sudo tee -a /etc/hosts
```

The API will then be available at `http://movie-rating.local.com/api/v1/`.

### Helm chart reference

| Value | Default | Description |
|---|---|---|
| `local.enabled` | `true` | Enables local-only resources (PostgreSQL subchart, migrations Job, env injection) |
| `app.image.tag` | `1.0.0` | Tag of the `movie-rating` runtime image |
| `app.ingress.host` | `movie-rating.local.com` | Ingress hostname |
| `app.ingress.className` | `kong` | Ingress class (Kong) |
| `migrations.image.tag` | `1.0.0` | Tag of the `movie-rating-migrations` builder image |
| `secrets.*` | see `values.yaml` | Database credentials and address injected as environment variables |

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

Both scripts target `http://localhost:8000/api/v1` by default and must be run from inside `app/`.

---

## Running Tests

From inside `app/`:

```bash
uv run task test
```

Generates an HTML coverage report at `app/htmlcov/index.html`.

---

## License

This project is licensed under the [MIT License](LICENSE).
