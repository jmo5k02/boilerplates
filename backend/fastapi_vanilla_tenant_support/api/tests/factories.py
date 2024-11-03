from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypeVar
from datetime import datetime
from pydantic import BaseModel

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory, T, SQLAASyncPersistence, SQLASyncPersistence
from polyfactory import Use

from app.db.base import Base
from app.common.utils.enums import UserRoles
from app.auth.models import AppUser, AppUserTenant
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
    __sync_persistence__= SQLASyncPersistence(Session)
    # Will be set by fixture
    __async_session__ = None


    def create_pydantic_model(self, **kwargs) -> PydanticModelClass:
        """Create an instance of a Pydantic model that can be used to test endpoints"""
        raise NotImplementedError
    
    def create_batch_pydantic(self, size: int, **kwargs) -> list[PydanticModelClass]:
        """Create a batch of instances of a Pydantic model"""
        return [self.create_pydantic_model(**kwargs) for _ in range(size)]



class UserFactory(BaseFactory):
    """Factory class for generating test User instances"""
    __model__ = AppUser


    def gen_password() -> str:
        return bytes(fake.password(), "utf-8")

    email = Use(BaseFactory.__faker__.email)
    password = Use(gen_password)
    salt = Use(gen_password)



    

class TenantFactory(BaseFactory):
    __model__ = Tenant

    name = Use(BaseFactory.__faker__.company)
    slug = Use(BaseFactory.__faker__.slug)
    description = Use(BaseFactory.__faker__.sentence)
    

class UserTenantFactory(BaseFactory):
    __model__ = AppUserTenant

    @classmethod
    async def create_user_with_tenant(cls) -> tuple[AppUser, Tenant]:
        user = await UserFactory.create_async()
        tenant = await TenantFactory.create_async()
        
        user_tenant = await cls.create_async(
            user_id=user.id,
            tenant_id=tenant.id,
            role=UserRoles.member
        )
        
        return user, tenant

    

