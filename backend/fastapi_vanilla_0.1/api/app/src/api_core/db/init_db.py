from app.src.users.model import User

from .database import Base, engine


async def create_tables():
    """
    Create the tables in the database with async support
    """
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
