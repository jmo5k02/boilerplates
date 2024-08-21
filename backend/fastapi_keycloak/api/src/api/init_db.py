from .database import Base, engine
from src.users.models import User


def create_tables():
    """
    Create the tables in the database.
    """
    Base.metadata.create_all(bind=engine)
