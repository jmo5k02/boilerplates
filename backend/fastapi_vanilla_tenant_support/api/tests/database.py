import asyncio
from sqlalchemy.ext.asyncio import (
    async_scoped_session,
    async_sessionmaker,
    AsyncSession,
)

Session = async_scoped_session(
    async_sessionmaker(class_=AsyncSession, expire_on_commit=False),
    scopefunc=asyncio.current_task,
)
