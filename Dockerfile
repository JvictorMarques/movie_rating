FROM python:3.13.13-alpine3.23 AS builder

ARG UV_VERSION=0.11.11

RUN pip install uv==${UV_VERSION} --no-cache-dir

WORKDIR /app

COPY pyproject.toml *.lock ./

RUN uv sync \
    --no-dev \
    --no-install-project \
    --frozen

COPY . .

FROM python:3.13.13-alpine3.23 AS runtime

ARG CURL_VERSION=8.17.0-r1

RUN apk add --no-cache curl=${CURL_VERSION} \
    && addgroup -S app \
    && adduser -S app -G app

WORKDIR /app

COPY --from=builder --chown=app:app /app /app

USER app

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["fastapi", "run", "app.py"]
