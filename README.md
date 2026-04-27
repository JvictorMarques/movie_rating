# Movie Rating API

![Python](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135%2B-009688?logo=fastapi)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![Version](https://img.shields.io/badge/version-0.6.0-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

A REST API for managing and rating movies, built with FastAPI and async SQLAlchemy. Users can register, movies can be created with a cast of actors, and each user can rate any movie on a scale from 0 to 10.

---

## Features

- **Users** — create, list, retrieve, update, and delete users
- **Movies** — create movies with director, synopsis, release date, and cast; list with optional filters by name and rating; update and delete
- **Ratings** — users can rate movies and update their existing ratings
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
| Password hashing | [pwdlib](https://github.com/frankie567/pwdlib) (Argon2) |
| Configuration | [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) |
| Migrations | [Alembic](https://alembic.sqlalchemy.org/) |
| Container | Docker + Docker Compose |
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

Create a `.env` file in the project root:

```env
DB_USER=postgres
DB_PASSWORD=postgres
DB_DATABASE=movie_rating
DB_ADRESS=localhost
DB_PORT=5432
```

### 4. Start the database

```bash
docker compose up -d
```

### 5. Run migrations

```bash
uv run alembic upgrade head
```

### 6. Start the development server

```bash
uv run task app
```

> The `app` task automatically runs lint, format, type checking, and starts Docker Compose before launching the server.

The API will be available at `http://localhost:8000`. Interactive docs are at `http://localhost:8000/docs`.

---

## Running with Docker

The `compose.yaml` at the project root spins up a PostgreSQL 16 container with a persistent volume. All environment variables are read from your `.env` file.

```bash
docker compose up -d
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `DB_USER` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_DATABASE` | Database name |
| `DB_ADRESS` | Database host address |
| `DB_PORT` | PostgreSQL port (typically `5432`) |

---

## API Reference

All endpoints are prefixed with `/api/v1`.

### Users — `/api/v1/users`

```http
GET    /api/v1/users               # List all users (supports ?limit, ?offset, ?search_filter)
GET    /api/v1/users/{id}          # Get a user by ID
POST   /api/v1/users               # Create a user
PUT    /api/v1/users/{id}          # Update a user (partial update supported)
DELETE /api/v1/users/{id}          # Delete a user
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
POST   /api/v1/movies/{id}/ratings # Rate a movie
PUT    /api/v1/movies/{id}/ratings # Update an existing rating
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

> Rating must be between 0 (exclusive) and 10 (inclusive). Pass `?current_user_id={id}` as a query parameter to identify the user.

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
├── compose.yaml            # Docker Compose (PostgreSQL)
├── pyproject.toml          # Project metadata, dependencies, tool config
├── alembic.ini             # Alembic configuration
├── migrations/             # Alembic migration scripts
├── src/
│   ├── core/
│   │   ├── database.py     # Async engine and session factory
│   │   └── settings.py     # Environment-based config (pydantic-settings)
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
│   │   ├── users.py
│   │   ├── movies.py
│   │   └── actors.py
│   ├── routers/            # FastAPI route handlers
│   │   ├── users.py
│   │   ├── movies.py
│   │   └── actors.py
│   └── schemas/            # Pydantic request/response models
│       ├── common.py       # Shared type aliases (Age, Name, Rating)
│       ├── users.py
│       ├── movies.py
│       └── actors.py
└── tests/
    ├── conftest.py         # Fixtures (session, client)
    ├── test_users.py
    ├── test_movies.py
    └── test_actors.py
```

---

## Running Tests

```bash
uv run task test
```

Generates an HTML coverage report at `htmlcov/index.html`.

---

## License

This project is licensed under the [MIT License](LICENSE).
