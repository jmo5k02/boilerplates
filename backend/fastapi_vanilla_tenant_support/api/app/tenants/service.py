from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import UUID4, ValidationError

from app.utils.base_classes.base_service import BaseService
from .models import Tenant
from .schemas import TenantCreate, TenantUpdate, TenantRead
from .repository import TenantRepository


class TenantService(BaseService[Tenant, TenantCreate, TenantUpdate, TenantRead]):
    def __init__(self, session: AsyncSession):
        super().__init__(TenantRepository, session)
        self.session = session

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

    async def get_by_slug(self, slug: str) -> Optional[Tenant]:
        """Gets a tenant by slug"""
        query = select(Tenant).where(Tenant.slug == slug)
        tenant = await self.session.execute(query)
        return tenant.scalar_one_or_none()

    async def get_by_slug_or_raise(self, tenant_in: TenantRead) -> Tenant:
        """Gets a tenant by slug or raises an exception"""
        tenant = await self.get_by_slug(tenant_in.slug)
        if not tenant:
            raise ValueError("Tenant not found")
        return tenant

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
