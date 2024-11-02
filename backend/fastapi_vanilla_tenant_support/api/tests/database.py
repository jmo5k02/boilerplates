import asyncio
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import (
    async_scoped_session,
    async_sessionmaker,
    AsyncSession,
)
from app.db.engine import engine


class RoutingSession(Session):
    def get_bind(self, mapper=None, clause=None, **kwargs):
        return engine.sync_engine


Session = async_scoped_session(
    async_sessionmaker(sync_session_class=RoutingSession),
    scopefunc=asyncio.current_task,
)