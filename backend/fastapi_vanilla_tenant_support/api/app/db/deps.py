import logging
from uuid import uuid1
from typing import Annotated, AsyncGenerator, Final, Optional
from contextvars import ContextVar

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import async_sessionmaker, async_scoped_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request, Depends

from app.db.engine import async_SessionLocal, engine
from app.auth.deps import CurrentUserDep

log = logging.getLogger(__name__)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_SessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


async def get_tenant_slug(request: Request) -> str:
    """return tenant slug from path params or default"""
    return request.path_params.get("tenant", "default")


TenantSlugDep = Annotated[str, Depends(get_tenant_slug)]


async def get_tenant_session(
    # tenant_slug: TenantSlugDep,
    request: Request,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Create an async sqlalchemy tenant scoped session and yield it
    """
    request_id = str(uuid1())
    tenant_slug = request.path_params.get("tenant", "default")
    schema = f"tenant_{tenant_slug}"
    # Validate slug exists
    async with engine.begin() as conn:
        # Use run_sync to run synchronous operations
        schema_names = await conn.run_sync(
            lambda sync_conn: sync_conn.dialect.get_schema_names(sync_conn)
        )
    if schema in schema_names:
        schema_engine = engine.execution_options(schema_translate_map={None: schema})
    else:
        raise ValueError(f"Schema {schema} does not exist")

    try:
        session = async_scoped_session(
            async_sessionmaker(bind=schema_engine), scopefunc=lambda: request_id
        )
        async with session() as session:
            log.debug("Session created")
            request.state.db = session
            try:
                yield session
                log.debug("Session committed")
                await session.commit()
            except Exception as e:
                log.debug("Session rolled back")
                await session.rollback()
                raise e
            finally:
                log.debug("Session closed")
                await session.close()
    except Exception as e:
        raise e


async def get_db(request: Request) -> AsyncSession:
    return request.state.db


DbSessionDep = Annotated[AsyncSession, Depends(get_db)]


async def common_parameters(
    current_user: CurrentUserDep,
    db_session: DbSessionDep,
):
    """This can be expanded to include more common parameters to support i.e. querying"""
    return {
        "current_user": current_user,
        "db_session": db_session,
    }


CommonParametersDep = Annotated[
    dict[CurrentUserDep, DbSessionDep], Depends(common_parameters)
]
