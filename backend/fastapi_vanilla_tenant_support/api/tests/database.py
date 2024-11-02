import asyncio
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import (
    async_scoped_session,
    async_sessionmaker,
    AsyncSession,
)


class RoutingSession(Session):
    def get_bind(self, mapper=None, clause=None, **kwargs):
        pass


Session = async_scoped_session(
    async_sessionmaker(),
    scopefunc=asyncio.current_task,
)