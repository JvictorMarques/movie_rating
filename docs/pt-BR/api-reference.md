# Referência da API

URL base: `/api/v1`

Todos os corpos de request e response usam `application/json`. Rotas protegidas requerem `Authorization: Bearer <token>` — veja [Autenticação](authentication.md).

---

## Auth

### `POST /auth/token`

Autentica e recebe um token de acesso JWT.

**Autenticação:** Nenhuma

**Corpo da requisição:**

```json
{
  "email": "usuario@exemplo.com",
  "password": "senhasecreta"
}
```

**Resposta `200`:**

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

**Erros:** `401` — email ou senha incorretos.

---

### `POST /auth/refresh_token`

Emite um novo token para o usuário autenticado.

**Autenticação:** Bearer token (deve ser válido, não expirado)

**Corpo da requisição:** Nenhum

**Resposta `200`:** Mesmo formato de `/token`.

---

## Usuários

### `GET /users/`

Lista usuários com paginação e busca opcional por nome.

**Autenticação:** Nenhuma

**Parâmetros de query:**

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `limit` | int (1–100) | 100 | Máximo de registros a retornar |
| `offset` | int (≥0) | 0 | Número de registros a pular |
| `search_filter` | string | — | Filtrar por nome (correspondência parcial) |

**Resposta `200`:**

```json
{
  "users": [
    {
      "id": 1,
      "name": "Alice",
      "email": "alice@exemplo.com",
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

Retorna um usuário pelo ID.

**Autenticação:** Nenhuma

**Resposta `200`:** Objeto de usuário único (mesmo formato do item da lista acima).

**Erros:** `404` — usuário não encontrado.

---

### `POST /users/`

Cria um novo usuário.

**Autenticação:** Nenhuma

**Corpo da requisição:**

```json
{
  "name": "Alice",
  "email": "alice@exemplo.com",
  "age": 30,
  "password": "senhasecreta"
}
```

Regras de validação: `name` ≥ 2 caracteres; `age` entre 1 e 150; `password` ≥ 8 caracteres.

**Resposta `201`:** Objeto do usuário criado (senha excluída da resposta).

**Erros:** `400` — email já cadastrado.

---

### `PUT /users/{user_id}`

Atualiza dados do usuário. Todos os campos são opcionais.

**Autenticação:** Bearer token; o dono do token deve corresponder ao `user_id`.

**Corpo da requisição (todos opcionais):**

```json
{
  "name": "Alice Atualizada",
  "email": "novoemail@exemplo.com",
  "age": 31,
  "password": "novasenha"
}
```

**Resposta `200`:** Objeto do usuário atualizado.

**Erros:** `401` — sem/token inválido; `403` — token pertence a outro usuário; `404` — usuário não encontrado.

---

### `DELETE /users/{user_id}`

Deleta um usuário e todas as suas avaliações (cascade).

**Autenticação:** Bearer token; o dono do token deve corresponder ao `user_id`.

**Resposta `204`:** Sem conteúdo.

**Erros:** `401`, `403`, `404`.

---

## Filmes

### `GET /movies/`

Lista filmes com paginação, filtro de nome e filtro de avaliação.

**Autenticação:** Nenhuma

**Parâmetros de query:**

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `limit` | int (1–100) | 100 | Máximo de registros |
| `offset` | int (≥0) | 0 | Registros a pular |
| `name_filter` | string | — | Filtrar por nome do filme |
| `rating_filter` | float | — | Filtrar por avaliação exata |

**Resposta `200`:**

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

Retorna um filme com elenco e avaliação média.

**Autenticação:** Nenhuma

**Resposta `200`:** Objeto de filme único (mesmo formato do item da lista acima).

**Erros:** `404` — filme não encontrado.

---

### `POST /movies/`

Cria um filme e opcionalmente associa atores.

**Autenticação:** Nenhuma

**Corpo da requisição:**

```json
{
  "name": "Inception",
  "synopsis": "Um ladrão que rouba segredos corporativos...",
  "director": "Christopher Nolan",
  "release_date": "2010-07-16",
  "cast_ids": [1, 2]
}
```

`cast_ids` é opcional. Cada ID deve referenciar um ator existente.

**Resposta `201`:** Filme criado com elenco.

---

### `PUT /movies/{movie_id}`

Atualiza dados do filme. Todos os campos são opcionais.

**Autenticação:** Nenhuma

**Corpo da requisição (todos opcionais):**

```json
{
  "name": "Inception",
  "synopsis": "Sinopse atualizada",
  "director": "C. Nolan",
  "release_date": "2010-07-16",
  "cast_ids": [1, 3]
}
```

**Resposta `200`:** Filme atualizado.

---

### `DELETE /movies/{movie_id}`

Deleta um filme e todas as avaliações e vínculos de elenco associados (cascade).

**Autenticação:** Nenhuma

**Resposta `204`:** Sem conteúdo.

---

### `POST /movies/{movie_id}/ratings`

Avalia um filme como o usuário autenticado. Cada usuário pode avaliar um filme apenas uma vez.

**Autenticação:** Bearer token

**Corpo da requisição:**

```json
{
  "rating": 8.5
}
```

`rating` deve estar entre 0 (exclusivo) e 10 (inclusivo).

**Resposta `201`:**

```json
{
  "user_id": 1,
  "movie_id": 5,
  "rating": 8.5,
  "created_at": "...",
  "updated_at": "..."
}
```

**Erros:** `401` — não autenticado; `404` — filme não encontrado; `400` — já avaliado.

---

### `PUT /movies/{movie_id}/ratings`

Atualiza uma avaliação existente.

**Autenticação:** Bearer token

**Corpo da requisição:** Mesmo formato de `POST /ratings`.

**Resposta `200`:**

```json
{
  "user_id": 1,
  "movie_id": 5,
  "rating": 9.0,
  "updated_at": "..."
}
```

**Erros:** `401`; `404` — filme não encontrado ou avaliação não existe.

---

## Atores

### `GET /actors/`

Lista atores com paginação e busca por nome.

**Autenticação:** Nenhuma

**Parâmetros de query:**

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `limit` | int (1–100) | 100 | Máximo de registros |
| `offset` | int (≥0) | 0 | Registros a pular |
| `search_filter` | string | — | Filtrar por nome |

**Resposta `200`:**

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

Retorna um ator pelo ID.

**Autenticação:** Nenhuma

**Resposta `200`:** Objeto de ator único.

**Erros:** `404` — ator não encontrado.

---

### `POST /actors/`

Cria um ator.

**Autenticação:** Nenhuma

**Corpo da requisição:**

```json
{
  "name": "Leonardo DiCaprio",
  "age": 49
}
```

**Resposta `201`:** Ator criado.

---

### `PUT /actors/{actor_id}`

Atualiza dados do ator. Todos os campos são opcionais.

**Autenticação:** Nenhuma

**Corpo da requisição:**

```json
{
  "name": "Leo DiCaprio",
  "age": 50
}
```

**Resposta `200`:** Ator atualizado.

---

### `DELETE /actors/{actor_id}`

Deleta um ator e todas as suas associações com filmes.

**Autenticação:** Nenhuma

**Resposta `204`:** Sem conteúdo.
