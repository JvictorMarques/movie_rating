# Primeiros Passos

## Pré-requisitos

- Python 3.13+
- Gerenciador de pacotes [uv](https://docs.astral.sh/uv/)
- Docker + Docker Compose

## 1. Clonar e instalar dependências

```bash
git clone https://github.com/JvictorMarques/movie-rating
cd movie_rating
uv sync
```

## 2. Configurar variáveis de ambiente

Copie `.env.example` para `.env` e preencha os valores:

```bash
cp .env.example .env
```

```dotenv
# Conexão PostgreSQL
DB_USER=postgres
DB_PASSWORD=postgres
DB_DATABASE=movie_rating
DB_ADDRESS=localhost
DB_PORT=5432

# JWT — use uma string longa e aleatória (ex: openssl rand -hex 32)
JWT_SECRET_KEY=sua_chave_secreta_aqui
```

### Variáveis opcionais

| Variável | Padrão | Descrição |
|---|---|---|
| `JWT_ALGORITHM` | `HS256` | Algoritmo de assinatura JWT |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Tempo de vida do token em minutos |

## 3. Iniciar o banco de dados

```bash
docker compose up -d
```

Isso sobe um container PostgreSQL 16 com health check. O nome do banco e as credenciais vêm do seu `.env`.

## 4. Executar as migrações

```bash
uv run alembic upgrade head
```

Aplica todas as migrações do diretório `migrations/` e cria as cinco tabelas: `users`, `movies`, `actors`, `users_movies`, `movies_actors`.

## 5. Iniciar o servidor de desenvolvimento

```bash
uv run task app
```

Esse comando executa `lint_fix → format → mypy → test_check → docker compose up -d` antes de iniciar o `fastapi dev app.py`.

A API ficará disponível em `http://127.0.0.1:8000`.
Documentação interativa: `http://127.0.0.1:8000/docs`

## Tasks disponíveis

| Comando | Descrição |
|---|---|
| `uv run task lint` | Executar ruff check |
| `uv run task lint_fix` | Corrigir problemas de lint automaticamente |
| `uv run task format` | Formatar código com ruff |
| `uv run task mypy` | Verificar tipos em `src/` |
| `uv run task test_check` | Executar testes sem cobertura |
| `uv run task test` | Executar testes com relatório HTML de cobertura |
| `uv run task app` | Pré-voo completo + iniciar servidor de desenvolvimento |

## Health check

```bash
curl http://127.0.0.1:8000/health
# {"message": "Hello World"}
```
