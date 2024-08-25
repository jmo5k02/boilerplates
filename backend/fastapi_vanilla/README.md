# FastAPI Vanilla Boilerplate

FastAPI Boilerplate code with PostgreSQL database.  
This example uses docker compose for development

## Commands

- Start in development mode
`docker compose up`

## Backend

- Database migrations
`docker compose exec fastapi_vanilla_web alembic revision --autogenerate -m "<migration-name>"`