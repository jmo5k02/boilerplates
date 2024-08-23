"""
This module handles the database connection 
provides `get_db` function to get the database session.
provided the Base class for the database models.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker

from settings import global_settings

engine = create_engine(
    str(global_settings.SQLALCHEMY_DATABASE_URI),
    poolclass=QueuePool,
    pool_size=50,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Declare the base model for all Database models
class Base(DeclarativeBase):
    pass

def get_db():
    """
    Create a database session.
    Yields:
        Session: The database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()