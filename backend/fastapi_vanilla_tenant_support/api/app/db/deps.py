from uuid import uuid1
from typing import Annotated, AsyncGenerator

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import async_sessionmaker, async_scoped_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request, Depends

from app.db.engine import async_SessionLocal, engine


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_SessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


DbSessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_tenant_slug(request: Request) -> str:
    return request.path_params.get("tenant")


TenantSlugDep = Annotated[str, Depends(get_tenant_slug)]


async def get_tenant_session(
    tenant_slug: TenantSlugDep,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Create an async sqlalchemy tenant scoped session and yield it
    """
    # TODO test if it is necessary to create a request id with context var to make sure session is soped to one request
    # request_id = str(uuid1())
    schema = f"tenant_{tenant_slug}"
    # Validate slug exists
    schema_names = inspect(engine).get_schema_names()
    if schema in schema_names:
        schema_engine = engine.execution_options(schema_translate_map={None: schema})
    else:
        raise ValueError(f"Schema {schema} does not exist")

    try:
        session = async_scoped_session(async_sessionmaker(bind=schema_engine))
        async with session() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()
    except Exception as e:
        raise e


TenantDbSessionDep = Annotated[AsyncSession, Depends(get_tenant_session)]
