# FastAPI Vanilla Boilerplate

FastAPI Boilerplate code with PostgreSQL database.  
This example uses docker compose for development

## Commands

- Start in development mode
`docker compose up`

- Fastapi app will be exposed to port 8004
- Postgres DB wil lbe exposed to port 5432
- Fastapi app and postgres db are communicating via docker compose default network

## Backend

### Database
- Create a database migration revision
`docker compose exec fastapi_vanilla_web alembic revision --autogenerate -m "<migration-name>"`
- Checkout the revision under `api/migrations/versions`
- Execute the migration
`docker compose exec fastapi_vanilla_web alembic upgrade head`

### Tests
- Execute pytest tests
`docker compose exec fastapi_vanilla_web python -m pytest`