from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypeVar
from datetime import datetime
from pydantic import BaseModel
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory, T, SQLAASyncPersistence

from app.db.base import Base
from app.auth.models import AppUser
from app.tenants.models import Tenant

from .database import Session

fake = Faker()

SqlModelClass = TypeVar("SqlModelClass", bound=Base)
PydanticModelClass = TypeVar("PydanticModelClass", bound=BaseModel)


class BaseFactory(SQLAlchemyFactory[T]):
    """Base factory class for test data generation with common methods"""
    __is_base_factory__ = True
    __set_relationships__ = True
    __set_primary_key__ = True
    __set_foreign_keys__ = True
    __randomize_collection_length__ = True
    __min_collection_length__ = 1
    __faker__ = fake
    
    
    __async_persistence__ = SQLAASyncPersistence(Session)
    # Will be set by fixture
    __async_session__ = None


    # def __init__(self, db: AsyncSession):
    #     self.session = db

    # async def create_sql_model(self, **kwargs) -> SqlModelClass:
    #     """Create an instance of a SQL model that can be persisted into the database directly"""
    #     raise NotImplementedError

    # async def _create_and_persist_sql_model(self, model: SqlModelClass, **kwargs) -> SqlModelClass:
    #     """Create and persist an instance of a model"""
    #     instance = model(**kwargs)
    #     self.session.add(instance)
    #     await self.session.commit()
    #     await self.session.refresh(instance)
    #     return instance

    # async def create_batch_sql(self, size: int, **kwargs) -> list[SqlModelClass]:
    #     """Create a batch of instances of a model"""
    #     return [await self.create_sql_model(**kwargs) for _ in range(size)]

    # def create_pydantic_model(self, **kwargs) -> PydanticModelClass:
    #     """Create an instance of a Pydantic model that can be used to test endpoints"""
    #     raise NotImplementedError
    
    # def create_batch_pydantic(self, size: int, **kwargs) -> list[PydanticModelClass]:
    #     """Create a batch of instances of a Pydantic model"""
    #     return [self.create_pydantic_model(**kwargs) for _ in range(size)]


class UserFactory(BaseFactory):
    """Factory class for generating test User instances"""
    __model__ = AppUser




class TenantFactory(BaseFactory):
    __model__ = Tenant



    

