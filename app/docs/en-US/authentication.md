# Authentication

The API uses **JWT Bearer tokens** (HS256). Tokens are stateless — the server does not store sessions.

## Endpoints

| Method | Path | Auth required |
|---|---|---|
| `POST` | `/api/v1/auth/token` | No |
| `POST` | `/api/v1/auth/refresh_token` | Yes (valid token) |

## Login flow

```mermaid
sequenceDiagram
    participant C as Client
    participant R as Router
    participant S as Service (auth)
    participant Sec as Security
    participant DB as Database

    C->>R: POST /token {email, password}
    R->>S: create_access_token(db, login_data)
    S->>DB: get_user_by_email(email)
    alt user not found
        DB-->>S: None
        S-->>R: 401 Incorrect email or password
        R-->>C: 401 Unauthorized
    else user found
        DB-->>S: User row
        S->>Sec: verify_password(plain, hashed)
        alt wrong password
            Sec-->>S: False
            S-->>R: 401 Incorrect email or password
            R-->>C: 401 Unauthorized
        else password matches
            Sec-->>S: True
            S->>Sec: create_access_token({sub: user.id})
            Sec-->>S: JWT string
            S-->>R: Token(access_token, token_type="bearer")
            R-->>C: 200 {access_token, token_type}
        end
    end
```

## Using the token

Include the token in the `Authorization` header for protected endpoints:

```
Authorization: Bearer <access_token>
```

## Token verification flow

Every protected route uses `get_current_user` as a FastAPI dependency:

```mermaid
sequenceDiagram
    participant C as Client
    participant R as Router
    participant S as Service (auth)
    participant Sec as Security
    participant DB as Database

    C->>R: Request with Authorization: Bearer <token>
    R->>S: get_current_user(db, credentials)
    S->>Sec: verify_access_token(token)
    alt expired token
        Sec-->>S: 401 Token has expired
        S-->>C: 401 Unauthorized
    else invalid token
        Sec-->>S: 401 Invalid token
        S-->>C: 401 Unauthorized
    else valid token
        Sec-->>S: payload {sub: user_id}
        S->>DB: get_user(user_id)
        alt user not found
            DB-->>S: None
            S-->>C: 404 Not Found
        else user exists
            DB-->>S: User
            S-->>R: User object
            R->>R: continue handler
        end
    end
```

## Token refresh

Refreshing issues a new token without re-entering credentials. The current token must be valid (not expired):

```mermaid
sequenceDiagram
    participant C as Client
    participant R as Router
    participant S as Service (auth)
    participant Sec as Security

    C->>R: POST /refresh_token (Bearer <token>)
    R->>S: get_current_user (dependency)
    note over S: validates token — see flow above
    S-->>R: current_user
    R->>S: refresh_access_token(current_user)
    S->>Sec: create_access_token({sub: user.id})
    Sec-->>S: new JWT
    S-->>R: Token
    R-->>C: 200 {access_token, token_type}
```

> **Design note:** `refresh_access_token` requires a valid (non-expired) token. There is no long-lived refresh token; the client must refresh before the 15-minute window closes or re-authenticate.

## Ownership check

`PUT` and `DELETE` on `/api/v1/users/{id}` also call `verify_user_ownership`, which raises `403 Forbidden` if `current_user.id != user_id`. This prevents a logged-in user from modifying another user's account.

The same check applies to rating endpoints — only the authenticated user can create or update their own rating.

## Token configuration

| Setting | Default | Description |
|---|---|---|
| `JWT_SECRET_KEY` | — (required) | HMAC signing secret |
| `JWT_ALGORITHM` | `HS256` | Signing algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Token lifetime |

See [Getting Started](getting-started.md) for how to set these variables.
