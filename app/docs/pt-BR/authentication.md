# Autenticação

A API usa **tokens JWT Bearer** (HS256). Os tokens são stateless — o servidor não armazena sessões.

## Endpoints

| Método | Path | Autenticação |
|---|---|---|
| `POST` | `/api/v1/auth/token` | Não |
| `POST` | `/api/v1/auth/refresh_token` | Sim (token válido) |

## Fluxo de login

```mermaid
sequenceDiagram
    participant C as Cliente
    participant R as Router
    participant S as Service (auth)
    participant Sec as Security
    participant DB as Banco de Dados

    C->>R: POST /token {email, password}
    R->>S: create_access_token(db, login_data)
    S->>DB: get_user_by_email(email)
    alt usuário não encontrado
        DB-->>S: None
        S-->>R: 401 Email ou senha incorretos
        R-->>C: 401 Unauthorized
    else usuário encontrado
        DB-->>S: linha User
        S->>Sec: verify_password(plain, hashed)
        alt senha errada
            Sec-->>S: False
            S-->>R: 401 Email ou senha incorretos
            R-->>C: 401 Unauthorized
        else senha correta
            Sec-->>S: True
            S->>Sec: create_access_token({sub: user.id})
            Sec-->>S: string JWT
            S-->>R: Token(access_token, token_type="bearer")
            R-->>C: 200 {access_token, token_type}
        end
    end
```

## Usando o token

Inclua o token no header `Authorization` para endpoints protegidos:

```
Authorization: Bearer <access_token>
```

## Fluxo de verificação do token

Todo route protegido usa `get_current_user` como dependência FastAPI:

```mermaid
sequenceDiagram
    participant C as Cliente
    participant R as Router
    participant S as Service (auth)
    participant Sec as Security
    participant DB as Banco de Dados

    C->>R: Requisição com Authorization: Bearer <token>
    R->>S: get_current_user(db, credentials)
    S->>Sec: verify_access_token(token)
    alt token expirado
        Sec-->>S: 401 Token expirado
        S-->>C: 401 Unauthorized
    else token inválido
        Sec-->>S: 401 Token inválido
        S-->>C: 401 Unauthorized
    else token válido
        Sec-->>S: payload {sub: user_id}
        S->>DB: get_user(user_id)
        alt usuário não encontrado
            DB-->>S: None
            S-->>C: 404 Not Found
        else usuário existe
            DB-->>S: User
            S-->>R: objeto User
            R->>R: continua o handler
        end
    end
```

## Refresh de token

O refresh emite um novo token sem precisar reenviar credenciais. O token atual deve ser válido (não expirado):

```mermaid
sequenceDiagram
    participant C as Cliente
    participant R as Router
    participant S as Service (auth)
    participant Sec as Security

    C->>R: POST /refresh_token (Bearer <token>)
    R->>S: get_current_user (dependência)
    note over S: valida o token — veja fluxo acima
    S-->>R: current_user
    R->>S: refresh_access_token(current_user)
    S->>Sec: create_access_token({sub: user.id})
    Sec-->>S: novo JWT
    S-->>R: Token
    R-->>C: 200 {access_token, token_type}
```

> **Decisão de design:** `refresh_access_token` exige um token válido (não expirado). Não existe um refresh token de longa duração; o cliente deve renovar antes que a janela de 15 minutos feche ou re-autenticar.

## Verificação de usuário dono de recurso

`PUT` e `DELETE` em `/api/v1/users/{id}` também chamam `verify_user_ownership`, que lança `403 Forbidden` se `current_user.id != user_id`. Isso impede que um usuário autenticado modifique a conta de outro usuário.

O mesmo vale para os endpoints de avaliação — apenas o usuário autenticado pode criar ou atualizar sua própria avaliação.

## Configuração do token

| Variável | Padrão | Descrição |
|---|---|---|
| `JWT_SECRET_KEY` | — (obrigatória) | Segredo HMAC para assinatura |
| `JWT_ALGORITHM` | `HS256` | Algoritmo de assinatura |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Tempo de vida do token |

Veja [Primeiros Passos](getting-started.md) para configurar essas variáveis.
