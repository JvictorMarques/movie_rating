## v0.3.0 (2026-04-20)

### Feat

- **schemas**: add Name type alias and movies schema file
- **models**: enforce nullable=False and unique constraints on name fields

## v0.2.0 (2026-04-20)

### Feat

- **users**: wire update_user endpoint in router
- **users**: implement update_user in repository, schema, and service layers
- **users**: add get_user and update_user endpoints; update list_users query params
- **users**: add pagination, search filter and get_user to service/repo layer
- **users**: add users router and register in app
- **users**: add user service layer with password hashing
- **users**: add user repository layer
- **users**: add user Pydantic schemas
- **migrations**: add Alembic migration scripts for all tables
- **models**: add users and association table models
- **models**: add base model, movies, and actors SQLAlchemy models
- **core**: add database connection and application settings
- **app**: add FastAPI application entry point and package structure

### Fix

- **users**: update user_exist return type to include None

### Refactor

- **users**: rename filter to search_filter and fix wildcard pattern
