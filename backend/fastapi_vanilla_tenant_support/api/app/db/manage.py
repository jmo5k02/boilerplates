import logging

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession
from sqlalchemy.schema import CreateSchema
from sqlalchemy import select, Table

from app.settings import settings
from app.db.base import Base
from app.db.engine import engine
from app.tenants.models import Tenant
from app.auth.models import AppUser, AppUserTenant
from app.common.utils.sqlalchemy_utils import create_database, database_exists, has_schema

log = logging.getLogger(__name__)

TENANT_SCHEMA_PREFIX = "tenant"

def get_core_tables() -> list[Table]:
    """Fetches tables that belong to the core schema"""
    core_tables = []
    for _, table in Base.metadata.tables.items():
        log.debug("Table: %s", str(table))
        log.debug("Schema: %s", str(table.schema))
        if table.schema == "core":
            core_tables.append(table)
    return core_tables


def get_tenant_tables() -> list[Table]:
    """Fetches tables that belong to their own tenant tables"""
    tenant_tables = []
    for _, table in Base.metadata.tables.items():
        if not table.schema:
            tenant_tables.append(table)
    return tenant_tables


async def init_database():
    """Initialize the database"""
    if not await database_exists(str(settings.SQLALCHEMY_DATABASE_URI)):
        print("Creating database")
        await create_database(str(settings.SQLALCHEMY_DATABASE_URI))

    schema_name = "core"
    if not await has_schema(engine, schema_name):
        print("Creating schema")
        async with engine.connect() as conn:
            await conn.execute(CreateSchema(schema_name))
            await conn.commit()

    tables = get_core_tables()
    print("Creating core tables", list(map(lambda x: x.name,tables)))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=tables)
    

    core_session = async_sessionmaker(bind=engine, class_=AsyncSession)
    async with core_session() as core_session:
        default_tenant_query = select(Tenant).where(Tenant.name == "default")
        default_tenant = await core_session.execute(default_tenant_query)
        default_tenant = default_tenant.scalar_one_or_none()

        if not default_tenant:
            print("Creating default tenant")
            default_tenant = Tenant(
                name="default", 
                slug="default",
                default=True,
                description="Default app tenant"
            )

            core_session.add(default_tenant)
            await core_session.commit()
            await core_session.refresh(default_tenant)
            

        await init_schema(engine=engine, tenant=default_tenant)

        
async def init_schema(*, engine: AsyncEngine, tenant: Tenant) -> Tenant:
    """Initializes a new schema."""
    print("Initializing schema")
    schema_name = f"{TENANT_SCHEMA_PREFIX}_{tenant.slug}"

    async with engine.begin() as conn:

        if not await has_schema(engine, schema_name):
            print("Creating default tenant schema")
            await conn.execute(CreateSchema(schema_name))
    
    tables = get_tenant_tables()

    schema_engine = engine.execution_options(
        schema_translate_map={None: schema_name}
    )

    print("Creating default tenant tables", list(map(lambda x: x.name,tables)))
    async with schema_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=tables)
        
        for t in tables:
            t.schema = schema_name

    session = async_sessionmaker(bind=schema_engine, class_=AsyncSession)

    async with session() as session:
        tenant = await session.merge(tenant)
        session.add(tenant)
        await session.commit()
        return tenant