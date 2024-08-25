from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import QueuePool

from app.settings import settings

engine: AsyncEngine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=settings.testing,
)

async_SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create an async sqlalchemy session and yield it
    """
    async with async_SessionLocal() as session:
        yield session