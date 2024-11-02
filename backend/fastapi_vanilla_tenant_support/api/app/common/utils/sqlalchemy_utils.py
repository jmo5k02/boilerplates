"""
SQLAlchemy utilities.
Reference: https://github.com/kvesteri/sqlalchemy-utils/blob/master/sqlalchemy_utils/functions/database.py#L425
"""

from copy import copy

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    async_object_session,
)
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
    if hasattr(obj, "bind"):
        conn = obj.bind
    else:
        try:
            conn = async_object_session(obj).bind
        except UnmappedInstanceError:
            conn = obj

    if not hasattr(conn, "execute"):
        raise TypeError(
            "This method accepts only Session, Engine, Connection and "
            "declarative model objects."
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
    if hasattr(url, "_replace"):
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
        if dialect_name == "postgresql":
            text = "SELECT 1 FROM pg_database WHERE datname = '%s'" % database
            for db in (database, "postgres", "template1", None):
                url = _set_url_database(url, database=db)
                print("Checking database existence for %s" % str(url))
                engine = create_async_engine(url, isolation_level="AUTOCOMMIT")
                try:
                    return bool(await _get_scalar_result(engine, sa.text(text)))
                except (ProgrammingError, OperationalError):
                    pass
            return False
        else:
            raise NotImplementedError(
                "Database existence check is currently only supported for postgresql dialect and not %s"
                % dialect_name
            )
    except Exception as e:
        print("Error checking database existence: %s" % str(e))
        return False
    finally:
        if engine is not None:
            await engine.dispose()


async def create_database(url: str, encoding="utf-8"):
    url: URL = make_url(url)
    database = url.database
    dialect_name = url.get_dialect().name

    if dialect_name == "postgresql":
        url = _set_url_database(url, database="postgres")

    engine = create_async_engine(url, isolation_level="AUTOCOMMIT")

    if dialect_name == "postgresql":
        template = "template1"

        async with engine.connect() as conn:
            text = "CREATE DATABASE {} ENCODING '{}' TEMPLATE {}".format(
                quote(conn, database), encoding, quote(conn, template)
            )
            await conn.execute(sa.text(text))
    else:
        raise NotImplementedError(
            "Database creation is currently only supported for postgresql dialect and not %s"
            % dialect_name
        )

    await engine.dispose()


async def drop_database(url: str):
    url: URL = make_url(url)
    database = url.database
    dialect_name = url.get_dialect().name
    dialect_dirver = url.get_dialect().driver

    if dialect_name == "postgresql":
        url = _set_url_database(url, database="postgres")
    else:
        raise NotImplementedError(
            "Database dropping is curently only supported for postgresql dialect and not %s"
            % dialect_name
        )


    if dialect_name == "postgresql" and dialect_dirver in {
        "asyncpg",
        "pg8000",
        "psycopg",
        "psycopg2",
    }:
        engine = create_async_engine(url, isolation_level="AUTOCOMMIT")
        async with engine.connect() as conn:
            # Disconnect all users from the database we are dropping.
            version = conn.dialect.server_version_info
            pid_column = (
                'pid' if (version >= (9, 2)) else 'procpid'
            )
            text = f"""
            SELECT pg_terminate_backend(pg_stat_activity.{pid_column})
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{database}'
            AND {pid_column} <> pg_backend_pid();
            """
            await conn.execute(sa.text(text))

            # Drop the database.
            text = f"DROP DATABASE {quote(conn, database)}"
            await conn.execute(sa.text(text))
    else:
        raise NotImplementedError(
            "Database dropping is not supported for dialect %s" % dialect_name
        )

    await engine.dispose()
