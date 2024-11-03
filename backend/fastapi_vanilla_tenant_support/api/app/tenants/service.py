import logging
from typing import Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import UUID4, ValidationError

from app.common.utils.base_classes.base_service import BaseService
from app.db.manage import init_schema
from app.db.engine import engine
from .models import Tenant
from .schemas import TenantCreate, TenantUpdate, TenantRead
from .repository import TenantRepository

log = logging.getLogger(__name__)


class TenantService(BaseService[Tenant, TenantCreate, TenantUpdate, TenantRead]):
    def __init__(self, session: AsyncSession):
        super().__init__(TenantRepository, session)
        self.session = session

    async def get_default(self) -> Optional[Tenant]:
        """Gets the default tenant"""
        default_tenant = await self.session.execute(select(Tenant).where(Tenant.default == True))
        return default_tenant.scalar_one_or_none()

    async def get_default_or_raise(self) -> Tenant:
        """Gets the default tenant or raises an exception"""
        default_tenant = await self.get_default()
        if not default_tenant:
            log.exception("Default tenant not found")
            raise ValueError("Default tenant not found")
        return default_tenant

    async def get_by_name(self, name: str) -> Optional[Tenant]:
        """Gets a tenant by name"""
        tenant = await self.session.execute(select(Tenant).where(Tenant.name == name))
        return tenant.scalar_one_or_none()

    async def get_by_name_or_raise(self, name: str) -> Tenant:
        """Gets a tenant by name or raises an exception"""
        tenant = await self.get_by_name(name)
        if not tenant:
            log.info(f"Tenant not found: {name}")
            raise ValueError("Tenant not found")
        return tenant

    async def get_by_name_or_default(self, name: str) -> Tenant:
        """Gets a tenant by name or returns the default tenant"""
        tenant = await self.get_by_name(name)
        if not tenant:
            log.info(f"Tenant not found: {name}, getting default tenant")
            tenant = await self.get_default_or_raise()
        return tenant

    async def get_by_slug(self, slug: str) -> Optional[Tenant]:
        """Gets a tenant by slug"""
        query = select(Tenant).where(Tenant.slug == slug)
        tenant = await self.session.execute(query)
        return tenant.scalar_one_or_none()

    async def get_by_slug_or_raise(self, tenant_in: TenantRead) -> Tenant:
        """Gets a tenant by slug or raises an exception"""
        tenant = await self.get_by_slug(tenant_in.slug)
        if not tenant:
            log.info(f"Tenant not found: {tenant_in.slug}")
            raise ValueError("Tenant not found")
        return tenant

    async def create(self, obj_in: TenantCreate) -> Tenant:
        """Creates a new tenant"""
        tenant = await self.repository.create(obj_in)
        tenant = await init_schema(engine=engine, tenant=tenant)
        return tenant

    async def update(self, tenant: Tenant, obj_in: TenantUpdate) -> Tenant:
        """Updates a tenant by ID"""
        for field in tenant.dict():
            if field in obj_in.model_dump():
                print("field", field)
                print("obj_in", getattr(obj_in, field))
                setattr(tenant, field, getattr(obj_in, field))
        await self.session.commit()
        await self.session.refresh(tenant)
        return tenant

    async def delete(self, tenant_id: UUID4) -> bool:
        """Deletes a tenant by ID"""
        try:
            await self.session.execute(delete(Tenant).where(Tenant.id == tenant_id))
            await self.session.commit()
            return True
        except Exception as e:
            log.exception(e)
            await self.session.rollback()
            return False

    async def add_user(self, user, tenant: Tenant, role) -> Tenant:
        """Adds a user to a tenant"""
        pass
