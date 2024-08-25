# FastAPI Vanilla Boilerplate

FastAPI Boilerplate code with PostgreSQL database.  
This example uses docker compose for development

## Commands

- Start in development mode
`docker compose up`

## Backend

- Create a database migration revision
`docker compose exec fastapi_vanilla_web alembic revision --autogenerate -m "<migration-name>"`
- Checkout the revision under `api/migrations/versions`
- Execute the migration
`docker compose exec fastapi_vanilla_web alembic upgrade head`