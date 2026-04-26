## v1.0.0 (2026-04-26)

### Feat

- **actors**: implement get and list actor routes
- **actors**: implement update and delete actor routes
- **movies**: add update movie route and tests
- **schemas**: add MovieUpdateResponseSchema
- **models**: remove rating field from MovieActor association table

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
