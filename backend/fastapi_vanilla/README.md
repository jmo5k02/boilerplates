# FastAPI Vanilla Boilerplate

FastAPI Boilerplate code with PostgreSQL database.  
This example uses docker compose for development

## Table of Contents

- [Commands](#commands)
- [Backend](#backend)
    - [database](#database)
    - [tests](#tests)
    - [deployment](#deployment)

## Commands

- Start in development mode
`docker compose up`

- Fastapi app will be exposed to port 8004
- Postgres DB wil lbe exposed to port 5432
- Fastapi app and postgres db are communicating via docker compose default network

## Backend

### Database
#### Adding a new table
- Create a table definition by letting it inherit from Base defined in `app/src/db/database.py`
- Import that new table definition into `migrations/env.py`
- Create a database migration revision
`docker compose exec fastapi_vanilla_web alembic revision --autogenerate -m "<migration-name>"`
- Checkout the revision under `api/migrations/versions`
- Execute the migration
`docker compose exec fastapi_vanilla_web alembic upgrade head`

### Tests
- Execute pytest tests with coverage
`docker compose exec fastapi_vanilla_web python -m pytest --cov="."`

- Select specific tests
    - Run all tests that have `health` in their name
    - `docker compose exec fastapi_vanilla_web python -m pytest -k health`
    - Run all tests that have `read` in their name
    - `docker compose exec fastapi_vanilla_web python -m pytest -k read`

- Execute with html coverage report
`docker compose exec fastapi_vanilla_web python -m pytest --cov="." --cov-report html`

#### General pytest commands
##### normal run
`$ docker-compose exec fastapi_vanilla_web python -m pytest`

##### disable warnings
`$ docker-compose exec fastapi_vanilla_web python -m pytest -p no:warnings`

##### run only the last failed tests
`$ docker-compose exec fastapi_vanilla_web python -m pytest --lf`

##### run only the tests with names that match the string expression
`$ docker-compose exec fastapi_vanilla_web python -m pytest -k "summary and not test_read_summary"`

##### stop the test session after the first failure
`$ docker-compose exec fastapi_vanilla_web python -m pytest -x`

##### enter PDB after first failure then end the test session
`$ docker-compose exec fastapi_vanilla_web python -m pytest -x --pdb`

##### stop the test run after two failures
`$ docker-compose exec fastapi_vanilla_web python -m pytest --maxfail=2`

##### show local variables in tracebacks
`$ docker-compose exec fastapi_vanilla_web python -m pytest -l`

##### list the 2 slowest tests
`$ docker-compose exec fastapi_vanilla_web python -m pytest --durations=2`

### Deployment
- Build the production container
`docker build -f api/Dockerfile.prod -t <prod-image-tag> ./api`
- Run the production container
`docker run --name <prod_container_name> -e PORT=8765 -e POSTGRES_SERVER_HOST="127.0.0.1" -p 5003:8765 <prod-image-tag>`
