FROM python:3.13-alpine3.23 AS builder

RUN apk add --no-cache build-base cargo rust \
    && pip install uv --no-cache-dir

WORKDIR /app

COPY pyproject.toml *.lock ./

RUN uv sync --no-dev --no-install-project --frozen

COPY . .

FROM python:3.13-alpine3.23 AS runtime

RUN apk add --no-cache curl \
    && addgroup -S app \
    && adduser -S app -G app

WORKDIR /app

COPY --from=builder --chown=app:app /app /app

USER app

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["fastapi", "run", "app.py"]
