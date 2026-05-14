FROM python:3.13.13-alpine3.23 AS builder

ENV PATH="/app/.venv/bin:$PATH"
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
ARG USER=app

RUN apk add --no-cache curl=${CURL_VERSION} \
    && addgroup -S ${USER} \
    && adduser -S ${USER} -G ${USER}

WORKDIR /app

COPY --from=builder --chown=${USER}:${USER} /app /app

RUN rm alembic.ini \
    && rm -rf migrations

USER ${USER}

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["fastapi", "run", "app.py"]

FROM python:3.13.13-alpine3.23 AS migrations

ARG UV_VERSION=0.11.11 \
    GCC_VERSION=15.2.0-r2 \
    MUSL_VERSION=1.2.5-r23 \
    LINUX_HEADERS_VERSION=6.16.12-r0

RUN apk add --no-cache "gcc=${GCC_VERSION}" \
    "musl-dev=${MUSL_VERSION}" \
    "linux-headers=${LINUX_HEADERS_VERSION}" \
    && pip install uv==${UV_VERSION} --no-cache-dir

WORKDIR /app

COPY --from=builder /app /app

RUN uv sync --no-install-project --frozen

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["uv", "run", "alembic", "upgrade", "head"]
