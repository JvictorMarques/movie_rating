## v1.2.0 (2026-05-11)

### Refactor

- **repo**: restructure project into mono-repo layout with `app/` and `observability/` as top-level directories

### Improvements

- **settings**: add JWT secret validation on startup and expose settings singleton for reuse across the codebase
- **compose**: extract dedicated `migrations` service and `db-env` anchor to avoid environment variable duplication
- **docker**: strip migrations from final image, export venv PATH, pin `uv` and `curl` versions, and parameterize image user
- **readme**: version badge now reads dynamically from `pyproject.toml`
- **commitizen**: add `.cz.toml` at repo root for versioning and changelog management from the mono-repo root

## v1.1.0 (2026-05-08)

### Feat

- **observability**: add logs dashboard with tabbed layout - Export logs dashboard to provisioning with v2 TabsLayout - Separate Errors, Warnings and Info into individual tabs - Enable timestamps on all log panels - Standardize LogQL filter syntax to backtick style - Exclude uvicorn internal logs from Info panel
- **observability**: add Database Pool tab to metrics dashboard - Add Active Connections and Idle Connections stat panels - Add Pool Utilization % gauge with same color schema as Server tab - Add Pool Usage timeseries with used/idle series - Use only db_client_connections_usage metric (only available pool metric)
- **services**: add structured logging to actor and movie services - Log name conflicts and missing cast members at WARNING - Log create/update/delete and rating operations at INFO - Log 404 misses, list filters and cast mutations at DEBUG
- **services**: add structured logging to auth and user services - Log failed login attempts and token anomalies at WARNING - Log ownership violations (403) at WARNING with user context - Log successful login, user create/update/delete at INFO - Log 404 misses and token refresh at DEBUG
- **telemetry**: enable DEBUG log level in development environment - Set log level to DEBUG when ENVIRONMENT=development, INFO otherwise - Add logger instance to middleware module
- **config**: make OTLP_ENDPOINT optional and guard telemetry setup - OTLP_ENDPOINT is now Optional[str] = None in settings - setup_telemetry is only called when OTLP_ENDPOINT is set - pre_app task now starts postgres container and runs alembic migrations - DB_PORT defaults to 5432 in settings
- **docker**: mount hostfs and Grafana dashboard volumes in compose - Mount /:/hostfs:ro in otel-collector for host metrics access - Mount dashboard provisioning config and dashboards dir into Grafana
- **observability**: add host metrics collection and Grafana dashboards - Configure hostmetrics receiver with cpu, memory, disk, network, filesystem scrapers - Add dashboard provisioning config pointing to /var/lib/grafana/dashboards - Add metrics Grafana dashboard JSON
- **observability**: wire HTTP middleware and configure histogram view - Register Middleware in app to track all HTTP requests - Add explicit bucket boundaries for http_request_duration histogram - Remove stream handler from logging, keeping only OTel handler
- **observability**: add HTTP metrics instruments and middleware - Create meter with http_request counter and http_request_duration histogram - Implement BaseHTTPMiddleware that records method, path, status_code and elapsed time per request
- **docker**: add observability stack to Docker Compose - Add Mimir, Tempo, Loki, OTel Collector and Grafana services - Mount config files from observability/ directory and persist data via named volumes - Set OTLP_ENDPOINT on app service pointing to otel-collector:4317
- **observability**: setup OpenTelemetry SDK with traces, metrics and logs - Add telemetry.py with setup_telemetry() configuring MeterProvider, TracerProvider and LoggerProvider - Wire FastAPI and SQLAlchemy auto-instrumentation via OTLP exporters - Add OTLP_ENDPOINT and ENVIRONMENT settings; call setup_telemetry on app startup

### Fix

- **observability**: fix log queries to use warn instead of warning
- **telemetry**: update Resource initialization to use create method

## v1.0.0 (2026-04-28)

### Feat

- **routes**: protect user and movie routes with JWT authentication
- **auth**: implement JWT authentication and refactor service constants

### Fix

- **settings**: rename DB_ADRESS to DB_ADDRESS

### Docs

- add custom styles and integrate extra CSS for theme enhancement
- update version badge in README to 1.0.0
- update README and CLAUDE.md to reflect JWT authentication
- add bilingual documentation (en-US and pt-BR)
- add mkdocs i18n support and improve theme configuration

## v0.6.0 (2026-04-27)

### Feat

- **actors**: implement get and list actor routes
- **actors**: implement update and delete actor routes
- **movies**: add update movie route and tests
- **schemas**: add MovieUpdateResponseSchema
- **models**: remove rating field from MovieActor association table

### Fix

- **actors**: fix partial update overwriting unset fields and remove dead code

### Refactor

- standardize schema names, route ordering, and type consistency

## v0.5.0 (2026-04-23)

### Feat

- **movies**: implement list movies route with name and rating filters
- **movies**: add get movie detail and delete movie routes
- **movies**: implement get movie detail and delete movie
- **movies**: implement movie rating create and update endpoints

### Refactor

- **models**: rename association relationships and add viewonly many-to-many

## v0.4.0 (2026-04-21)

### Feat

- **app**: register movies and actors routers
- **movies**: add movies repository, service, and router
- **actors**: add actors repository, service, and router
- **models**: add release_date to Movie and ondelete CASCADE to intermediate tables
- **schemas**: add actors schema file
- **schemas**: add common type aliases module

### Refactor

- **schemas**: rename and expand actors and movies schemas
- **schemas**: use common type aliases in movies and users schemas

## [Actors] v0.3.0 (2026-04-21)

### Feat

- **schemas**: add actors schema file
- **actors**: add actors repository, service, and router

---

## [Movies] v0.2.x

### v0.2.2 (2026-04-23)

#### Feat

- **movies**: implement list movies route with name and rating filters
- **movies**: add get movie detail and delete movie routes
- **movies**: implement get movie detail and delete movie
- **movies**: implement movie rating create and update endpoints

#### Refactor

- **models**: rename association relationships and add viewonly many-to-many

### v0.2.1 (2026-04-21)

#### Feat

- **app**: register movies and actors routers
- **movies**: add movies repository, service, and router

### v0.2.0 (2026-04-20)

#### Feat

- **schemas**: add common type aliases module
- **schemas**: add Name type alias and movies schema file
- **models**: enforce nullable=False and unique constraints on name fields
- **models**: add release_date to Movie and ondelete CASCADE to intermediate tables

#### Refactor

- **schemas**: rename and expand actors and movies schemas
- **schemas**: use common type aliases in movies and users schemas

---

## [Users] v0.1.x

### v0.1.1 (2026-04-20)

#### Feat

- **users**: wire update_user endpoint in router
- **users**: implement update_user in repository, schema, and service layers
- **users**: add get_user and update_user endpoints; update list_users query params
- **users**: add pagination, search filter and get_user to service/repo layer

#### Fix

- **users**: update user_exist return type to include None

#### Refactor

- **users**: rename filter to search_filter and fix wildcard pattern

### v0.1.0 (2026-04-20)

#### Feat

- **app**: add FastAPI application entry point and package structure
- **core**: add database connection and application settings
- **models**: add base model, movies, and actors SQLAlchemy models
- **models**: add users and association table models
- **migrations**: add Alembic migration scripts for all tables
- **users**: add user Pydantic schemas
- **users**: add user repository layer
- **users**: add user service layer with password hashing
- **users**: add users router and register in app
