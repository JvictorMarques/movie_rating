# Movie Rating API

A REST API for rating movies, built with **FastAPI** and **async SQLAlchemy**.

## Tech stack

| Layer | Technology |
|---|---|
| Web framework | [FastAPI](https://fastapi.tiangolo.com/) |
| ORM | SQLAlchemy 2.x (async) |
| Database | PostgreSQL (production) / SQLite in-memory (tests) |
| Migrations | Alembic |
| Settings | pydantic-settings |
| Password hashing | pwdlib[argon2] |
| Authentication | PyJWT (HS256) |
| Validation | Pydantic v2 |

## Data model

The diagram below shows all five database tables and their relationships.

```mermaid
erDiagram
    users {
        int id PK
        string name
        string email UK
        int age
        string password
        datetime created_at
        datetime updated_at
    }
    movies {
        int id PK
        string name UK
        string synopsis
        string director
        date release_date
        datetime created_at
        datetime updated_at
    }
    actors {
        int id PK
        string name UK
        int age
        datetime created_at
        datetime updated_at
    }
    users_movies {
        int user_id FK
        int movie_id FK
        float rating
        datetime created_at
        datetime updated_at
    }
    movies_actors {
        int movie_id FK
        int actor_id FK
        datetime created_at
        datetime updated_at
    }
    users ||--o{ users_movies : "rates"
    movies ||--o{ users_movies : "rated by"
    movies ||--o{ movies_actors : "features"
    actors ||--o{ movies_actors : "appears in"
```

## Explore the docs

- [Getting Started](getting-started.md) — run the project locally
- [Architecture](architecture.md) — layers, request lifecycle, and core modules
- [Authentication](authentication.md) — JWT flow and token usage
- [Database](database.md) — tables, constraints, and cascade rules
- [API Reference](api-reference.md) — all endpoints with request/response details
