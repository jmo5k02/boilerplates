from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import UUID4

from app.core.base_service import BaseService
from .models import Tenant
from .schemas import TenantCreate, TenantUpdate, TenantRead
from .repository import TenantRepository


class TenantService(BaseService[Tenant, TenantCreate, TenantUpdate, TenantRead]):
    def __init__(self, session: AsyncSession):
        super().__init__(TenantRepository, session)

    async def get_default(self) -> Optional[Tenant]:
        """Gets the default tenant"""
        pass

    async def get_default_or_raise(self) -> Tenant:
        """Gets the default tenant or raises an exception"""
        pass

    async def get_by_name(self, name: str) -> Optional[Tenant]:
        """Gets a tenant by name"""
        pass

    async def get_by_name_or_raise(self, name: str) -> Tenant:
        """Gets a tenant by name or raises an exception"""
        pass

    async def get_by_name_or_default(self, name: str) -> Tenant:
        """Gets a tenant by name or returns the default tenant"""
        pass

    async def create(self, obj_in: TenantCreate) -> Tenant:
        """Creates a new tenant"""
        pass

    async def get_or_create(self, obj_in: TenantCreate) -> Tenant:
        """Gets a tenant by name or creates a new tenant"""
        pass

    async def update(self, tenant: Tenant, obj_in: TenantUpdate) -> Tenant:
        """Updates a tenant by ID"""
        pass

    async def delete(self, tenant_id: UUID4) -> bool:
        """Deletes a tenant by ID"""
        pass

    async def add_user(self, user, tenant: Tenant, role) -> Tenant:
        """Adds a user to a tenant"""
        pass
