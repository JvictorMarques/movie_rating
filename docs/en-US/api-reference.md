# API Reference

Base URL: `/api/v1`

All request and response bodies use `application/json`. Protected routes require `Authorization: Bearer <token>` — see [Authentication](authentication.md).

---

## Auth

### `POST /auth/token`

Authenticate and receive a JWT access token.

**Auth:** None

**Request body:**

```json
{
  "email": "user@example.com",
  "password": "secretpassword"
}
```

**Response `200`:**

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

**Errors:** `401` — incorrect email or password.

---

### `POST /auth/refresh_token`

Issue a new token for the currently authenticated user.

**Auth:** Bearer token (must be valid, not expired)

**Request body:** None

**Response `200`:** Same shape as `/token`.

---

## Users

### `GET /users/`

List users with pagination and optional name search.

**Auth:** None

**Query parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `limit` | int (1–100) | 100 | Max records to return |
| `offset` | int (≥0) | 0 | Number of records to skip |
| `search_filter` | string | — | Filter by name (partial match) |

**Response `200`:**

```json
{
  "users": [
    {
      "id": 1,
      "name": "Alice",
      "email": "alice@example.com",
      "age": 30,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "limit": 100,
  "offset": 0
}
```

---

### `GET /users/{user_id}`

Get a single user by ID.

**Auth:** None

**Response `200`:** Single user object (same shape as list item above).

**Errors:** `404` — user not found.

---

### `POST /users/`

Create a new user.

**Auth:** None

**Request body:**

```json
{
  "name": "Alice",
  "email": "alice@example.com",
  "age": 30,
  "password": "secretpassword"
}
```

Validation rules: `name` ≥ 2 chars; `age` between 1 and 150; `password` ≥ 8 chars.

**Response `201`:** Created user object (password excluded from response).

**Errors:** `400` — email already registered.

---

### `PUT /users/{user_id}`

Update user data. All fields are optional.

**Auth:** Bearer token; token owner must match `user_id`.

**Request body (all fields optional):**

```json
{
  "name": "Alice Updated",
  "email": "newemail@example.com",
  "age": 31,
  "password": "newpassword"
}
```

**Response `200`:** Updated user object.

**Errors:** `401` — no/invalid token; `403` — token belongs to a different user; `404` — user not found.

---

### `DELETE /users/{user_id}`

Delete a user and all their ratings (cascade).

**Auth:** Bearer token; token owner must match `user_id`.

**Response `204`:** No content.

**Errors:** `401`, `403`, `404`.

---

## Movies

### `GET /movies/`

List movies with pagination, name filter, and rating filter.

**Auth:** None

**Query parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `limit` | int (1–100) | 100 | Max records |
| `offset` | int (≥0) | 0 | Records to skip |
| `name_filter` | string | — | Filter by movie name |
| `rating_filter` | float | — | Filter by exact rating |

**Response `200`:**

```json
{
  "movies": [
    {
      "id": 1,
      "name": "Inception",
      "synopsis": "...",
      "director": "Christopher Nolan",
      "release_date": "2010-07-16",
      "rating": 9.2,
      "cast": [{"id": 1, "name": "Leonardo DiCaprio", "age": 49}],
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "limit": 100,
  "offset": 0
}
```

---

### `GET /movies/{movie_id}`

Get a single movie with cast and average rating.

**Auth:** None

**Response `200`:** Single movie object (same shape as list item above).

**Errors:** `404` — movie not found.

---

### `POST /movies/`

Create a movie and optionally associate actors.

**Auth:** None

**Request body:**

```json
{
  "name": "Inception",
  "synopsis": "A thief who steals corporate secrets...",
  "director": "Christopher Nolan",
  "release_date": "2010-07-16",
  "cast_ids": [1, 2]
}
```

`cast_ids` is optional. Each ID must reference an existing actor.

**Response `201`:** Created movie with cast.

---

### `PUT /movies/{movie_id}`

Update movie data. All fields optional.

**Auth:** None

**Request body (all fields optional):**

```json
{
  "name": "Inception",
  "synopsis": "Updated synopsis",
  "director": "C. Nolan",
  "release_date": "2010-07-16",
  "cast_ids": [1, 3]
}
```

**Response `200`:** Updated movie.

---

### `DELETE /movies/{movie_id}`

Delete a movie and all associated ratings and cast links (cascade).

**Auth:** None

**Response `204`:** No content.

---

### `POST /movies/{movie_id}/ratings`

Rate a movie as the authenticated user. A user can only rate each movie once.

**Auth:** Bearer token

**Request body:**

```json
{
  "rating": 8.5
}
```

`rating` must be between 0 (exclusive) and 10 (inclusive).

**Response `201`:**

```json
{
  "user_id": 1,
  "movie_id": 5,
  "rating": 8.5,
  "created_at": "...",
  "updated_at": "..."
}
```

**Errors:** `401` — not authenticated; `404` — movie not found; `400` — already rated.

---

### `PUT /movies/{movie_id}/ratings`

Update an existing rating.

**Auth:** Bearer token

**Request body:** Same as `POST /ratings`.

**Response `200`:**

```json
{
  "user_id": 1,
  "movie_id": 5,
  "rating": 9.0,
  "updated_at": "..."
}
```

**Errors:** `401`; `404` — movie not found or rating does not exist.

---

## Actors

### `GET /actors/`

List actors with pagination and name search.

**Auth:** None

**Query parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `limit` | int (1–100) | 100 | Max records |
| `offset` | int (≥0) | 0 | Records to skip |
| `search_filter` | string | — | Filter by name |

**Response `200`:**

```json
{
  "actors": [
    {"id": 1, "name": "Leonardo DiCaprio", "age": 49, "created_at": "...", "updated_at": "..."}
  ],
  "limit": 100,
  "offset": 0
}
```

---

### `GET /actors/{actor_id}`

Get a single actor by ID.

**Auth:** None

**Response `200`:** Single actor object.

**Errors:** `404` — actor not found.

---

### `POST /actors/`

Create an actor.

**Auth:** None

**Request body:**

```json
{
  "name": "Leonardo DiCaprio",
  "age": 49
}
```

**Response `201`:** Created actor.

---

### `PUT /actors/{actor_id}`

Update actor data. All fields optional.

**Auth:** None

**Request body:**

```json
{
  "name": "Leo DiCaprio",
  "age": 50
}
```

**Response `200`:** Updated actor.

---

### `DELETE /actors/{actor_id}`

Delete an actor and all their movie associations.

**Auth:** None

**Response `204`:** No content.
