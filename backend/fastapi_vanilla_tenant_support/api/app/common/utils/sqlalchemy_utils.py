"""
SQLAlchemy utilities.
Reference: https://github.com/kvesteri/sqlalchemy-utils/blob/master/sqlalchemy_utils/functions/database.py#L425
"""
from copy import copy

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_object_session
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.engine.url import make_url, URL
from sqlalchemy.exc import OperationalError, ProgrammingError

async def has_schema(engine: AsyncEngine, schema_name: str) -> bool:
    async with engine.connect() as conn:
        # For PostgreSQL
        query = sa.text(
            "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = :schema)"
        )
        result = await conn.scalar(query, {"schema": schema_name})
        return bool(result)


def get_bind(obj):
    """
    Return the bind for given SQLAlchemy Engine / Connection / declarative
    model object.

    :param obj: SQLAlchemy Engine / Connection / declarative model object

    ::

        from sqlalchemy_utils import get_bind


        get_bind(session)  # Connection object

        get_bind(user)

    """
    if hasattr(obj, 'bind'):
        conn = obj.bind
    else:
        try:
            conn = async_object_session(obj).bind
        except UnmappedInstanceError:
            conn = obj

    if not hasattr(conn, 'execute'):
        raise TypeError(
            'This method accepts only Session, Engine, Connection and '
            'declarative model objects.'
        )
    return conn


def quote(mixed, ident):
    """
    Conditionally quote an identifier.
    ::


        from sqlalchemy_utils import quote


        engine = create_engine('sqlite:///:memory:')

        quote(engine, 'order')
        # '"order"'

        quote(engine, 'some_other_identifier')
        # 'some_other_identifier'


    :param mixed: SQLAlchemy Session / Connection / Engine / Dialect object.
    :param ident: identifier to conditionally quote
    """
    if isinstance(mixed, sa.Dialect):
        dialect = mixed
    else:
        dialect = get_bind(mixed).dialect
    return dialect.preparer(dialect).quote(ident)


def _set_url_database(url: URL, database):
    """Set the database of an engine URL.

    :param url: A SQLAlchemy engine URL.
    :param database: New database to set.

    """
    if hasattr(url, '_replace'):
        # Cannot use URL.set() as database may need to be set to None.
        ret = url._replace(database=database)
    else:  # SQLAlchemy <1.4
        url = copy(url)
        url.database = database
        ret = url
    assert ret.database == database, ret
    return ret


async def _get_scalar_result(engine: AsyncEngine, sql: str):
    async with engine.connect() as conn:
        return await conn.scalar(sql)


async def database_exists(url: str) -> bool:
    url: URL = make_url(url)
    database = url.database
    dialect_name = url.get_dialect().name
    engine = None

    try:
        if dialect_name == 'postgresql':
            text = "SELECT 1 FROM pg_database WHERE datname = '%s'" % database
            for db in (database, 'postgres', 'template1', None):
                url = _set_url_database(url, database=db)
                print("Checking database existence for %s" % str(url))
                engine = create_async_engine(url)
                try:
                    return bool(await _get_scalar_result(engine, sa.text(text)))
                except (ProgrammingError, OperationalError):
                    pass
            return False
        else:
            raise NotImplementedError("Database existence check is not supported for %s" % dialect_name)
    finally:
        if engine is not None:
            await engine.dispose()

async def create_database(url: str, encoding='utf-8'):
    url: URL = make_url(url)
    database = url.database
    dialect_name = url.get_dialect().name
    
    if dialect_name == 'postgresql':
        url = _set_url_database(url, database="postgres")
    
    engine = create_async_engine(url)

    if dialect_name == 'postgresql':
        template = 'template1'

        async with engine.begin() as conn:
            text = "CREATE DATABASE {} ENCODING '{}' TEMPLATE {}".format(
                quote(conn, database),
                encoding,
                quote(conn, template)
            )
            await conn.execute(sa.text(text))
    else:
        raise NotImplementedError("Database creation is not supported for %s" % dialect_name)
    
    await engine.dispose()